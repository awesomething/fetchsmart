# Migration Guide: Converting Recruitment Backend from A2A to FastMCP

## Overview

This guide documents the process of converting the `recruitment-backend` from **A2A (Agent-to-Agent) protocol** to **FastMCP** to match the `staffing-backend` architecture. This migration will:

- ✅ Fix the "Method not found" error (`-32601`) when `MCPToolset` tries to connect
- ✅ Standardize both backends to use the same MCP protocol
- ✅ Enable proper MCP tool discovery and invocation
- ✅ Simplify deployment and maintenance

## Current State vs. Target State

### Current State (A2A)
- **Protocol**: A2A (Agent-to-Agent) via `A2AStarletteApplication`
- **Server Type**: Full ADK agent with A2A endpoints
- **Tool Exposure**: Tools wrapped in ADK agent, exposed via A2A protocol
- **MCP Compatibility**: ❌ Not compatible with `MCPToolset`
- **Endpoint**: Base URL (no `/mcp` path)
- **Error**: `Code=-32601, Message='Method not found'` when `MCPToolset` tries to initialize

### Target State (FastMCP)
- **Protocol**: FastMCP (Model Context Protocol)
- **Server Type**: MCP server with tool registrations
- **Tool Exposure**: Direct MCP tool functions with `@mcp.tool()` decorator
- **MCP Compatibility**: ✅ Fully compatible with `MCPToolset`
- **Endpoint**: `/mcp` path (e.g., `https://recruitment-backend-xyz.run.app/mcp`)
- **Result**: `MCPToolset` can successfully connect and discover tools

## Key Differences

| Aspect | A2A Server | FastMCP Server |
|--------|-----------|----------------|
| **Import** | `from a2a.server.apps import A2AStarletteApplication` | `from mcp.server.fastmcp import FastMCP` |
| **Server Init** | `A2AStarletteApplication(agent_card=..., http_handler=...)` | `FastMCP("recruitment-agent", host="0.0.0.0", port=PORT)` |
| **Tool Registration** | Tools wrapped in ADK agent, exposed via A2A | Direct `@mcp.tool()` decorator on async functions |
| **Tool Function** | Regular Python functions | Async functions (`async def`) |
| **Server Start** | `uvicorn.run(server.build(), ...)` | `mcp.run(transport='streamable-http')` |
| **Dependencies** | `google-adk`, `a2a-sdk`, `uvicorn` | `fastmcp` (includes server) |
| **Endpoint** | Base URL | `/mcp` path |

## Migration Steps

### Step 1: Update Dependencies

**File**: `mcp_server/recruitment_backend/requirements.txt`

**Remove:**
```txt
google-adk>=1.10.0
a2a-sdk>=0.2.5
uvicorn>=0.30.0
nest-asyncio>=1.6.0
```

**Add:**
```txt
fastmcp>=0.9.0
```

**Keep:**
```txt
python-dotenv>=1.0.0
requests>=2.31.0
```

**Final `requirements.txt`:**
```txt
# Recruitment Backend Dependencies
# FastMCP Server for MCP Protocol

# MCP Server
fastmcp>=0.9.0

# Environment
python-dotenv>=1.0.0

# HTTP Client (for GitHub API, Hunter API)
requests>=2.31.0
```

### Step 2: Refactor Server File

**File**: `mcp_server/recruitment_backend/server.py`

#### 2.1 Update Imports

**Remove:**
```python
from google.adk.agents import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from a2a.server.apps import A2AStarletteApplication
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
import uvicorn
```

**Add:**
```python
from mcp.server.fastmcp import FastMCP
```

**Keep:**
```python
import os
import sys
import logging
import json
from typing import Any, List, Dict
from dotenv import load_dotenv
from recruitment_service import recruitment_service
from candidate_matcher import CandidateMatcher
from github_scraper import GitHubProfileScraper
```

#### 2.2 Initialize FastMCP Server

**Replace the A2A server initialization (around line 695-825) with:**

