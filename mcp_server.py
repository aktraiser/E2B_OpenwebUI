"""
MCP Server for VPS - Simple Version
Exposes E2B + CrewAI tools to OpenWebUI via MCP protocol

Simple approach using E2B Code Interpreter + CrewAI directly
"""
import asyncio
import json
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from e2b_code_interpreter import Sandbox
from crewai.tools import tool
from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("e2b-crewai-mcp")

@tool("Python Interpreter")
def execute_python(code: str) -> str:
    """
    Execute Python code and return the results.
    """
    try:
        with Sandbox.create() as sandbox:
            execution = sandbox.run_code(code)
            if execution.error:
                return f"Error: {execution.error}"
            return execution.text if execution.text else "Code executed successfully"
    except Exception as e:
        return f"Execution error: {str(e)}"


def create_crew(task_description: str):
    """
    Create a CrewAI crew with E2B tools
    """
    # Define the agent
    python_executor = Agent(
        role='Python Executor and Researcher',
        goal='Execute Python code and solve complex tasks',
        backstory='You are an expert Python programmer and researcher capable of executing code and solving problems.',
        tools=[execute_python],
        llm=LLM(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        verbose=True
    )

    # Define the task
    execute_task = Task(
        description=task_description,
        agent=python_executor,
        expected_output="Complete solution with execution results"
    )

    # Create the crew
    crew = Crew(
        agents=[python_executor],
        tasks=[execute_task],
        verbose=True
    )

    return crew


async def execute_crewai_task(task: str, sandbox_id: str = None) -> dict:
    """
    Execute a task using CrewAI with E2B Code Interpreter
    
    Args:
        task: Task description for CrewAI
        sandbox_id: Optional (not used in simple version)
    
    Returns:
        Execution result
    """
    try:
        logger.info(f"Executing CrewAI task: {task[:100]}...")
        
        # Create crew
        crew = create_crew(task)
        
        # Execute task
        result = crew.kickoff()
        
        logger.info("Task completed successfully")
        return {
            "success": True,
            "result": str(result)
        }
        
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def list_active_sandboxes() -> dict:
    """List active sandboxes (simple version - no caching)"""
    return {
        "active_sandboxes": [],
        "count": 0,
        "note": "Simple version uses ephemeral sandboxes"
    }


async def cleanup_sandbox(sandbox_id: str) -> dict:
    """Cleanup sandbox (simple version - auto cleanup)"""
    return {
        "success": True, 
        "message": "Simple version uses auto-cleanup sandboxes"
    }


# Create MCP server
app = Server("e2b-crewai-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="execute_crewai_task",
            description="""Execute a task using CrewAI agent with E2B Code Interpreter.

The CrewAI agent can:
- Execute Python code in secure E2B sandboxes
- Perform calculations and data analysis
- Solve complex programming problems

Examples:
- "Calculate 2 + 2 using Python"
- "Analyze CSV data and create a summary"
- "Calculate the fibonacci sequence up to n=20"
- "Count how many r's are in the word 'strawberry'"

The agent will use Python code execution to complete tasks.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description for the CrewAI agent"
                    },
                    "sandbox_id": {
                        "type": "string",
                        "description": "Optional: Not used in simple version"
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="list_sandboxes",
            description="List active E2B sandboxes (simple version uses ephemeral sandboxes)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cleanup_sandbox",
            description="Cleanup sandbox (simple version uses auto-cleanup)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sandbox_id": {
                        "type": "string",
                        "description": "Sandbox ID (not used in simple version)"
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
        sandbox_id = arguments.get("sandbox_id", "")
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
    logger.info("Starting E2B CrewAI MCP Server (Simple Version)...")

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