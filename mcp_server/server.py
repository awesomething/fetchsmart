import os
import requests
from typing import Any, Dict

class MCPTool:
    """Base class for MCP tool HTTP communication"""
    
    def __init__(self):
        self.mcp_url = os.environ.get(
            "MCP_SERVER_URL",
            "http://localhost:8080/mcp"
        )
    
    def health_check(self) -> bool:
        """Check if MCP server is running"""
        response = requests.get(f"{self.mcp_url}/health")
        return response.status_code == 200
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Call MCP server tool via HTTP"""