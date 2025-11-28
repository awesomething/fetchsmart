"""
Test MCP server via HTTP requests
Tests the full MCP server running on localhost:8100
"""
import requests
import json

MCP_SERVER_URL = "http://localhost:8100"

def test_health_check():
    """Test health check endpoint"""
    print("\n🏥 Testing Health Check...")
    try:
        # FastMCP uses SSE endpoint for health checks
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health check passed")
            return True
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to MCP server")
        print("  💡 Make sure the server is running: python mcpstaffingagent.py")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_tool_via_mcp_inspector():
    """Instructions for testing via MCP Inspector"""
    print("\n🔧 Testing via MCP Inspector (Recommended)")
    print("  Steps:")
    print("  1. Start MCP server: python mcpstaffingagent.py")
    print("  2. In another terminal, run:")
    print("     npx @modelcontextprotocol/inspector python mcpstaffingagent.py")
    print("  3. Browser will open at http://localhost:6274")
    print("  4. Configure connection:")
    print("     - Transport: Streamable HTTP")
    print("     - URL: http://127.0.0.1:8100/sse")
    print("  5. Click 'Connect' and test tools in the UI")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing MCP Server (HTTP)")
    print("=" * 60)
    
    test_health_check()
    test_tool_via_mcp_inspector()
    
    print("\n💡 For full testing, use MCP Inspector (see instructions above)")

