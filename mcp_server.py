"""
MCP Server for VPS
Exposes E2B + CrewAI tools to OpenWebUI via MCP protocol

This server runs on the VPS and creates E2B sandboxes with CrewAI on demand.
"""
import asyncio
import json
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from e2b import Sandbox
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("e2b-crewai-mcp")

# Global sandbox cache to reuse sandboxes
_sandbox_cache = {}
_sandbox_lock = asyncio.Lock()

async def get_or_create_sandbox(sandbox_id: str = None) -> Sandbox:
    """
    Get existing sandbox or create new one with MCP + CrewAI

    Args:
        sandbox_id: Optional sandbox ID to reuse

    Returns:
        Sandbox instance
    """
    async with _sandbox_lock:
        # Try to reuse existing sandbox
        if sandbox_id and sandbox_id in _sandbox_cache:
            try:
                sbx = _sandbox_cache[sandbox_id]
                # Test if still alive
                sbx.commands.run("echo test", timeout=5000)
                logger.info(f"Reusing existing sandbox: {sandbox_id}")
                return sbx
            except:
                logger.warning(f"Sandbox {sandbox_id} not reachable, creating new one")
                del _sandbox_cache[sandbox_id]

        # Create new sandbox
        logger.info("Creating new E2B sandbox with MCP Gateway...")

        sbx = Sandbox.beta_create(
            template="mcp-gateway",
            mcp={
                "browserbase": {
                    "apiKey": os.getenv("BROWSERBASE_API_KEY", ""),
                    "geminiApiKey": os.getenv("GEMINI_API_KEY", ""),
                    "projectId": os.getenv("BROWSERBASE_PROJECT_ID", ""),
                },
                "exa": {
                    "apiKey": os.getenv("EXA_API_KEY", ""),
                },
                "duckduckgo": {},  # No API key needed
                "arxiv": {"storagePath": "/"},
            },
            timeout=600000  # 10 minutes
        )

        logger.info(f"Sandbox created: {sbx.id}")

        # Upload CrewAI agent code
        logger.info("Setting up CrewAI in sandbox...")
        with open("crewai_agent.py", "r") as f:
            agent_code = f.read()

        sbx.files.write("/root/crewai_agent.py", agent_code)

        # Create requirements
        requirements = """crewai>=0.28.0
e2b-code-interpreter>=0.0.10
requests>=2.31.0
python-dotenv>=1.0.0
"""
        sbx.files.write("/root/requirements.txt", requirements)

        # Set environment variables
        env_vars = f"""export OPENAI_API_KEY="{os.getenv('OPENAI_API_KEY')}"
export E2B_API_KEY="{os.getenv('E2B_API_KEY')}"
"""
        sbx.files.write("/root/.env_setup", env_vars)

        # Install dependencies
        logger.info("Installing dependencies...")
        result = sbx.commands.run(
            "bash -c 'source /root/.env_setup && pip install -q -r /root/requirements.txt'",
            timeout=180000  # 3 minutes
        )

        if result.exit_code != 0:
            logger.error(f"Failed to install dependencies: {result.stderr}")
            raise Exception(f"Dependency installation failed: {result.stderr}")

        # Keep alive for 30 minutes
        sbx.keep_alive(1800)

        # Cache the sandbox
        _sandbox_cache[sbx.id] = sbx

        logger.info(f"Sandbox ready: {sbx.id}")
        return sbx


