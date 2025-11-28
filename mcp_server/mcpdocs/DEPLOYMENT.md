# MCP Servers Deployment Guide

This guide covers deploying both MCP servers to Google Cloud Run:
- **Staffing Backend**: FastMCP server for job search, candidate submission, and hiring pipeline
- **Recruitment Backend**: A2A server with MCP tools for candidate sourcing and portfolio analysis

## 📋 Prerequisites

1. **Google Cloud SDK** installed and authenticated
   ```bash
   gcloud auth login
   gcloud config set project baseshare
   gcloud auth configure-docker
   ```

2. **Docker** installed and running

3. **Environment Variables** prepared (see below)

## 🔧 Environment Variables

### Staffing Backend Required Variables

```bash
# Supabase Configuration (Required)
SUPABASE_URL=your-supabase-project-url
SUPABASE_SERVICE_KEY=your-service-role-key

# Optional: JSearch API (fallback for job search)
JSEARCHRAPDKEY=your-jsearch-api-key
```

### Recruitment Backend Required Variables

```bash
# GitHub API (Required)
GITHUB_TOKEN=your-github-personal-access-token

# Hunter.io API (Optional, for email lookup)
HUNTER_API_KEY=your-hunter-api-key
```

## 🚀 Quick Deployment

### Option 1: Using Deployment Scripts (Recommended)

#### Staffing Backend

**Linux/Mac (Bash):**
```bash
cd mcp_server/staffing_backend

# Set environment variables
export SUPABASE_URL="your-supabase-url"
export SUPABASE_SERVICE_KEY="your-service-key"
export JSEARCHRAPDKEY="your-jsearch-key"  # Optional

# Make script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

**Windows (PowerShell):**
```powershell
cd mcp_server/staffing_backend

# Set environment variables
$env:SUPABASE_URL = "your-supabase-url"
$env:SUPABASE_SERVICE_KEY = "your-service-key"
$env:JSEARCHRAPDKEY = "your-jsearch-key"  # Optional

# Run deployment script
.\deploy.ps1
```

#### Recruitment Backend

**Linux/Mac (Bash):**
```bash
cd mcp_server/recruitment_backend

# Set environment variables
export GITHUB_TOKEN="your-github-token"
export HUNTER_API_KEY="your-hunter-key"  # Optional

# Make script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

**Windows (PowerShell):**
```powershell
cd mcp_server/recruitment_backend

# Set environment variables
$env:GITHUB_TOKEN = "your-github-token"
$env:HUNTER_API_KEY = "your-hunter-key"  # Optional

# Run deployment script
.\deploy.ps1
```

### Option 2: Manual Deployment

#### Step 1: Build Locally

**Staffing Backend:**
```bash
cd mcp_server/staffing_backend

# Build local image for testing
docker build -t staffing-backend-local .

# Test locally
docker run -p 8100:8100 \
  -e SUPABASE_URL="..." \
  -e SUPABASE_SERVICE_KEY="..." \
  -e JSEARCHRAPDKEY="..." \
  staffing-backend-local

# Test endpoint
curl http://localhost:8100/mcp
```

**Recruitment Backend:**
```bash
cd mcp_server/recruitment_backend

# Build local image for testing
docker build -t recruitment-backend-local .

# Test locally
docker run -p 8100:8100 \
  -e GITHUB_TOKEN="..." \
  -e HUNTER_API_KEY="..." \
  recruitment-backend-local

# Test endpoint
curl http://localhost:8100/.well-known/agent-card.json
```

#### Step 2: Build and Push to GCR

**Staffing Backend:**
```bash
cd mcp_server/staffing_backend

# Build for GCR
docker build -t gcr.io/baseshare/staffing-backend .

# Authenticate
gcloud auth configure-docker

# Push to GCR
docker push gcr.io/baseshare/staffing-backend
```

**Recruitment Backend:**
```bash
cd mcp_server/recruitment_backend

# Build for GCR
docker build -t gcr.io/baseshare/recruitment-backend .

# Authenticate
gcloud auth configure-docker

# Push to GCR
docker push gcr.io/baseshare/recruitment-backend
```

#### Step 3: Deploy to Cloud Run

**Staffing Backend:**
```bash
# Note: PORT is automatically set by Cloud Run - don't include it in env vars
gcloud run deploy staffing-backend \
  --image gcr.io/baseshare/staffing-backend \
  --region us-central1 \
  --project baseshare \
  --allow-unauthenticated \
  --port 8100 \
  --set-env-vars="SUPABASE_URL=${SUPABASE_URL},SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY},JSEARCHRAPDKEY=${JSEARCHRAPDKEY}" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

**Recruitment Backend:**
```bash
# Note: PORT is automatically set by Cloud Run - don't include it in env vars
gcloud run deploy recruitment-backend \
  --image gcr.io/baseshare/recruitment-backend \
  --region us-central1 \
  --project baseshare \
  --allow-unauthenticated \
  --port 8100 \
  --set-env-vars="GITHUB_TOKEN=${GITHUB_TOKEN},HUNTER_API_KEY=${HUNTER_API_KEY}" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

