# Deploying Multiple Agents in Same GCP Project

## Overview
You can deploy multiple ADK agents to the same Google Cloud project. Each agent:
- Has its own **unique agent name** (display name)
- Uses its own **staging bucket** (recommended but optional)
- Shares the same **project ID** and **location**
- Can use different **models** or **configurations**

This is useful for:
- Separating production vs. development agents
- Running specialized agents (e.g., Planning Agent vs. Q&A Agent)
- Testing different configurations or models

---

## Current Setup: Your Root Agent

### Root Agent: Recruiter Agent (Multi-Agent Coordinator)
```
AGENT_NAME=recruiter-agent
PROJECT_ID=YOUR_PROJECT_ID
LOCATION=us-central1
STAGING_BUCKET=recruiter-staging
```

**Note:** This is a root coordinator agent containing 6 sub-agents:
1. PlanningAgent - Goal planning & task decomposition
2. QAAgent - Google Docs search & Q&A
3. RecruiterOrchestrator - Candidate search, GitHub sourcing, pipeline metrics
4. RecruiterEmailPipeline - Outreach email generation & refinement
5. StaffingRecruiterOrchestrator - Job search, candidate matching, submissions
6. StaffingEmployerOrchestrator - Candidate review, interview scheduling

---

## Deployment Methods

### Method 1: Using Environment Files (Recommended)

Create separate `.env` files for each agent:

#### Step 1: Create `.env.recruiter` for Recruiter Agent
```bash
# .env.recruiter
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STAGING_BUCKET=recruiter-staging
AGENT_NAME=recruiter-agent
MODEL=gemini-2.5-flash

# Google Drive API (for QAAgent)
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# MCP Server (for Recruiter Orchestrator)
MCP_SERVER_URL=http://localhost:8100
```

#### Step 2: Deploy the Root Agent

**Deploy Recruiter Agent:**
```bash
# Load recruiter agent config
cp .env.recruiter .env

# Deploy
make deploy-adk
```

---

### Method 2: Using Environment Variables (Quick)

Deploy agents without changing files:

**Deploy Recruiter Agent:**
```bash
AGENT_NAME=recruiter-agent \
GOOGLE_CLOUD_STAGING_BUCKET=recruiter-staging \
make deploy-adk
```

---

### Method 3: Using Makefile Targets (Most Convenient)

Add dedicated targets to your `Makefile`:

```makefile
# Deploy recruiter agent (root coordinator)
deploy-recruiter:
	@echo "🚀 Deploying Recruiter Agent (Root Coordinator)..."
	@cp .env.recruiter .env
	@make deploy-adk
	@echo "✅ Recruiter Agent deployed!"
```

Then simply run:
```bash
make deploy-recruiter     # Deploy recruiter agent (all sub-agents included)
```

---

## Storage Bucket Options

### Option A: Separate Buckets (Recommended)
Each agent gets its own staging bucket for clean separation:

```bash
# Create recruiter agent bucket
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://recruiter-staging
```

**Note:** The root agent contains all sub-agents, so only one bucket is needed.

---

## Viewing Deployed Agents

