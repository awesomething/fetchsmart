# Agent Deployment Reference

Quick reference for deploying multiple agents to the same GCP project without managing multiple `.env` files.

---

## Your Setup

**Project Configuration** (stays the same in `.env`):
```bash
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
MODEL=gemini-2.5-flash
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

**Agent-Specific Settings** (change per deployment):
```bash
AGENT_NAME=<agent-name>
GOOGLE_CLOUD_STAGING_BUCKET=<bucket-name>
```

---

## Deployed Agents

| Agent Name | Bucket | Purpose | Deploy Command |
|------------|--------|---------|----------------|
| `recruiter-agent` | `recruiter-staging` | Multi-agent coordinator (Planning, QA, Recruiter, Email, Staffing) | `AGENT_NAME=recruiter-agent GOOGLE_CLOUD_STAGING_BUCKET=recruiter-staging make deploy-adk` |

**Note:** The `recruiter-agent` is a root coordinator containing 6 sub-agents:
1. PlanningAgent - Goal planning & task decomposition
2. QAAgent - Google Docs search & Q&A
3. RecruiterOrchestrator - Candidate search, GitHub sourcing, pipeline metrics
4. RecruiterEmailPipeline - Outreach email generation & refinement
5. StaffingRecruiterOrchestrator - Job search, candidate matching, submissions
6. StaffingEmployerOrchestrator - Candidate review, interview scheduling

Add more agents here as you deploy them...

---

## How to Deploy Each Agent

### Method 1: Using Helper Scripts (Easiest)

```powershell
# Deploy planning agent
.\deploy-planning.ps1

# Deploy Q&A agent
.\deploy-docqabot.ps1

# Deploy any future agent
.\scripts\deploy-agent.ps1 -AgentName "agent3" -Bucket "agent3-staging"
```

### Method 2: Using Environment Variables

**Windows PowerShell:**
```powershell
# Recruiter agent (root coordinator with all sub-agents)
$env:AGENT_NAME="recruiter-agent"; $env:GOOGLE_CLOUD_STAGING_BUCKET="recruiter-staging"; make deploy-adk

# Future agents
$env:AGENT_NAME="agent3"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent3-staging"; make deploy-adk
```

**Linux/Mac Bash:**
```bash
# Recruiter agent (root coordinator with all sub-agents)
AGENT_NAME=recruiter-agent GOOGLE_CLOUD_STAGING_BUCKET=recruiter-staging make deploy-adk

# Future agents
AGENT_NAME=agent3 GOOGLE_CLOUD_STAGING_BUCKET=agent3-staging make deploy-adk
```

### Method 3: Edit .env Temporarily

1. Edit `.env` and change:
   ```bash
   AGENT_NAME=<your-agent-name>
   GOOGLE_CLOUD_STAGING_BUCKET=<your-bucket>
   ```

2. Deploy:
   ```bash
   make deploy-adk
   ```

3. Change `.env` back when done

---

## Creating Buckets

### For docqabot
```bash
make create-docqabot-bucket
```

### For future agents
```bash
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://<agent-name>-staging
```

Or use the bucket creation pattern:
```bash
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://agent3-staging
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://agent4-staging
```

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| **Create bucket** | `gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://<bucket-name>` |
| **List agents** | `gcloud ai agent-engines list --project=YOUR_PROJECT_ID --location=us-central1` |
| **Deploy agent** | `$env:AGENT_NAME="<name>"; $env:GOOGLE_CLOUD_STAGING_BUCKET="<bucket>"; make deploy-adk` |
| **View in console** | https://console.cloud.google.com/vertex-ai/agent-builder |
| **Check deployment** | `cat logs/deployment_metadata.json` |

---

## Adding a New Agent (Checklist)

- [ ] **Define agent purpose** and name
- [ ] **Create staging bucket**: `gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://<agent>-staging`
- [ ] **Deploy agent**: Use one of the methods above
- [ ] **Test in console**: Visit Agent Builder
- [ ] **Add to table**: Update the "Deployed Agents" table in this file
- [ ] **Create script** (optional): Create `deploy-<agent>.ps1` for convenience

---

## Best Practices

### 1. Keep .env for Your Primary Agent
Configure `.env` for the agent you develop/deploy most often:
```bash
AGENT_NAME=recruiter-agent  # Your main agent
GOOGLE_CLOUD_STAGING_BUCKET=recruiter-staging
```

### 2. Use Environment Variables for Others
Override when deploying different agents:
```powershell
$env:AGENT_NAME="custom-agent"; $env:GOOGLE_CLOUD_STAGING_BUCKET="custom-staging"; make deploy-adk
```

### 3. Create Helper Scripts
For agents you deploy frequently, create a simple script:
```powershell
# deploy-myagent.ps1
$env:AGENT_NAME="myagent"
$env:GOOGLE_CLOUD_STAGING_BUCKET="myagent-staging"
make deploy-adk
```

### 4. Use Consistent Naming
```
Agent Name: <purpose>-agent or <purpose>bot
Bucket: <agent-name>-staging
Example: analytics-agent → analytics-agent-staging
```

### 5. Track Your Agents
Maintain the table in this file with:
- Agent name
- Bucket name  
- Purpose/description
- Deployment command

---

## Troubleshooting

### Environment variables not taking effect?
**Solution:** Make sure you're setting them in the same command:
```powershell
# ✅ Correct (one line)
$env:AGENT_NAME="docqabot"; $env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"; make deploy-adk

# ❌ Wrong (separate commands - env vars may not persist)
$env:AGENT_NAME="docqabot"
$env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"
make deploy-adk
```

### Wrong agent deploying?
**Solution:** Check `logs/deployment_metadata.json` to see what was actually deployed:
```bash
cat logs/deployment_metadata.json
```

### Bucket permission errors?
**Solution:** Ensure bucket exists and you have access:
```bash
gsutil ls gs://<bucket-name>
```

---

## Architecture

```
Project: YOUR_PROJECT_ID (us-central1)
│
├── Agent: recruiter-agent
│   ├── Staging: gs://recruiter-staging/
│   ├── Artifacts: gs://YOUR_PROJECT_ID-recruiter-agent-logs-data/
│   ├── Type: LlmAgent (Root Coordinator)
│   └── Sub-agents:
│       ├── PlanningAgent (BuiltInPlanner)
│       ├── QAAgent (Google Drive tools)
│       ├── RecruiterOrchestrator (MCP tools)
│       ├── RecruiterEmailPipeline (Email generation)
│       ├── StaffingRecruiterOrchestrator (Job search)
│       └── StaffingEmployerOrchestrator (Candidate review)
│
└── Agent: <future-agent>
    ├── Staging: gs://<future-agent>-staging/
    ├── Artifacts: gs://YOUR_PROJECT_ID-<future-agent>-logs-data/
    └── Type: LlmAgent with custom tools
```

---

## Resources

- **[Deploy Doc Q&A Bot](./DEPLOY_DOCQABOT.md)** - Step-by-step guide
- **[Multi-Agent Deployment](./MULTI_AGENT_DEPLOYMENT.md)** - Comprehensive guide
- **[ADK Deployment Guide](./ADK_DEPLOYMENT_GUIDE.md)** - Full deployment docs
- **[Agent Builder Console](https://console.cloud.google.com/vertex-ai/agent-builder)** - View/test agents
- **[Cloud Storage Console](https://console.cloud.google.com/storage)** - Manage buckets

