# Quick Guide: Deploy Doc Q&A Bot

This guide shows you how to deploy the **docqabot** agent to the same GCP project as your existing planning agent.

**Key Concept:** You don't need separate `.env` files for each agent! Just update `AGENT_NAME` and `GOOGLE_CLOUD_STAGING_BUCKET` in your single `.env` file, or pass them as environment variables when deploying.

---

## Prerequisites

✅ You already have:
- Project ID: `YOUR_PROJECT_ID`
- Location: `us-central1`
- Existing staging bucket: `plannin`
- Planning agent deployed: `plannin-agent`

---

## Step 1: Create Staging Bucket for Doc Q&A Bot

```bash
make create-docqabot-bucket
```

Or manually:
```bash
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://docqabot-staging
```

**Note:** You can reuse the `plannin` bucket if preferred, but separate buckets are cleaner for production.

---

## Step 2: Deploy Doc Q&A Bot

You have two options for deploying without creating separate `.env` files:

### Option A: Update .env Temporarily (Simplest)

Edit your `.env` file:
```bash
# Change these two lines:
AGENT_NAME=docqabot
GOOGLE_CLOUD_STAGING_BUCKET=docqabot-staging

# Keep these the same:
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
MODEL=gemini-2.5-flash
```

Then deploy:
```bash
make deploy-adk
```

**Remember to change them back** when deploying your planning agent again.

### Option B: Use Environment Variables (Recommended)

Deploy without touching your `.env` file:

**Windows (PowerShell):**
```powershell
$env:AGENT_NAME="docqabot"; $env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"; make deploy-adk
```

**Linux/Mac (Bash):**
```bash
AGENT_NAME=docqabot GOOGLE_CLOUD_STAGING_BUCKET=docqabot-staging make deploy-adk
```

This way, your `.env` file stays configured for your main agent, and you just override when deploying others.

---

## Step 3: Verify Deployment

