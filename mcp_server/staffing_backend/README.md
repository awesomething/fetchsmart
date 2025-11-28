# Staffing MCP Backend

MCP server providing staffing agency tools: job search, candidate submissions, and hiring pipeline management.

## Quick Start

### 1. Setup Environment

```bash
# Create .env file
cat > .env << EOF
SUPABASE_URL=your-supabase-project-url
SUPABASE_SERVICE_KEY=your-service-role-key
JSEARCHRAPDKEY=your-rapidapi-key  # Optional, for fallback
PORT=8100
EOF
```

### 2. Install Dependencies

**Use the shared virtual environment from `mcp_server/`:**

```bash
# Activate shared venv (if not already active)
cd mcp_server
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install staffing backend dependencies
pip install -r staffing_backend/requirements.txt
```

**Note:** The `mcp_server/` directory has a shared `.venv` that all subdirectories use. Do not create a separate venv in `staffing_backend/`.

### 3. Test Tools Locally

```bash
# Using shared venv from mcp_server/
cd mcp_server
.venv\Scripts\activate  # Windows (if not already active)
python staffing_backend/test_tools.py

# Or use Makefile (handles venv automatically)
make test-staffing-tools
```

### 4. Start MCP Server

```bash
# Using shared venv from mcp_server/
cd mcp_server
.venv\Scripts\activate  # Windows (if not already active)
python staffing_backend/mcpstaffingagent.py

# Or use Makefile
make dev-staffing-mcp
```

### 5. Test with MCP Inspector

```bash
# In another terminal (using shared venv)
cd mcp_server
npx @modelcontextprotocol/inspector .venv/Scripts/python staffing_backend/mcpstaffingagent.py
```

Then open `http://localhost:6274` and connect to `http://127.0.0.1:8100/sse`

## Available Tools

1. **search_jobs** - Search job openings from Supabase with JSearch API fallback
2. **create_candidate_submission** - Create candidate submissions for job openings
3. **get_pipeline_status** - Get hiring pipeline status
4. **update_pipeline_stage** - Update candidate pipeline stages
5. **health_check** - Health check endpoint

## Testing

See `TESTING_GUIDE.md` in the project root for comprehensive testing instructions.

## Deployment

See `TODOSupply.md` for Cloud Run deployment instructions.


### Troubleshooting

## Session Terminated Fixed

- Found two stray `python.exe` processes (PIDs 33760 & 38676) bound to port 8100. They weren’t the FastMCP server, so `/mcp` returned 404 and every ADK initialize call was dropped → “Session terminated”.
- Stopped both processes, then restarted the real staffing MCP server with the project’s venv (`make dev-staffing-mcp`). The server now logs the correct StreamableHTTP endpoint and stays alive.
- Verified connectivity with the same handshake the ADK client performs:

```
curl -i -X POST http://localhost:8100/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"diag","version":"1.0"}}}'
```

The response streams an `event: message` payload (protocolVersion, capabilities, serverInfo), confirming the MCP session stays open.

### What to do going forward
1. Start the MCP server with `make dev-staffing-mcp` before using the staffing modes and keep that terminal running.
2. Ensure `STAFFING_MCP_SERVER_URL=http://localhost:8100/mcp` in `app/.env`.
3. If “Session terminated” reappears, run `netstat -ano | findstr 8100` and kill any leftover `python.exe` processes using that port, then restart the server.

The frontend can now connect without terminating the session.
