# Agent Routing Architecture Explained

## Why Only One Agent Endpoint in Vercel?

**TL;DR:** You only need **one agent endpoint** (e.g., `recruiter-agent`) in Vercel because it's the **root coordinator** that manages all sub-agents.

### Architecture Overview

```
Vercel Frontend
    ↓
AGENT_ENGINE_ENDPOINT=https://us-central1-YOUR_PROJECT_ID.pkg.dev/...
    ↓
Root Agent (recruiter-agent) - Coordinator
    ├── PlanningAgent (goal planning & task decomposition)
    ├── QAAgent (Google Docs search)
    ├── RecruiterOrchestrator (candidate search, GitHub sourcing)
    ├── RecruiterEmailPipeline (outreach email generation & refinement)
    ├── StaffingRecruiterOrchestrator (job search, candidate matching)
    └── StaffingEmployerOrchestrator (candidate review, interview scheduling)
```

### How It Works

1. **Single Deployment**: The `root_agent` (deployed as `recruiter-agent` or custom name) contains all sub-agents embedded within it
2. **Smart Routing**: The root agent analyzes user requests and routes to the appropriate specialist
3. **Mode Override**: The frontend can force routing using `[MODE:XXX]` directives
4. **Coordinated Response**: The root agent returns the specialist's response to the user

### Why This Design?

- **Simpler Deployment**: One endpoint to manage instead of multiple
- **Better Coordination**: Root agent can coordinate multi-agent workflows
- **Cost Efficient**: Single agent instance handles all routing
- **Easier Maintenance**: Update routing logic in one place

## Routing Mechanism

### Mode Directives (From UI)

When a user selects a specific mode in the UI, the frontend prepends a directive:

- `[MODE:PLANNING]` → Routes to PlanningAgent
- `[MODE:QA]` → Routes to QAAgent  
- `[MODE:RECRUITER]` → Routes to RecruiterOrchestrator
- `[MODE:EMAIL]` → Routes to RecruiterEmailPipeline
- `[MODE:STAFFING_RECRUITER]` → Routes to StaffingRecruiterOrchestrator
- `[MODE:STAFFING_EMPLOYER]` or `[MODE:EMPLOYER]` → Routes to StaffingEmployerOrchestrator
- No directive → Smart routing based on intent

### Smart Routing (Auto Mode)

When no directive is present, the root agent analyzes the request:

- Planning/strategy/goals → PlanningAgent
- Document questions/search → QAAgent
- Recruitment/hiring/candidates/GitHub sourcing → RecruiterOrchestrator
- Outreach email drafting/refinement → RecruiterEmailPipeline
- Staffing agency job search/candidate matching → StaffingRecruiterOrchestrator
- Employer candidate review/interview scheduling → StaffingEmployerOrchestrator

## Troubleshooting

### Issue: Bot Always Responds as Planning Agent

**Cause**: The root agent's routing instruction wasn't strict enough about following MODE directives.

**Fix Applied**: Updated `app/agent.py` to:
1. Check for MODE directives FIRST (before smart routing)
2. Use explicit, forceful language: "MUST FOLLOW", "IMMEDIATELY delegate"
3. Provide clear examples of directive processing

**Action Required**: Redeploy the agent after the fix:

```bash
AGENT_NAME=recruiter-agent \
GOOGLE_CLOUD_STAGING_BUCKET=recruiter-staging \
make deploy-adk
```

### Issue: QA Agent Not Responding

**Possible Causes**:
1. Google Drive credentials not set in Agent Engine environment
2. MODE directive not being processed correctly
3. Root agent not routing to QAAgent

**Check**:
- Verify `GOOGLE_SERVICE_ACCOUNT_KEY_BASE64` is set in Agent Engine deployment
- Check logs to see if `[MODE:QA]` directive is being received
- Verify root agent is routing correctly (logs should show delegation)

### Issue: Agent Not Responding At All

**Possible Causes**:
1. Agent Engine endpoint incorrect in Vercel
2. Network/timeout issues
3. Agent deployment failed

**Check**:
- Verify `AGENT_ENGINE_ENDPOINT` in Vercel matches your deployed agent
- Check Agent Engine logs in GCP Console
- Verify agent is deployed and active

## Environment Variables

### Vercel (Frontend)
- `AGENT_ENGINE_ENDPOINT`: URL to your deployed root agent

### Agent Engine (Backend)
- `GOOGLE_SERVICE_ACCOUNT_KEY_BASE64`: For Google Drive access (QAAgent)
- `MCP_SERVER_URL`: For recruitment agents (Recruiter Orchestrator)
- `AGENT_NAME`: Deployment name (e.g., `recruiter-agent`)

## Verification Steps

1. **Check Agent Deployment**:
   ```bash
   gcloud ai reasoning-engines list --project=YOUR_PROJECT_ID --location=us-central1
   ```

2. **Test MODE Directive**:
   - Select "FAQ Agent" mode in UI (MODE:QA)
   - Ask: "What is our deployment process?"
   - Should route to QAAgent (not PlanningAgent)
   - Try other modes: Recruiter, Email, Staffing Recruiter, Staffing Employer

3. **Check Logs**:
   - Look for `[MODE:QA]` in request payload
   - Verify root agent delegates to QAAgent
   - Check QAAgent uses Google Drive tools

## Next Steps

After applying the routing fix:

1. **Redeploy the agent** with updated instructions
2. **Test each mode** in the UI to verify routing
3. **Monitor logs** to ensure correct delegation
4. **Verify Google Drive access** for QAAgent responses

