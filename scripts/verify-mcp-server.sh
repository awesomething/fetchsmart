#!/bin/bash
# Verify MCP Server on Cloud Run

set -e

PROJECT_ID="baseshare"
REGION="us-central1"
SERVICE_NAME="mcp-server"

echo "🔍 Verifying MCP Server on Cloud Run..."
echo "=========================================="
echo ""

# 1. Get service URL
echo "1️⃣  Getting service URL..."
MCP_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --format='value(status.url)' 2>/dev/null)

if [ -z "$MCP_URL" ]; then
  echo "❌ Service not found or not accessible"
  exit 1
fi

echo "✅ Service URL: $MCP_URL"
echo ""

# 2. Check service status
echo "2️⃣  Checking service status..."
STATUS=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --format='value(status.conditions[0].status)' 2>/dev/null)

if [ "$STATUS" = "True" ]; then
  echo "✅ Service is READY"
else
  echo "⚠️  Service status: $STATUS"
fi
echo ""

# 3. Check recent logs
echo "3️⃣  Checking recent logs (last 5 lines)..."
gcloud run services logs read $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --limit 5 \
  --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -10
echo ""

# 4. Test basic connectivity
echo "4️⃣  Testing basic connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$MCP_URL/" || echo "000")
echo "   Root endpoint HTTP status: $HTTP_CODE"

if [ "$HTTP_CODE" = "404" ]; then
  echo "   ℹ️  404 is expected - MCP protocol doesn't use root endpoint"
fi
echo ""

# 5. Test with MCP protocol headers
echo "5️⃣  Testing MCP protocol endpoint..."
echo "   Note: FastMCP streamable-http uses MCP protocol, not REST"
echo "   Testing with proper MCP headers..."

# Try SSE endpoint (common for MCP)
SSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  "$MCP_URL/sse" 2>/dev/null || echo "000")
echo "   SSE endpoint HTTP status: $SSE_CODE"

# Try MCP endpoint
MCP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Content-Type: application/json" \
  "$MCP_URL" 2>/dev/null || echo "000")
echo "   Base URL HTTP status: $MCP_CODE"
echo ""

# 6. Verify environment variables
echo "6️⃣  MCP_SERVER_URL Configuration:"
echo "   For ADK agents, use:"
echo "   MCP_SERVER_URL=$MCP_URL"
echo ""
echo "   ⚠️  Do NOT use: $MCP_URL/mcp (FastMCP doesn't use /mcp path)"
echo ""

# 7. Summary
echo "=========================================="
echo "📋 Summary:"
echo "   ✅ Service URL: $MCP_URL"
echo "   ✅ Status: $STATUS"
echo ""
echo "💡 To test MCP tools, the ADK MCPToolset will handle protocol communication."
echo "   Just set: MCP_SERVER_URL=$MCP_URL"
echo ""
echo "🧪 To test locally with MCP Inspector:"
echo "   npx @modelcontextprotocol/inspector python mcppoagent.py"
echo ""

