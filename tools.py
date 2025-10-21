"""
CrewAI tools for E2B code execution on VPS.
Optimized for cost control and resource management.
"""
import logging
import asyncio
import time
from typing import List
from crewai.tools import tool
from e2b_code_interpreter import ExecutionError, OutputMessage, Result
from sandbox_pool import get_sandbox_pool
from config import VPSConfig

logger = logging.getLogger(__name__)


@tool("Python Code Interpreter (E2B)")
async def execute_python(code: str) -> str:
    """
    Execute Python code in a secure E2B cloud sandbox.

    IMPORTANT:
    - Each execution creates a cloud sandbox (costs money)
    - Use sparingly and only when necessary
    - Think before executing - validate your code logic first
    - Maximum execution time: 30 seconds
    - Maximum code length: 10,000 characters

    Args:
        code (str): Python code to execute

    Returns:
        str: Execution results including stdout, stderr, errors, and metrics

    Examples:
        >>> execute_python("print('Hello, World!')")
        "Output:\\nHello, World!\\n\\n[Execution time: 1.23s]"

        >>> execute_python("x = 5 + 3\\nprint(x)")
        "Output:\\n8\\n\\n[Execution time: 1.15s]"
    """
    pool = get_sandbox_pool()

    # ==================== VALIDATION ====================
    validation_error = _validate_code(code)
    if validation_error:
        logger.warning(f"Code validation failed: {validation_error}")
        return f"Validation Error: {validation_error}"

    # ==================== EXECUTION WITH RETRY ====================
    for attempt in range(VPSConfig.MAX_RETRIES):
        try:
            logger.info(f"Executing code (attempt {attempt + 1}/{VPSConfig.MAX_RETRIES})")
            # Execute directly in async context
            result = await _execute_with_pool(pool, code)
            return result

        except RuntimeError as e:
            error_msg = str(e)

            # Check if it's a rate limit error
            if "Cannot create sandbox" in error_msg:
                logger.warning(f"Rate limit hit: {error_msg}")
                metrics = pool.get_metrics()
                return (
                    f"⚠️ Service Temporarily Unavailable\n\n"
                    f"Reason: {error_msg}\n\n"
                    f"Current Usage:\n"
                    f"- Active sandboxes: {metrics['active_sandboxes']}/{VPSConfig.MAX_CONCURRENT_SANDBOXES}\n"
                    f"- Hourly usage: {metrics['hourly_count']}/{VPSConfig.MAX_SANDBOXES_PER_HOUR}\n"
                    f"- Total executions: {metrics['total_executions']}\n\n"
                    f"Please wait a few minutes before trying again."
                )

            # Retry for transient errors
            if attempt < VPSConfig.MAX_RETRIES - 1:
                logger.warning(
                    f"Attempt {attempt + 1} failed: {error_msg}. "
                    f"Retrying in {VPSConfig.RETRY_DELAY}s..."
                )
                time.sleep(VPSConfig.RETRY_DELAY)
            else:
                logger.error(f"All {VPSConfig.MAX_RETRIES} attempts failed")
                return (
                    f"❌ Execution Failed\n\n"
                    f"Error: {error_msg}\n"
                    f"Attempts: {VPSConfig.MAX_RETRIES}\n\n"
                    f"This may be a temporary issue. Please try again later."
                )

        except Exception as e:
            logger.exception("Unexpected error during code execution")
            return (
                f"❌ Unexpected Error\n\n"
                f"Error: {str(e)}\n"
                f"Type: {type(e).__name__}\n\n"
                f"Please report this error if it persists."
            )

    return f"❌ Maximum retries ({VPSConfig.MAX_RETRIES}) exceeded"


def _validate_code(code: str) -> str | None:
    """
    Validate code before execution.

    Returns:
        Error message if invalid, None if valid
    """
    if not code or not code.strip():
        return "Empty code provided"

    if len(code) > VPSConfig.MAX_CODE_LENGTH:
        return (
            f"Code too long ({len(code)} chars). "
            f"Maximum: {VPSConfig.MAX_CODE_LENGTH} chars"
        )

    # Check for obviously dangerous patterns
    dangerous_patterns = [
        "import os",
        "subprocess",
        "eval(",
        "exec(",
        "__import__"
    ]

    for pattern in dangerous_patterns:
        if pattern in code.lower():
            logger.warning(f"Potentially dangerous pattern detected: {pattern}")
            # Note: E2B sandboxes are isolated, so this is just a warning
            # We don't block it but log it for monitoring

    return None


