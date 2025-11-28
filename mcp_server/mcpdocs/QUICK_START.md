# MCP Servers Quick Start Guide

Quick reference for deploying both MCP servers to Cloud Run.

## 🎯 Prerequisites Checklist

- [ ] Google Cloud SDK installed (`gcloud --version`)
- [ ] Docker installed and running (`docker ps`)
- [ ] Authenticated with GCP (`gcloud auth login`)
- [ ] Project set (`gcloud config set project baseshare`)
- [ ] Docker authenticated with GCR (`gcloud auth configure-docker`)

## 📦 Environment Variables Setup

### Staffing Backend

```bash
# Required
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"

# Optional (for JSearch API fallback)
export JSEARCHRAPDKEY="your-jsearch-api-key"
```

### Recruitment Backend

```bash
# Required
export GITHUB_TOKEN="ghp_your-github-token"

# Optional (for email lookup)
export HUNTER_API_KEY="your-hunter-api-key"
```

## 🚀 Deploy Staffing Backend

### Windows (PowerShell)

```powershell
cd mcp_server/staffing_backend
$env:SUPABASE_URL = "your-url"
$env:SUPABASE_SERVICE_KEY = "your-key"
.\deploy.ps1
```

### Linux/Mac (Bash)

```bash
cd mcp_server/staffing_backend
export SUPABASE_URL="your-url"
export SUPABASE_SERVICE_KEY="your-key"
chmod +x deploy.sh && ./deploy.sh
```

## 🚀 Deploy Recruitment Backend

### Windows (PowerShell)

```powershell
cd mcp_server/recruitment_backend
$env:GITHUB_TOKEN = "your-token"
.\deploy.ps1
```

### Linux/Mac (Bash)

```bash
cd mcp_server/recruitment_backend
export GITHUB_TOKEN="your-token"
chmod +x deploy.sh && ./deploy.sh
```

## 🔍 Get Service URLs

After deployment, get your service URLs:

```bash
# Staffing Backend
gcloud run services describe staffing-backend \
  --region us-central1 \
  --project baseshare \
  --format='value(status.url)'

# Recruitment Backend
gcloud run services describe recruitment-backend \
  --region us-central1 \
  --project baseshare \
  --format='value(status.url)'
```

## 🔗 Configure ADK Agents

Update your ADK agent environment variables:

```bash
# Staffing Backend (FastMCP - use /mcp endpoint)
STAFFING_MCP_SERVER_URL=https://staffing-backend-xyz-uc.a.run.app/mcp

# Recruitment Backend (A2A - use base URL)
RECRUITMENT_MCP_SERVER_URL=https://recruitment-backend-xyz-uc.a.run.app
```

## 🧪 Test Endpoints

```bash
# Staffing Backend MCP endpoint
curl https://staffing-backend-uucrxxrxsq-uc.a.run.app/mcp

# Recruitment Backend Agent Card
curl https://recruitment-backend-xyz-uc.a.run.app/.well-known/agent-card.json
```

## 📝 Manual Build Commands

If you prefer manual deployment:

### Staffing Backend

```bash
cd mcp_server/staffing_backend

# Build and test locally
docker build -t staffing-backend-local .
docker run -p 8100:8100 \
  -e SUPABASE_URL="..." \
  -e SUPABASE_SERVICE_KEY="..." \
  staffing-backend-local

# Build and push to GCR
docker build -t gcr.io/baseshare/staffing-backend .
docker push gcr.io/baseshare/staffing-backend

# Deploy to Cloud Run
gcloud run deploy staffing-backend \
  --image gcr.io/baseshare/staffing-backend \
  --region us-central1 \
  --project baseshare \
  --allow-unauthenticated \
  --port 8100 \
  --set-env-vars="SUPABASE_URL=${SUPABASE_URL},SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}"
```

### Recruitment Backend

```bash
cd mcp_server/recruitment_backend

# Build and test locally
docker build -t recruitment-backend-local .
docker run -p 8100:8100 \
  -e GITHUB_TOKEN="..." \
  recruitment-backend-local

# Build and push to GCR
docker build -t gcr.io/baseshare/recruitment-backend .
docker push gcr.io/baseshare/recruitment-backend

# Deploy to Cloud Run
gcloud run deploy recruitment-backend \
  --image gcr.io/baseshare/recruitment-backend \
  --region us-central1 \
  --project baseshare \
  --allow-unauthenticated \
  --port 8100 \
  --set-env-vars="GITHUB_TOKEN=${GITHUB_TOKEN}"
```

## 🆘 Troubleshooting

**Build fails?**

- Check Docker is running: `docker ps`
- Verify requirements.txt exists
- Check Python version (3.11+)

**Deployment fails?**

- Verify GCR auth: `gcloud auth configure-docker`
- Check project: `gcloud config get-value project`
- Verify environment variables are set

**Service not responding?**

- Check logs: `gcloud run services logs read <service-name> --region us-central1`
- Verify environment variables in Cloud Run console
- Test locally first

## 📚 Full Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment guide.