### Using Google Cloud Console
1. Go to [Vertex AI Agent Builder](https://console.cloud.google.com/vertex-ai/agent-builder)
2. Select project: `YOUR_PROJECT_ID`
3. Navigate to **Agent Engine** → **Agents**
4. You'll see the deployed agent listed:
   - `recruiter-agent` (contains all 6 sub-agents)

### Using gcloud CLI
```bash
# List all agents in project
gcloud ai agent-engines list --project=YOUR_PROJECT_ID --location=us-central1

# Get details of specific agent
gcloud ai agent-engines describe AGENT_ID --project=YOUR_PROJECT_ID --location=us-central1
```

### Using ADK CLI
```bash
# List agents
uv run adk agent-engine list

# Get agent details
uv run adk agent-engine get --agent-name=docqabot
```

---

## Managing Multiple Agents

### Updating an Agent
When you deploy an agent with an existing name, it **updates** the agent:

```bash
# Update planning agent
AGENT_NAME=plannin-agent make deploy-adk

# Update Q&A agent
AGENT_NAME=docqabot make deploy-adk
```

### Deleting an Agent
```bash
# Delete via console
# Go to Vertex AI Agent Builder → Agents → Select agent → Delete

# Or via gcloud
gcloud ai agent-engines delete AGENT_ID \
  --project=YOUR_PROJECT_ID \
  --location=us-central1
```

### Testing the Agent
```bash
# Test recruiter agent (root coordinator)
AGENT_NAME=recruiter-agent uv run adk agent-engine test
```

---

## Configuration Best Practices

### 1. Use Clear Naming Conventions
```
recruiter-agent        → Root coordinator (all sub-agents)
recruiter-dev          → Development version
recruiter-prod         → Production version
```

### 2. Separate Environments
```
# Development
AGENT_NAME=recruiter-dev
STAGING_BUCKET=recruiter-dev-staging

# Production
AGENT_NAME=recruiter-agent
STAGING_BUCKET=recruiter-staging
```

### 3. Document Your Agents
Keep a file like `AGENTS.md`:
```markdown
# Deployed Agents

| Agent Name | Purpose | Bucket | Status |
|------------|---------|--------|--------|
| recruiter-agent | Root coordinator (6 sub-agents) | recruiter-staging | Active |
```

---

## Troubleshooting

### Issue: Agent name already exists
**Symptom:** Error when deploying with existing name
**Solution:** This is expected - it will update the existing agent

### Issue: Bucket access denied
**Symptom:** Permission errors during deployment
**Solution:** 
```bash
# Grant storage admin to your account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/storage.admin"
```

### Issue: Can't find deployed agent
**Symptom:** Agent doesn't appear in console
**Solution:** 
- Check you're in the right project (`YOUR_PROJECT_ID`)
- Check the right location (`us-central1`)
- Wait 1-2 minutes after deployment

### Issue: Wrong agent responding
**Symptom:** Wrong sub-agent handling the request
**Solution:** 
- Check your `.env` file has the right `AGENT_NAME`
- Verify deployment metadata in `logs/deployment_metadata.json`
- Check MODE directives in the UI are correct
- Review routing logic in `app/agent.py`

---

## Quick Reference

### Deploy Commands
```bash
# Method 1: Environment files
cp .env.recruiter .env && make deploy-adk

# Method 2: Inline environment variables
AGENT_NAME=recruiter-agent GOOGLE_CLOUD_STAGING_BUCKET=recruiter-staging make deploy-adk

# Method 3: Makefile targets (if added)
make deploy-recruiter
```

### Required Environment Variables
```bash
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID           # Same for all
GOOGLE_CLOUD_LOCATION=us-central1        # Same for all
GOOGLE_CLOUD_STAGING_BUCKET=<bucket>     # Unique per agent
AGENT_NAME=<name>                        # Unique per agent
```

### Bucket Naming Convention
```
<agent-name>-staging
recruiter-staging
recruiter-dev-staging
```

---

## Next Steps

1. **Create `.env.recruiter` file** (see Step 1 above)
2. **Create staging bucket**:
   ```bash
   gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://recruiter-staging
   ```
3. **Deploy recruiter agent** (root coordinator):
   ```bash
   cp .env.recruiter .env
   make deploy-adk
   ```
4. **Test the agent** in the Agent Builder console
5. **Test all modes** in the UI:
   - Planning mode
   - QA mode
   - Recruiter mode
   - Email mode
   - Staffing Recruiter mode
   - Staffing Employer mode

---

## Resources

- [Agent Engine Documentation](https://cloud.google.com/vertex-ai/docs/agent-engine/overview)
- [Multi-Agent Systems with ADK](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk)
- [ADK Deployment Guide](./ADK_DEPLOYMENT_GUIDE.md)
- [Google Drive Setup Guide](./GOOGLE_DRIVE_SETUP.md)