async def execute_crewai_task(task: str, sandbox_id: str = None) -> dict:
    """
    Execute a task using CrewAI in E2B sandbox

    Args:
        task: Task description for CrewAI
        sandbox_id: Optional sandbox ID to reuse

    Returns:
        Execution result
    """
    try:
        # Get or create sandbox
        sbx = await get_or_create_sandbox(sandbox_id)

        # Create a temporary Python script to run the task
        task_script = f'''
from crewai_agent import create_crew
import json

task = """{task}"""

try:
    crew = create_crew(task)
    result = crew.kickoff()
    output = {{
        "success": True,
        "result": str(result),
        "sandbox_id": "{sbx.id}"
    }}
except Exception as e:
    output = {{
        "success": False,
        "error": str(e),
        "sandbox_id": "{sbx.id}"
    }}

print(json.dumps(output))
'''

        sbx.files.write("/root/task_runner.py", task_script)

        # Execute the task
        logger.info(f"Executing CrewAI task in sandbox {sbx.id}...")
        result = sbx.commands.run(
            "bash -c 'source /root/.env_setup && cd /root && python task_runner.py'",
            timeout=300000  # 5 minutes for task execution
        )

        if result.exit_code != 0:
            logger.error(f"Task execution failed: {result.stderr}")
            return {
                "success": False,
                "error": f"Execution failed: {result.stderr}",
                "sandbox_id": sbx.id
            }

        # Parse the JSON output
        try:
            output = json.loads(result.stdout.strip())
            logger.info(f"Task completed successfully in sandbox {sbx.id}")
            return output
        except json.JSONDecodeError:
            logger.error(f"Failed to parse output: {result.stdout}")
            return {
                "success": False,
                "error": "Failed to parse task output",
                "raw_output": result.stdout,
                "sandbox_id": sbx.id
            }

    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def list_active_sandboxes() -> dict:
    """List all active sandboxes in cache"""
    return {
        "active_sandboxes": list(_sandbox_cache.keys()),
        "count": len(_sandbox_cache)
    }


async def cleanup_sandbox(sandbox_id: str) -> dict:
    """
    Cleanup a specific sandbox

    Args:
        sandbox_id: Sandbox ID to cleanup

    Returns:
        Cleanup result
    """
    async with _sandbox_lock:
        if sandbox_id in _sandbox_cache:
            try:
                sbx = _sandbox_cache[sandbox_id]
                # E2B sandboxes auto-cleanup, just remove from cache
                del _sandbox_cache[sandbox_id]
                logger.info(f"Removed sandbox {sandbox_id} from cache")
                return {"success": True, "message": f"Sandbox {sandbox_id} removed from cache"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Sandbox {sandbox_id} not found in cache"}


# Create MCP server
app = Server("e2b-crewai-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="execute_crewai_task",
            description="""Execute a task using CrewAI agent running in E2B sandbox with MCP tools.

The CrewAI agent has access to:
- Python code execution (via E2B Code Interpreter)
- Web search (via Browserbase MCP)
- Research papers (via ArXiv MCP)
- Web search (via DuckDuckGo MCP)
- Academic search (via Exa MCP)

Examples:
- "Search for the latest AI research on transformers and summarize the findings"
- "Analyze the website https://example.com and extract key information"
- "Calculate the fibonacci sequence up to n=20 using Python"
- "Research market trends for electric vehicles in 2024"

The agent will intelligently use the appropriate tools to complete the task.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description for the CrewAI agent"
                    },
                    "sandbox_id": {
                        "type": "string",
                        "description": "Optional: Sandbox ID to reuse (improves performance)"
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="list_sandboxes",
            description="List all active E2B sandboxes currently cached for reuse",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cleanup_sandbox",
            description="Remove a sandbox from cache (it will be auto-cleaned by E2B)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sandbox_id": {
                        "type": "string",
                        "description": "Sandbox ID to cleanup"
                    }
                },
                "required": ["sandbox_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if name == "execute_crewai_task":
        task = arguments.get("task")
        sandbox_id = arguments.get("sandbox_id")

        if not task:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "Task parameter is required"})
            )]

        result = await execute_crewai_task(task, sandbox_id)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "list_sandboxes":
        result = await list_active_sandboxes()
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "cleanup_sandbox":
        sandbox_id = arguments.get("sandbox_id")

        if not sandbox_id:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "sandbox_id parameter is required"})
            )]

        result = await cleanup_sandbox(sandbox_id)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]


async def main():
    """Run the MCP server"""
    logger.info("Starting E2B CrewAI MCP Server...")

    # Check required environment variables
    required_vars = ["E2B_API_KEY", "OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        raise Exception(f"Missing environment variables: {', '.join(missing)}")

    logger.info("Environment variables OK")
    logger.info("MCP Server ready to accept connections")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
