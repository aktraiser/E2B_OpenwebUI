"""
CrewAI tools using E2B MCP client - Synchronous wrappers
"""
import asyncio
import json
from typing import Optional
from crewai.tools import tool
from mcp_client import MCPClient

# Global MCP client instance
_mcp_client: Optional[MCPClient] = None
_loop: Optional[asyncio.AbstractEventLoop] = None


def get_or_create_loop():
    """Get or create event loop for async operations"""
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


def run_async(coro):
    """Run async coroutine in a safe way"""
    loop = get_or_create_loop()
    return loop.run_until_complete(coro)


async def get_mcp_client():
    """Get or create MCP client"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
        await _mcp_client.create_sandbox()
    return _mcp_client


@tool("Execute Python Code")
def execute_python(code: str) -> str:
    """Execute Python code in E2B sandbox via MCP

    Args:
        code: Python code to execute

    Returns:
        Execution output with results or errors

    Example:
        >>> execute_python("print(5 + 3)")
        "✅ Code executed successfully:\\n\\n8"
    """
    async def _run():
        try:
            client = await get_mcp_client()
            result = await client.execute_code(code)
            if result:
                return f"✅ Code executed successfully:\n\n{result}"
            else:
                return "✅ Code executed (no output)"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    return run_async(_run())


@tool("Search DuckDuckGo")
def search_duckduckgo(query: str) -> str:
    """Search the web using DuckDuckGo via MCP

    Args:
        query: Search query string

    Returns:
        Search results in JSON format
    """
    async def _run():
        try:
            client = await get_mcp_client()
            result = await client.call_tool("duckduckgo_search", {"query": query})
            return f"✅ Search results:\n\n{json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Search error: {str(e)}"

    return run_async(_run())


@tool("Search ArXiv")
def search_arxiv(query: str) -> str:
    """Search ArXiv scientific papers via MCP

    Args:
        query: Research topic or keywords

    Returns:
        ArXiv papers in JSON format
    """
    async def _run():
        try:
            client = await get_mcp_client()
            result = await client.call_tool("arxiv_search", {"query": query})
            return f"✅ ArXiv results:\n\n{json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ ArXiv error: {str(e)}"

    return run_async(_run())


@tool("List MCP Tools")
def list_mcp_tools() -> str:
    """List all available MCP tools in the E2B sandbox

    Returns:
        List of tools with descriptions in JSON format
    """
    async def _run():
        try:
            client = await get_mcp_client()
            tools = await client.list_tools()
            return f"✅ Available MCP tools:\n\n{json.dumps(tools, indent=2)}"
        except Exception as e:
            return f"❌ Error listing tools: {str(e)}"

    return run_async(_run())
