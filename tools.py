"""
CrewAI tools using E2B MCP client
"""
import asyncio
import json
from crewai.tools import tool
from mcp_client import MCPClient

# Global MCP client instance
_mcp_client = None

async def get_mcp_client():
    """Get or create MCP client"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
        await _mcp_client.create_sandbox()
    return _mcp_client


@tool("Execute Python Code")
def execute_python(code: str) -> str:
    """Execute Python code in E2B sandbox"""
    async def run():
        try:
            client = await get_mcp_client()
            result = await client.execute_code(code)
            return f"Code executed:\n{result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    return asyncio.run(run())


@tool("Search DuckDuckGo")
def search_duckduckgo(query: str) -> str:
    """Search DuckDuckGo via MCP"""
    async def run():
        try:
            client = await get_mcp_client()
            result = await client.call_tool("duckduckgo_search", {"query": query})
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
    
    return asyncio.run(run())


@tool("Search ArXiv")
def search_arxiv(query: str) -> str:
    """Search ArXiv papers via MCP"""
    async def run():
        try:
            client = await get_mcp_client()
            result = await client.call_tool("arxiv_search", {"query": query})
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
    
    return asyncio.run(run())


@tool("List MCP Tools")
def list_mcp_tools() -> str:
    """List available MCP tools"""
    async def run():
        try:
            client = await get_mcp_client()
            tools = await client.list_tools()
            return json.dumps(tools, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
    
    return asyncio.run(run())