```python
# Initialize FastMCP server
PORT = int(os.environ.get("PORT", 8100))
HOST = os.environ.get("HOST", "0.0.0.0")

# FastMCP automatically handles MCP protocol initialization
# The 'streamable-http' transport is compatible with ADK's MCPToolset
mcp = FastMCP("recruitment-agent", host=HOST, port=PORT)
```

#### 2.3 Convert Tool Functions to Async MCP Tools

**Current tool functions (synchronous):**
```python
def search_candidates_tool(
    job_description: str,
    job_title: str = "",
    limit: int = 8
) -> str:
    # ... implementation
```

**Convert to async MCP tools:**
```python
@mcp.tool()
async def search_candidates_tool(
    job_description: str,
    job_title: str = "",
    limit: int = 8
) -> str:
    """
    Intelligent candidate search using AI-powered matching.
    
    Args:
        job_description: Natural language job description or requirements
        job_title: Optional job title for better matching
        limit: Number of top candidates to return (default: 8)
    
    Returns:
        JSON string with matched candidates, scores, and reasons
    """
    logger.info(f"[REQUEST] search_candidates_tool called: job_title={job_title}, limit={limit}")
    try:
        candidates = recruitment_service.candidates
        results = matcher.match_candidates(
            candidates=candidates,
            job_description=job_description,
            job_title=job_title,
            limit=limit
        )
        
        # Format for agent consumption
        response = {
            "query": job_description,
            "total_matches": results['total_matches'],
            "showing_top": results['showing'],
            "requirements_detected": results['requirements'],
            "top_candidates": []
        }
        
        for match in results['top_candidates']:
            candidate = match['candidate']
            likely_roles = candidate.get('likely_roles') or []
            role = likely_roles[0] if likely_roles else 'Software Engineer'
            candidate_id = candidate.get('id') or candidate.get('github_username') or 'unknown'
            
            response['top_candidates'].append({
                "id": candidate_id,
                "name": candidate.get('name') or candidate.get('github_username', 'Unknown'),
                "github_username": candidate.get('github_username', ''),
                "github_profile_url": candidate.get('github_profile_url', ''),
                "role": role,
                "experience_level": candidate.get('estimated_experience_level', 'Mid'),
                "location": candidate.get('location', ''),
                "primary_language": candidate.get('primary_language', ''),
                "skills": candidate.get('skills', [])[:8],
                "github_stats": {
                    "repos": candidate.get('public_repos', 0),
                    "stars": candidate.get('total_stars', 0),
                    "followers": candidate.get('followers', 0),
                },
                "match_score": match.get('match_score', 0),
                "match_reasons": match.get('match_reasons', []),
                "matched_skills": match.get('matched_skills', []),
            })
        
        result = json.dumps(response, indent=2)
        logger.info(f"[SUCCESS] search_candidates_tool completed: {response.get('showing_top', 0)} candidates found")
        return result
    except Exception as e:
        logger.error(f"[ERROR] search_candidates_tool failed: {e}", exc_info=True)
        return json.dumps({"error": str(e), "status": "failed"})
```

**Apply the same pattern to all tool functions:**
- `scrape_github_profiles_tool` → `@mcp.tool()` + `async def`
- `get_compensation_data_tool` → `@mcp.tool()` + `async def`
- `get_pipeline_metrics_tool` → `@mcp.tool()` + `async def`
- `analyze_portfolio_tool` → `@mcp.tool()` + `async def`
- `get_time_tracking_tool` → `@mcp.tool()` + `async def`
- `generate_recruitment_report_tool` → `@mcp.tool()` + `async def`
- `send_recruitment_email_tool` → `@mcp.tool()` + `async def`
- `find_emails_by_github_usernames_tool` → `@mcp.tool()` + `async def`
- `find_candidate_emails_tool` → `@mcp.tool()` + `async def`

#### 2.4 Remove ADK Agent Creation