async def _execute_with_pool(pool, code: str) -> str:
    """
    Execute code using the sandbox pool.

    Args:
        pool: SandboxPool instance
        code: Python code to execute

    Returns:
        Formatted execution results
    """
    results = {
        "stdout": [],
        "stderr": [],
        "errors": [],
        "result": None
    }

    start_time = time.time()

    # ==================== SANDBOX ACQUISITION ====================
    async with pool.acquire_sandbox() as sandbox:

        # ==================== CALLBACKS ====================
        def on_stdout(msg: OutputMessage):
            """Handle stdout messages"""
            results["stdout"].append(msg.line)
            logger.debug(f"stdout: {msg.line}")

        def on_stderr(msg: OutputMessage):
            """Handle stderr messages"""
            results["stderr"].append(msg.line)
            logger.debug(f"stderr: {msg.line}")

        def on_error(error: ExecutionError):
            """Handle execution errors"""
            results["errors"].append({
                "name": error.name,
                "value": error.value,
                "traceback": error.traceback[:VPSConfig.MAX_OUTPUT_LENGTH]
            })
            logger.warning(f"Execution error: {error.name} - {error.value}")

        def on_result(result: Result):
            """Handle execution result"""
            results["result"] = result
            logger.debug(f"Result: {result}")

        # ==================== CODE EXECUTION ====================
        try:
            execution = await asyncio.wait_for(
                asyncio.to_thread(
                    sandbox.run_code,
                    code=code,
                    on_stdout=on_stdout,
                    on_stderr=on_stderr,
                    on_error=on_error,
                    on_result=on_result,
                    timeout=VPSConfig.CODE_EXECUTION_TIMEOUT
                ),
                timeout=VPSConfig.REQUEST_TIMEOUT
            )

            execution_time = time.time() - start_time

            # Record metrics
            pool.metrics.record_execution(execution_time)
            pool.metrics.save_to_file()

            # Format and return results
            return _format_execution_results(results, execution_time, execution)

        except asyncio.TimeoutError:
            logger.error(f"Execution timeout after {VPSConfig.REQUEST_TIMEOUT}s")
            pool.metrics.record_timeout()
            pool.metrics.save_to_file()
            return (
                f"⏱️ Execution Timeout\n\n"
                f"Code execution exceeded {VPSConfig.REQUEST_TIMEOUT}s limit.\n"
                f"Consider optimizing your code or breaking it into smaller parts."
            )

        except Exception as e:
            logger.exception("Error during code execution")
            pool.metrics.record_failure()
            pool.metrics.save_to_file()
            raise


def _format_execution_results(
    results: dict,
    execution_time: float,
    execution
) -> str:
    """
    Format execution results into a readable string.

    Args:
        results: Dictionary with stdout, stderr, errors, result
        execution_time: Time taken for execution
        execution: Execution object from E2B

    Returns:
        Formatted string
    """
    output_parts = []

    # ==================== STDOUT ====================
    if results["stdout"]:
        stdout_lines = results["stdout"][:50]  # Limit lines
        output_parts.append(
            f"📤 Output:\n{chr(10).join(stdout_lines)}"
        )
        if len(results["stdout"]) > 50:
            output_parts.append(f"... ({len(results['stdout']) - 50} more lines)")

    # ==================== STDERR ====================
    if results["stderr"]:
        stderr_lines = results["stderr"][:20]  # Limit lines
        output_parts.append(
            f"⚠️ Warnings/Stderr:\n{chr(10).join(stderr_lines)}"
        )
        if len(results["stderr"]) > 20:
            output_parts.append(f"... ({len(results['stderr']) - 20} more lines)")

    # ==================== ERRORS ====================
    if results["errors"]:
        error_messages = []
        for error in results["errors"]:
            error_messages.append(
                f"{error['name']}: {error['value']}\n"
                f"Traceback: {error['traceback'][:500]}"
            )
        output_parts.append(
            f"❌ Execution Errors:\n{chr(10).join(error_messages)}"
        )

    # ==================== RESULT ====================
    if results["result"]:
        output_parts.append(f"✅ Result: {results['result']}")

    # ==================== LOGS ====================
    if hasattr(execution, 'logs') and execution.logs:
        logs_str = str(execution.logs)[:500]
        output_parts.append(f"📋 Logs:\n{logs_str}")

    # ==================== METRICS ====================
    output_parts.append(
        f"\n⏱️ Execution time: {execution_time:.2f}s"
    )

    # ==================== FINAL OUTPUT ====================
    if output_parts:
        return "\n\n".join(output_parts)
    else:
        return f"✅ Code executed successfully (no output)\n\n⏱️ Execution time: {execution_time:.2f}s"