### Check in Google Cloud Console
1. Go to [Vertex AI Agent Builder](https://console.cloud.google.com/vertex-ai/agent-builder)
2. Select project: **YOUR_PROJECT_ID**
3. Navigate to **Agent Engine** → **Agents**
4. You should see:
   - ✅ `plannin-agent` (existing)
   - ✅ `docqabot` (new)

### Check Using gcloud
```bash
gcloud ai agent-engines list \
  --project=YOUR_PROJECT_ID \
  --location=us-central1
```

---

## Step 4: Test the Agent

### Via Console
1. Go to your deployed agent in Vertex AI
2. Click **Test** or **Try it out**
3. Ask a question like: "What documents are available?"

### Via API
```bash
# Get agent endpoint from deployment metadata
cat logs/deployment_metadata.json

# Test with curl (replace AGENT_ID)
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"query": "What documents are available?"}' \
  https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/agent-engines/AGENT_ID:query
```

---

## Managing Multiple Agents

Since `plannin-agent` is already deployed, you can deploy `docqabot` independently without affecting it. Each agent is completely separate.

### Your Current Setup (.env)
Keep your `.env` configured for your primary agent (e.g., `plannin-agent`):
```bash
AGENT_NAME=plannin-agent
GOOGLE_CLOUD_STAGING_BUCKET=plannin
```

### Deploy Different Agents

**Deploy Planning Agent** (using .env):
```bash
make deploy-adk
```

**Deploy Q&A Agent** (override with env vars):

Windows:
```powershell
$env:AGENT_NAME="docqabot"; $env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"; make deploy-adk
```

Linux/Mac:
```bash
AGENT_NAME=docqabot GOOGLE_CLOUD_STAGING_BUCKET=docqabot-staging make deploy-adk
```

**Deploy Future Agent #3, #4, etc.:**

Just change the agent name and bucket:
```powershell
# Windows
$env:AGENT_NAME="agent3"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent3-staging"; make deploy-adk
$env:AGENT_NAME="agent4"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent4-staging"; make deploy-adk
```

```bash
AGENT_NAME=agent3 GOOGLE_CLOUD_STAGING_BUCKET=agent3-staging make deploy-adk
AGENT_NAME=agent4 GOOGLE_CLOUD_STAGING_BUCKET=agent4-staging make deploy-adk
```

### Update an Agent
Just deploy again with the same name:
```bash
# Update Q&A agent after code changes
AGENT_NAME=docqabot GOOGLE_CLOUD_STAGING_BUCKET=docqabot-staging make deploy-adk
```

**Pro Tip:** Create a simple script for agents you deploy frequently:
```powershell
# deploy-docqabot.ps1
$env:AGENT_NAME="docqabot"
$env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"
make deploy-adk
```

Then just run: `.\deploy-docqabot.ps1`

---

## Troubleshooting

### Error: Bucket not found
**Solution:** Create the bucket first:
```bash
make create-docqabot-bucket
```

### Error: Permission denied
**Solution:** Ensure you have the right IAM roles:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/aiplatform.user"
```

### Error: APIs not enabled
**Solution:** Enable required APIs:
```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
gcloud services enable storage.googleapis.com --project=YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project=YOUR_PROJECT_ID
gcloud services enable run.googleapis.com --project=YOUR_PROJECT_ID
```

### Can't see the agent in console
**Solution:** 
- Wait 1-2 minutes after deployment
- Check you're viewing the right project and location
- Check deployment logs: `cat logs/deployment_metadata.json`

---

## What's Different Between the Two Agents?

| Feature | plannin-agent | docqabot |
|---------|---------------|----------|
| **Purpose** | Goal planning & task decomposition | Google Docs Q&A |
| **Tools** | BuiltInPlanner | Google Drive API (search, read, list) |
| **Bucket** | `plannin` | `docqabot-staging` |
| **Agent Type** | LlmAgent with Planner | LlmAgent with tools |

Both agents:
- Share the same project: `YOUR_PROJECT_ID`
- Use the same location: `us-central1`
- Use the same model: `gemini-2.5-flash`

---

## Architecture Overview

```
Project: YOUR_PROJECT_ID
├── plannin-agent
│   ├── Staging: gs://plannin
│   ├── Type: Planning with BuiltInPlanner
│   └── Artifacts: YOUR_PROJECT_ID-plannin-agent-logs-data
└── docqabot
    ├── Staging: gs://docqabot-staging
    ├── Type: Q&A with Google Drive tools
    └── Artifacts: YOUR_PROJECT_ID-docqabot-logs-data
```

---

## Tracking Your Agents

Keep a simple reference of your deployed agents:

| Agent Name | Bucket | Purpose | Status |
|------------|--------|---------|--------|
| `plannin-agent` | `plannin` | Goal planning & task decomposition | ✅ Deployed |
| `docqabot` | `docqabot-staging` | Google Docs Q&A | 🚧 Deploying |

**Deployment Commands:**

```powershell
# Planning Agent (from .env)
make deploy-adk

# Doc Q&A Bot
$env:AGENT_NAME="docqabot"; $env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"; make deploy-adk

# Or use the helper script:
.\deploy-docqabot.ps1
```

---

## Quick Scripts Created

Three PowerShell scripts are now available in your repo:

1. **`deploy-planning.ps1`** - Deploy planning agent
2. **`deploy-docqabot.ps1`** - Deploy Q&A agent  
3. **`scripts/deploy-agent.ps1`** - Generic deployer for any agent

**Usage examples:**

```powershell
# Deploy specific agents
.\deploy-planning.ps1
.\deploy-docqabot.ps1

# Deploy any agent with custom settings
.\scripts\deploy-agent.ps1 -AgentName "myagent" -Bucket "myagent-staging"

# Deploy agent (bucket name auto-generated from agent name)
.\scripts\deploy-agent.ps1 -AgentName "analytics-bot"
```

---

## Next Steps

1. ✅ **Create the bucket**: Run `make create-docqabot-bucket`
2. 🚀 **Deploy the agent**: Run `.\deploy-docqabot.ps1` or use the PowerShell command
3. 📊 **Monitor deployment**: Check the console
4. 🧪 **Test the agent**: Ask some questions about your docs
5. 🔄 **Iterate**: Update code and redeploy as needed
6. 📝 **Track agents**: Update the table above with new agents

---

## Resources

- [Full Multi-Agent Deployment Guide](./MULTI_AGENT_DEPLOYMENT.md)
- [ADK Deployment Guide](./ADK_DEPLOYMENT_GUIDE.md)
- [Google Drive Setup](./GOOGLE_DRIVE_SETUP.md)
- [Multi-Agent Architecture](./MULTI_AGENT_ARCHITECTURE.md)