**Remove the entire `create_recruitment_agent()` function and related ADK agent setup:**
- Remove `create_recruitment_agent()` function (lines ~682-750)
- Remove ADK agent creation code
- Remove A2A server setup code
- Remove `main()` function's A2A-specific initialization

#### 2.5 Update Server Startup

**Replace the `main()` function (around line 695-846) with:**

```python
def main():
    """Start the FastMCP server."""
    try:
        logger.info("=" * 60)
        logger.info("🚀 Recruitment Backend MCP Server Starting...")
        logger.info("=" * 60)
        logger.info(f"📍 Server: http://{HOST}:{PORT}")
        logger.info(f"🔧 Transport: streamable-http")
        logger.info(f"📦 Tools: {len([f for f in dir(mcp) if hasattr(getattr(mcp, f), '__name__')])} available")
        logger.info(f"💡 Test with: npx @modelcontextprotocol/inspector python server.py")
        logger.info("=" * 60)
        logger.info(f"[INFO] MCP endpoint will be available at: http://{HOST}:{PORT}/mcp")
        logger.info(f"[INFO] ADK agents should connect to: http://{HOST}:{PORT}/mcp")
        logger.info("=" * 60)
        logger.info(f"[INFO] Environment: PORT={PORT}, HOST={HOST}")
        logger.info(f"[INFO] Cloud Run will map this to the service URL")
        logger.info("=" * 60)
        
        # Start FastMCP server
        logger.info(f"[INFO] Starting FastMCP server on port {PORT}...")
        mcp.run(transport='streamable-http')
        
    except KeyboardInterrupt:
        logger.info("\n[INFO] Server stopped by user")
    except Exception as e:
        logger.error(f"\n[ERROR] Server crashed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

### Step 3: Update Dockerfile (if needed)

**File**: `mcp_server/recruitment_backend/Dockerfile`

**Verify the CMD is correct:**
```dockerfile
# Run the MCP server
CMD ["python", "server.py"]
```

This should already be correct, but verify it points to `server.py` (not a different entry point).

### Step 4: Update Deployment Scripts

**Files**: 
- `mcp_server/recruitment_backend/deploy.sh`
- `mcp_server/recruitment_backend/deploy.ps1`

**Update the MCP endpoint reference:**

**In deploy.sh (around line 159):**
```bash
echo "🔗 MCP Endpoint:"
echo "   ${SERVICE_URL}/mcp"
echo ""
echo "💡 Set this in your ADK agent environment:"
echo "   RECRUITMENT_MCP_SERVER_URL=${SERVICE_URL}/mcp"
```

**In deploy.ps1 (around line 176):**
```powershell
Write-Host "🔗 MCP Endpoint:" -ForegroundColor Cyan
Write-Host "   $SERVICE_URL/mcp"
Write-Host ""
Write-Host "💡 Set this in your ADK agent environment:" -ForegroundColor Yellow
Write-Host "   RECRUITMENT_MCP_SERVER_URL=$SERVICE_URL/mcp"
```

### Step 5: Update Agent Configuration

**File**: `app/recruiter_agents/recruiter_orchestrator_agent/adk_agent.py`

**Update the URL format (around line 156):**

**Change from:**
```python
# Note: Recruitment backend uses A2A protocol but exposes MCP tools
# Use base URL (no /mcp path) as per deployment docs
recruitment_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(url=recruitment_mcp_url),
    tool_filter=["search_candidates_tool"]
)
```

**Change to:**
```python
# Note: Recruitment backend now uses FastMCP (same as staffing backend)
# Use /mcp endpoint path
if not recruitment_mcp_url.endswith('/mcp'):
    recruitment_mcp_url = f"{recruitment_mcp_url.rstrip('/')}/mcp"

