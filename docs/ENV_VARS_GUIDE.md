# Environment Variables Guide

Complete guide to configuring environment variables for multi-agent deployment without multiple `.env` files.

---

## Quick Reference

### Required Variables (.env file)

```bash
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID    # Your GCP project ID
GOOGLE_CLOUD_LOCATION=us-central1       # GCP region
GOOGLE_CLOUD_STAGING_BUCKET=plannin     # Default staging bucket
AGENT_NAME=plannin-agent                # Default agent name
```

### Optional Variables

```bash
MODEL=gemini-2.5-flash                           # AI model (default shown)
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json  # For Google Drive API
```

---

## How Environment Variables Work

### 1. Base Configuration (.env file)
Your `.env` file contains **shared settings** for all agents:
```bash
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
MODEL=gemini-2.5-flash
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

And **default agent settings**:
```bash
AGENT_NAME=plannin-agent
GOOGLE_CLOUD_STAGING_BUCKET=plannin
```

### 2. Runtime Overrides
When deploying a different agent, **override** only agent-specific variables:

**Windows PowerShell:**
```powershell
$env:AGENT_NAME="docqabot"
$env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"
make deploy-adk
```

**Linux/Mac Bash:**
```bash
AGENT_NAME=docqabot GOOGLE_CLOUD_STAGING_BUCKET=docqabot-staging make deploy-adk
```

### 3. Variable Priority
Environment variables override `.env` file values:
```
1. Command-line environment variables (highest priority)
2. .env file values
3. Default values in code (lowest priority)
```

---

## Configuration in app/config.py

The `AgentConfiguration` class reads environment variables dynamically:

```python
@dataclass
class AgentConfiguration:
    """Reads environment variables at runtime for flexible deployment."""
    
    def __post_init__(self) -> None:
        # Load from .env file first
        load_environment_variables()
        
        # Then read from environment (overrides .env)
        self.model = os.environ.get("MODEL", "gemini-2.5-flash")
        self.deployment_name = os.environ.get("AGENT_NAME", "plannin-agent")
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.staging_bucket = os.environ.get("GOOGLE_CLOUD_STAGING_BUCKET")
```

**Key Points:**
- Variables are read **at runtime**, not at import time
- Command-line env vars override `.env` values
- Each deployment can use different `AGENT_NAME` and `GOOGLE_CLOUD_STAGING_BUCKET`

---

## Deployment Scenarios

### Scenario 1: Deploy Primary Agent
Use `.env` file as-is:
```bash
make deploy-adk
```
**Result:** Deploys `plannin-agent` with bucket `plannin`

### Scenario 2: Deploy Secondary Agent
Override agent-specific variables:
```powershell
$env:AGENT_NAME="docqabot"; $env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"; make deploy-adk
```
**Result:** Deploys `docqabot` with bucket `docqabot-staging`

### Scenario 3: Deploy Multiple Agents
Deploy each with different overrides:
```powershell
# Agent 1
$env:AGENT_NAME="agent1"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent1-staging"; make deploy-adk

# Agent 2
$env:AGENT_NAME="agent2"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent2-staging"; make deploy-adk

# Agent 3
$env:AGENT_NAME="agent3"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent3-staging"; make deploy-adk
```
**Result:** Three separate agents in the same project

---

## Variable Details

### GOOGLE_CLOUD_PROJECT
- **Required:** Yes
- **Source:** `.env` file or `gcloud auth` default
- **Example:** `your-project-id`
- **Purpose:** GCP project ID where agents are deployed
- **Shared:** Same for all agents

### GOOGLE_CLOUD_LOCATION
- **Required:** Yes
- **Source:** `.env` file
- **Default:** `us-central1`
- **Example:** `us-central1`, `us-east1`, `europe-west1`
- **Purpose:** GCP region for deployment
- **Shared:** Same for all agents (typically)

### GOOGLE_CLOUD_STAGING_BUCKET
- **Required:** Yes (for deployment)
- **Source:** `.env` file or environment override
- **Example:** `plannin`, `docqabot-staging`
- **Purpose:** GCS bucket for staging deployment artifacts
- **Per-Agent:** Can be unique or shared

### AGENT_NAME
- **Required:** Yes
- **Source:** `.env` file or environment override
- **Default:** `plannin-agent`
- **Example:** `plannin-agent`, `docqabot`, `analytics-bot`
- **Purpose:** Unique identifier for the deployed agent
- **Per-Agent:** Must be unique per agent
- **Format:** Letters, numbers, hyphens (no underscores in display name)

### MODEL
- **Required:** No
- **Source:** `.env` file or environment override
- **Default:** `gemini-2.5-flash`
- **Example:** `gemini-2.5-flash`, `gemini-2.0-pro`
- **Purpose:** AI model used by the agent
- **Per-Agent:** Can be different per agent

### GOOGLE_APPLICATION_CREDENTIALS
- **Required:** No (only if using Google Drive API or service account)
- **Source:** `.env` file
- **Example:** `./service-account-key.json`
- **Purpose:** Path to GCP service account key file
- **Shared:** Same for all agents (typically)

---

## Best Practices

### 1. Keep Shared Config in .env
```bash
# .env - shared across all agents
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
MODEL=gemini-2.5-flash
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

