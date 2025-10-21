"""
MCP Client for E2B sandbox connection
"""
import asyncio
import httpx
from typing import Dict, Any
from e2b import AsyncSandbox


class MCPClient:
    """Client to connect to MCP servers via E2B sandbox"""
    
    def __init__(self):
        self.sandbox = None
        self.mcp_url = None
        self.mcp_token = None
    
    async def create_sandbox(self, mcp_servers: Dict[str, Any] = None):
        """Create E2B sandbox with MCP servers"""
        if not mcp_servers:
            mcp_servers = {
                "duckduckgo": {},
                "arxiv": {"storagePath": "/"}
            }
        
        self.sandbox = await AsyncSandbox.beta_create(
            mcp=mcp_servers,
            timeout_ms=600_000
        )
        
        self.mcp_url = self.sandbox.beta_get_mcp_url()
        self.mcp_token = await self.sandbox.beta_get_mcp_token()
        
        return self.mcp_url
    
    async def list_tools(self):
        """List available MCP tools"""
        if not self.mcp_url or not self.mcp_token:
            raise ValueError("Sandbox not created")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.mcp_url}/tools/list",
                headers={"Authorization": f"Bearer {self.mcp_token}"}
            )
            return response.json()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call an MCP tool"""
        if not self.mcp_url or not self.mcp_token:
            raise ValueError("Sandbox not created")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.mcp_url}/tools/call",
                headers={"Authorization": f"Bearer {self.mcp_token}"},
                json={
                    "name": tool_name,
                    "arguments": arguments
                }
            )
            return response.json()
    
    async def execute_code(self, code: str):
        """Execute code in the sandbox"""
        if not self.sandbox:
            raise ValueError("Sandbox not created")
        
        execution = await self.sandbox.run_code(code)
        return execution.text
    
    async def close(self):
        """Close the sandbox"""
        if self.sandbox:
            await self.sandbox.aclose()