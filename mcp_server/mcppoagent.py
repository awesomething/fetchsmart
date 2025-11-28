from typing import List, Dict
import json
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
# Load environment variables from .env file if present
load_dotenv()
# Print all environment variables (for debugging)
# for key, value in os.environ.items():
#     print(f"{key}={value}")
# Initialize FastMCP server
PORT = int(os.environ.get("PORT", 8099))
mcp = FastMCP("potool", host="0.0.0.0", port=PORT)

print("MCP server initialized successfully.")

# Health check endpoint
@mcp.tool()
async def health_check() -> str:
    """Health check endpoint for the MCP server"""
    return json.dumps({
        "status": "healthy",
        "server": "MCP Server",
        "tools_count": len(mcp.list_tools()) if hasattr(mcp, 'list_tools') else 1
    })

if __name__ == "__main__":
    # Initialize and run the server
    print("\n" + "=" * 60)
    print("Starting MCP Server")
    print("=" * 60)
    print(f"📍 Server: http://localhost:{PORT}")
    print(f"🔧 Transport: streamable-http")
    print(f"📦 Tools: 1 available (health_check)")
    print(f"💡 Test with: npx @modelcontextprotocol/inspector python mcppoagent.py")
    print("=" * 60 + "\n")
    mcp.run(transport='streamable-http')