### 2. Override Agent-Specific Values
```bash
# .env - primary agent defaults
AGENT_NAME=plannin-agent
GOOGLE_CLOUD_STAGING_BUCKET=plannin

# Command-line - secondary agents
AGENT_NAME=docqabot GOOGLE_CLOUD_STAGING_BUCKET=docqabot-staging
```

### 3. Use Helper Scripts
Create `deploy-<agent>.ps1` for frequently deployed agents:
```powershell
# deploy-docqabot.ps1
$env:AGENT_NAME="docqabot"
$env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"
make deploy-adk
```

### 4. Document Your Agents
Keep a reference table (see `AGENTS_REFERENCE.md`):
| Agent Name | Bucket | Purpose |
|------------|--------|---------|
| plannin-agent | plannin | Goal planning |
| docqabot | docqabot-staging | Docs Q&A |

---

## Troubleshooting

### Issue: Wrong agent name showing in deployment
**Check:**
```bash
echo $env:AGENT_NAME  # PowerShell
echo $AGENT_NAME      # Bash
```

**Fix:** Set environment variable correctly:
```powershell
$env:AGENT_NAME="correct-agent-name"
```

### Issue: Bucket not found during deployment
**Check:**
```bash
gsutil ls gs://your-bucket-name
```

**Fix:** Create the bucket:
```bash
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://your-bucket-name
```

### Issue: Changes to .env not taking effect
**Cause:** Environment variables override `.env` values

**Fix:** Clear environment variables:
```powershell
# PowerShell
Remove-Item Env:\AGENT_NAME
Remove-Item Env:\GOOGLE_CLOUD_STAGING_BUCKET

# Bash
unset AGENT_NAME
unset GOOGLE_CLOUD_STAGING_BUCKET
```

### Issue: Config showing wrong values
**Debug:** Check what `config.py` sees:
```bash
# Deployment shows configuration summary
make deploy-adk

# Look for:
# 📋 Configuration Summary:
#   Agent Name: <actual-name>
#   💡 AGENT_NAME override detected: <if-overridden>
```

---

## Examples

### Example 1: Deploy with .env defaults
```bash
# .env has:
#   AGENT_NAME=plannin-agent
#   GOOGLE_CLOUD_STAGING_BUCKET=plannin

make deploy-adk
# Deploys: plannin-agent → gs://plannin
```

### Example 2: Deploy with overrides (Windows)
```powershell
$env:AGENT_NAME="docqabot"
$env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"
make deploy-adk
# Deploys: docqabot → gs://docqabot-staging
```

### Example 3: Deploy with overrides (Linux/Mac)
```bash
AGENT_NAME=docqabot \
GOOGLE_CLOUD_STAGING_BUCKET=docqabot-staging \
make deploy-adk
# Deploys: docqabot → gs://docqabot-staging
```

### Example 4: Deploy with helper script
```powershell
.\deploy-docqabot.ps1
# Deploys: docqabot → gs://docqabot-staging
# (Script sets env vars internally)
```

### Example 5: Deploy multiple agents sequentially
```powershell
# Agent 1
$env:AGENT_NAME="agent1"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent1-staging"; make deploy-adk

# Agent 2
$env:AGENT_NAME="agent2"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent2-staging"; make deploy-adk

# Agent 3
$env:AGENT_NAME="agent3"; $env:GOOGLE_CLOUD_STAGING_BUCKET="agent3-staging"; make deploy-adk
```

---

## Resources

- **Setup Example:** `env.example.txt` - Copy to `.env`
- **Deployment Guide:** `DEPLOY_DOCQABOT.md` - Deploy secondary agents
- **Agent Reference:** `AGENTS_REFERENCE.md` - Track your agents
- **Config Code:** `app/config.py` - See implementation

