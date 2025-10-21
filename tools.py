"""
CrewAI tools pour utiliser MCP Gateway dans le même sandbox E2B
IMPORTANT: Ce code tourne DANS le sandbox, pas à l'extérieur
"""
import requests
import json
from crewai.tools import tool
import os

# MCP Gateway URL (tourne dans le même sandbox sur localhost)
MCP_URL = os.getenv("MCP_URL", "http://localhost:8080")


def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """
    Appelle un tool MCP via le Gateway local

    Args:
        tool_name: Nom du tool MCP
        arguments: Arguments du tool

    Returns:
        Résultat du tool
    """
    try:
        response = requests.post(
            f"{MCP_URL}/tools/call",
            json={
                "name": tool_name,
                "arguments": arguments
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@tool("Python Interpreter")
def execute_python(code: str) -> str:
    """
    Execute Python code via MCP server

    IMPORTANT: N'utilise PAS Sandbox.create() car on est déjà dans un sandbox !
    Appelle le MCP Gateway qui tourne localement.

    Args:
        code: Python code to execute

    Returns:
        Execution output

    Example:
        >>> execute_python("print(5 + 3)")
        "8"
    """
    try:
        # Appel au MCP Gateway local
        result = call_mcp_tool("python_execution", {"code": code})

        if "error" in result:
            return f"❌ Error: {result['error']}"

        # Extraire le résultat du format MCP
        # Format MCP: {"content": [{"type": "text", "text": "..."}]}
        content = result.get("content", [])
        if content and len(content) > 0:
            text = content[0].get("text", "")
            return f"✅ Code executed:\n\n{text}"
        else:
            return "✅ Code executed (no output)"

    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool("Search DuckDuckGo")
def search_duckduckgo(query: str) -> str:
    """
    Search the web using DuckDuckGo via MCP

    Args:
        query: Search query

    Returns:
        Search results
    """
    try:
        result = call_mcp_tool("duckduckgo_search", {"query": query})

        if "error" in result:
            return f"❌ Search error: {result['error']}"

        # Formater les résultats
        content = result.get("content", [])
        if content:
            text = content[0].get("text", "")
            return f"✅ Search results:\n\n{text}"
        else:
            return "No results found"

    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool("Search ArXiv")
def search_arxiv(query: str) -> str:
    """
    Search ArXiv papers via MCP

    Args:
        query: Research topic

    Returns:
        ArXiv papers
    """
    try:
        result = call_mcp_tool("arxiv_search", {"query": query})

        if "error" in result:
            return f"❌ ArXiv error: {result['error']}"

        content = result.get("content", [])
        if content:
            text = content[0].get("text", "")
            return f"✅ ArXiv results:\n\n{text}"
        else:
            return "No papers found"

    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool("List MCP Tools")
def list_mcp_tools() -> str:
    """
    List all available MCP tools in the Gateway

    Returns:
        List of available tools
    """
    try:
        response = requests.post(
            f"{MCP_URL}/tools/list",
            timeout=10
        )
        response.raise_for_status()
        tools_data = response.json()

        # Formater la liste
        tools = tools_data.get("tools", [])
        if tools:
            tool_list = []
            for t in tools:
                name = t.get("name", "unknown")
                description = t.get("description", "No description")
                tool_list.append(f"- {name}: {description}")

            return f"✅ Available MCP tools:\n\n" + "\n".join(tool_list)
        else:
            return "No MCP tools available"

    except Exception as e:
        return f"❌ Error listing tools: {str(e)}"