recruitment_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(url=recruitment_mcp_url),
    tool_filter=["search_candidates_tool"]
)
```

**Also update other agents that use `MCP_SERVER_URL` for recruitment:**
- `app/recruiter_agents/resume_screening_agent/agent.py` (line 58)
- `app/recruiter_agents/recruiter_productivity_agent/agent.py` (line 47)
- `app/recruiter_agents/compensation_agent/agent.py` (if it uses MCP)

**Update to:**
```python
mcp_url = os.getenv("RECRUITMENT_MCP_SERVER_URL", "http://localhost:8100/mcp")
# Ensure /mcp path is included
if not mcp_url.endswith('/mcp'):
    mcp_url = f"{mcp_url.rstrip('/')}/mcp"
```

### Step 6: Update Documentation

**Files to update:**
- `mcp_server/mcpdocs/DEPLOYMENT.md` - Update recruitment backend section
- `mcp_server/mcpdocs/QUICK_START.md` - Update URL format
- `docs/MCP_SESSION_ERROR_FIX.md` - Update with new URL format
- `README.md` - Update any references

**Key changes:**
- Change "A2A server" → "FastMCP server"
- Change "base URL (no /mcp path)" → "URL with /mcp endpoint"
- Update example URLs to include `/mcp`

### Step 7: Update Environment Variables

**After deployment, update environment variables:**

**For Agent Engine deployment:**
```bash
# OLD (A2A - base URL)
RECRUITMENT_MCP_SERVER_URL=https://recruitment-backend-143611176760.us-central1.run.app

# NEW (FastMCP - with /mcp)
RECRUITMENT_MCP_SERVER_URL=https://recruitment-backend-143611176760.us-central1.run.app/mcp
```

**For local development:**
```bash
# OLD
MCP_SERVER_URL=http://localhost:8100

# NEW
RECRUITMENT_MCP_SERVER_URL=http://localhost:8100/mcp
```

## Testing Steps

### 1. Local Testing

```bash
cd mcp_server/recruitment_backend

# Install new dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN="your-token"
export HUNTER_API_KEY="your-key"

# Run server
python server.py
```

**Expected output:**
```
[12/02/25 10:00:00] INFO ============================================================
[12/02/25 10:00:00] INFO 🚀 Recruitment Backend MCP Server Starting...
[12/02/25 10:00:00] INFO ============================================================
[12/02/25 10:00:00] INFO 📍 Server: http://0.0.0.0:8100
[12/02/25 10:00:00] INFO 🔧 Transport: streamable-http
[12/02/25 10:00:00] INFO [INFO] MCP endpoint will be available at: http://0.0.0.0:8100/mcp
```

### 2. Test MCP Endpoint

```bash
# Test MCP endpoint (should return 406 - this is expected for MCP protocol)
curl http://localhost:8100/mcp

# Expected: JSON-RPC error with 406 or method not found (normal for direct curl)
# MCPToolset will send proper headers
```

### 3. Test with MCP Inspector

```bash
# Install MCP inspector
npx @modelcontextprotocol/inspector python server.py

# Should show all registered tools
```

### 4. Test with ADK Agent

**Update local `.env` or environment:**
```bash
export RECRUITMENT_MCP_SERVER_URL=http://localhost:8100/mcp
```

**Run agent locally:**
```bash
cd app/recruiter_agents/recruiter_orchestrator_agent
python -c "from adk_agent import recruiter_orchestrator_agent; print('Agent loaded successfully')"
```

**Expected:**
```
[INFO] Attempting to connect to recruitment MCP backend: http://localhost:8100/mcp
[OK] ✅ MCP recruitment backend configured successfully: http://localhost:8100/mcp
[OK] ✅ search_candidates_tool will be available via MCP
```

### 5. Test Tool Invocation

**Create a test script:**
```python
# test_recruitment_mcp.py
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(url="http://localhost:8100/mcp"),
    tool_filter=["search_candidates_tool"]
)