## 🔍 Verify Deployment

### Get Service URLs

**Staffing Backend:**
```bash
gcloud run services describe staffing-backend \
  --region us-central1 \
  --project baseshare \
  --format='value(status.url)'
```

**Recruitment Backend:**
```bash
gcloud run services describe recruitment-backend \
  --region us-central1 \
  --project baseshare \
  --format='value(status.url)'
```

### Test Endpoints

**Staffing Backend (FastMCP):**
```bash
# MCP endpoint (may return 406 - this is expected for MCP protocol)
curl https://staffing-backend-xyz-uc.a.run.app/mcp
```

**Recruitment Backend (A2A):**
```bash
# Agent card endpoint
curl https://recruitment-backend-xyz-uc.a.run.app/.well-known/agent-card.json
```

## 🔗 Configure ADK Agents

After deployment, update your ADK agent environment variables:

### Staffing Backend
```bash
# For FastMCP, use the /mcp endpoint
STAFFING_MCP_SERVER_URL=https://staffing-backend-xyz-uc.a.run.app/mcp
```

### Recruitment Backend
```bash
# For A2A server, use the base URL (no /mcp path)
RECRUITMENT_MCP_SERVER_URL=https://recruitment-backend-xyz-uc.a.run.app
```

## 📊 Service Details

### Staffing Backend
- **Service Name**: `staffing-backend`
- **Port**: 8100
- **Protocol**: FastMCP (streamable-http)
- **Endpoint**: `/mcp`
- **Tools**: 
  - `search_jobs`
  - `create_candidate_submission`
  - `get_candidate_resume`
  - `get_pipeline_status`

### Recruitment Backend
- **Service Name**: `recruitment-backend`
- **Port**: 8100
- **Protocol**: A2A (Agent-to-Agent) with MCP tools
- **Endpoint**: Base URL (no `/mcp` path)
- **Tools**:
  - `search_candidates_tool`
  - `analyze_portfolio_tool`
  - `find_candidate_emails_tool`
  - `generate_recruitment_report_tool`

## 🛠️ Troubleshooting

### Build Failures

1. **Check Docker is running**
   ```bash
   docker ps
   ```

2. **Check Python dependencies**
   - Staffing: `supabase`, `fastmcp`, `PyPDF2`
   - Recruitment: `google-adk`, `a2a-sdk`, `uvicorn`

3. **Verify requirements.txt exists**
   ```bash
   ls mcp_server/staffing_backend/requirements.txt
   ls mcp_server/recruitment_backend/requirements.txt
   ```

### Deployment Failures

1. **Error: "reserved env names were provided: PORT"**
   - **Cause**: Cloud Run automatically sets the `PORT` environment variable
   - **Solution**: Don't include `PORT` or `HOST` in `--set-env-vars`. The deployment scripts handle this automatically.

2. **Check GCR authentication**
   ```bash
   gcloud auth configure-docker
   ```

3. **Verify project permissions**
   ```bash
   gcloud projects list
   gcloud config set project baseshare
   ```

4. **Check environment variables**
   ```bash
   echo $SUPABASE_URL
   echo $GITHUB_TOKEN
   ```

### Port Already in Use (Local Testing)

If you see "port is already allocated" error during local testing:

**Windows (PowerShell):**
```powershell
# Find what's using port 8100
netstat -ano | findstr :8100

# Stop the process (replace PID with actual process ID)
Stop-Process -Id <PID> -Force

# Or the deployment script will automatically use port 8101 for testing
```

**Linux/Mac:**
```bash
# Find what's using port 8100
lsof -i :8100
# or
netstat -an | grep :8100

# Stop the process
kill <PID>

# Or the deployment script will automatically use port 8101 for testing
```

The deployment scripts now automatically detect port conflicts and use port 8101 for testing if 8100 is busy.

### Runtime Issues

1. **Check Cloud Run logs**
   ```bash
   gcloud run services logs read staffing-backend --region us-central1
   gcloud run services logs read recruitment-backend --region us-central1
   ```

2. **Verify environment variables in Cloud Run**
   ```bash
   gcloud run services describe staffing-backend --region us-central1 --format="value(spec.template.spec.containers[0].env)"
   ```

## 🔄 Update Deployment

To update an existing deployment:

1. **Rebuild and push new image**
   ```bash
   docker build -t gcr.io/baseshare/staffing-backend .
   docker push gcr.io/baseshare/staffing-backend
   ```

2. **Redeploy (Cloud Run will use latest image)**
   ```bash
   gcloud run deploy staffing-backend \
     --image gcr.io/baseshare/staffing-backend \
     --region us-central1
   ```

Or simply use the deployment scripts again - they will update the existing service.

## 📝 Notes

- Both services use port 8100 by default, but Cloud Run handles port mapping automatically
- Staffing Backend uses FastMCP protocol (requires `/mcp` endpoint)
- Recruitment Backend uses A2A protocol (base URL, no `/mcp` path)
- Environment variables can be updated in Cloud Run console or via `gcloud run services update`

