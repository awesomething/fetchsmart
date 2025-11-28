#!/usr/bin/env python3
"""
Test script to verify MCP server connectivity and endpoint structure.
"""
import requests
import json
import sys

MCP_URL = "https://mcp-server-uucrxxrxsq-uc.a.run.app"

def test_endpoint(path, method="GET", data=None, headers=None):
    """Test an endpoint and return status."""
    url = f"{MCP_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers or {}, timeout=5)
        else:
            response = requests.post(url, json=data, headers=headers or {}, timeout=5)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text[:200] if response.text else ""
        }
    except Exception as e:
        return {"error": str(e)}

print("🔍 Testing MCP Server Endpoints...")
print("=" * 60)
print(f"Base URL: {MCP_URL}\n")

# Test common MCP endpoints
endpoints = [
    ("/", "GET"),
    ("/sse", "POST", {"jsonrpc": "2.0", "method": "initialize", "params": {}}),
    ("/mcp", "POST", {"jsonrpc": "2.0", "method": "initialize", "params": {}}),
    ("/health", "GET"),
    ("/health_check", "GET"),
]

mcp_headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

for endpoint_info in endpoints:
    path = endpoint_info[0]
    method = endpoint_info[1]
    data = endpoint_info[2] if len(endpoint_info) > 2 else None
    
    print(f"Testing: {method} {path}")
    if data:
        print(f"  With MCP protocol headers")
        result = test_endpoint(path, method, data, mcp_headers)
    else:
        result = test_endpoint(path, method)
    
    if "error" in result:
        print(f"  ❌ Error: {result['error']}")
    else:
        status = result['status_code']
        symbol = "✅" if status == 200 else "⚠️" if status != 404 else "❌"
        print(f"  {symbol} Status: {status}")
        if status != 404 and result.get('text'):
            print(f"  Response preview: {result['text'][:100]}")
    print()

print("=" * 60)
print("\n💡 If all return 404, FastMCP might need explicit endpoint configuration.")
print("   Check FastMCP documentation for streamable-http endpoint setup.")