# Test tool call
result = mcp_toolset.search_candidates_tool(
    job_description="Find senior React engineers",
    limit=5
)
print(result)
```

## Deployment Checklist

- [ ] Update `requirements.txt` (remove A2A/ADK deps, add FastMCP)
- [ ] Refactor `server.py` (replace A2A with FastMCP)
- [ ] Convert all tool functions to `@mcp.tool()` async functions
- [ ] Update deployment scripts to reference `/mcp` endpoint
- [ ] Update agent configurations to use `/mcp` URL
- [ ] Test locally with MCP inspector
- [ ] Test locally with ADK agent
- [ ] Build Docker image: `docker build -t gcr.io/baseshare/recruitment-backend .`
- [ ] Test Docker image locally
- [ ] Push to GCR: `docker push gcr.io/baseshare/recruitment-backend`
- [ ] Deploy to Cloud Run: `gcloud run deploy recruitment-backend ...`
- [ ] Verify Cloud Run logs show FastMCP startup
- [ ] Test Cloud Run endpoint: `curl https://recruitment-backend-xyz.run.app/mcp`
- [ ] Update `RECRUITMENT_MCP_SERVER_URL` in Agent Engine deployment
- [ ] Redeploy Agent Engine with new URL
- [ ] Test end-to-end: "Find senior engineers on GitHub"
- [ ] Verify no more "Method not found" errors

## Rollback Plan

If issues occur after deployment:

1. **Revert to previous Docker image:**
   ```bash
   gcloud run deploy recruitment-backend \
     --image gcr.io/baseshare/recruitment-backend:previous-tag \
     --region us-central1
   ```

2. **Revert environment variables:**
   ```bash
   # Change back to base URL (no /mcp)
   export RECRUITMENT_MCP_SERVER_URL=https://recruitment-backend-xyz.run.app
   ```

3. **Redeploy Agent Engine** with old URL format

## Benefits After Migration

✅ **Fixed Compatibility**: `MCPToolset` can successfully connect and discover tools  
✅ **Standardized Architecture**: Both backends use the same FastMCP protocol  
✅ **Simplified Dependencies**: Removed heavy ADK/A2A dependencies  
✅ **Better Error Handling**: FastMCP provides better MCP protocol error messages  
✅ **Easier Testing**: Can use MCP inspector and standard MCP tools  
✅ **Consistent URL Format**: Both backends use `/mcp` endpoint pattern  

## Common Issues and Solutions

### Issue: "Module 'mcp' has no attribute 'server'"

**Solution**: Ensure `fastmcp>=0.9.0` is installed:
```bash
pip install fastmcp>=0.9.0
```

### Issue: "Tool function must be async"

**Solution**: All `@mcp.tool()` decorated functions must be `async def`:
```python
@mcp.tool()
async def my_tool(...) -> str:  # ✅ Correct
    ...

@mcp.tool()
def my_tool(...) -> str:  # ❌ Wrong - must be async
    ...
```

### Issue: "MCPToolset still can't connect after migration"

**Solution**: 
1. Verify URL includes `/mcp`: `https://recruitment-backend-xyz.run.app/mcp`
2. Check Cloud Run logs for FastMCP startup messages
3. Verify `mcp.run(transport='streamable-http')` is being called
4. Test with MCP inspector first

### Issue: "Tools not appearing in MCPToolset"

**Solution**:
1. Verify all tools have `@mcp.tool()` decorator
2. Check tool function signatures match expected format
3. Verify `tool_filter` in `MCPToolset` matches tool names
4. Check server logs for tool registration messages

## References

- **FastMCP Documentation**: [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- **Staffing Backend Reference**: `mcp_server/staffing_backend/mcpstaffingagent.py`
- **MCP Protocol Spec**: [Model Context Protocol](https://modelcontextprotocol.io)

## Summary

This migration converts the recruitment backend from A2A to FastMCP, making it compatible with `MCPToolset` and standardizing it with the staffing backend. The key changes are:

1. Replace A2A server with FastMCP server
2. Convert tool functions to async MCP tools with `@mcp.tool()` decorator
3. Update URL format to include `/mcp` endpoint
4. Update all agent configurations to use new URL format
5. Test thoroughly before production deployment

After migration, both backends will use FastMCP, eliminating the "Method not found" error and providing a consistent architecture.

