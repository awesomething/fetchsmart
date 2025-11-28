# Deployment script for Recruitment Backend MCP Server (PowerShell)
# Builds locally, tests, then deploys to Cloud Run

$ErrorActionPreference = "Stop"

$PROJECT_ID = "baseshare"
$REGION = "us-central1"
$SERVICE_NAME = "recruitment-backend"
$IMAGE_NAME = "gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
$LOCAL_IMAGE = "${SERVICE_NAME}-local"

Write-Host "🚀 Deploying Recruitment Backend MCP Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host "Image: $IMAGE_NAME"
Write-Host ""

# Check required environment variables
if (-not $env:GITHUB_TOKEN) {
    Write-Host "⚠️  WARNING: GITHUB_TOKEN not set" -ForegroundColor Yellow
    Write-Host "   This will need to be set in Cloud Run deployment"
}

# Step 1: Build locally
Write-Host "📦 Step 1: Building Docker image locally..." -ForegroundColor Green
docker build -t $LOCAL_IMAGE .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Local build successful!" -ForegroundColor Green
Write-Host ""

# Step 2: Test locally (optional)
$test = Read-Host "🧪 Test locally before deploying? (y/n)"
if ($test -eq "y" -or $test -eq "Y") {
    # Check if port 8100 is in use
    $portInUse = Get-NetTCPConnection -LocalPort 8100 -ErrorAction SilentlyContinue
    $testPort = 8100
    
    if ($portInUse) {
        Write-Host "⚠️  Port 8100 is already in use" -ForegroundColor Yellow
        Write-Host "   Using port 8101 for testing instead" -ForegroundColor Yellow
        $testPort = 8101
    }
    
    Write-Host "🧪 Starting local container for testing..." -ForegroundColor Yellow
    Write-Host "   Access at: http://localhost:$testPort"
    Write-Host "   Agent Card: http://localhost:$testPort/.well-known/agent-card.json"
    Write-Host "   Press Ctrl+C to stop and continue deployment"
    Write-Host ""
    
    $containerId = $null
    try {
        $containerId = docker run -d -p "${testPort}:8100" `
            -e GITHUB_TOKEN="$env:GITHUB_TOKEN" `
            -e HUNTER_API_KEY="$env:HUNTER_API_KEY" `
            -e PORT=8100 `
            -e HOST=0.0.0.0 `
            $LOCAL_IMAGE
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to start container" -ForegroundColor Red
            Write-Host "   Skipping local test..." -ForegroundColor Yellow
        } else {
            Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            # Check if container is still running
            $containerRunning = docker ps --filter "id=$containerId" --format "{{.ID}}" 2>$null
            if ($containerRunning) {
                Write-Host "✅ Container is running" -ForegroundColor Green
                
                # Test endpoint
                Write-Host "Testing endpoint..."
                try {
                    $response = Invoke-WebRequest -Uri "http://localhost:$testPort/.well-known/agent-card.json" -UseBasicParsing -TimeoutSec 5
                    Write-Host "✅ Endpoint responding (Status: $($response.StatusCode))" -ForegroundColor Green
                    Write-Host $response.Content.Substring(0, [Math]::Min(200, $response.Content.Length))
                } catch {
                    Write-Host "⚠️  Endpoint test failed: $($_.Exception.Message)" -ForegroundColor Yellow
                }
            } else {
                Write-Host "⚠️  Container stopped unexpectedly" -ForegroundColor Yellow
                Write-Host "   Check logs: docker logs $containerId" -ForegroundColor Yellow
            }
            
            Read-Host "Press Enter to stop container and continue"
            
            # Clean up container
            if ($containerId) {
                docker stop $containerId 2>$null
                docker rm $containerId 2>$null
            }
        }
    } catch {
        Write-Host "⚠️  Local test failed: $_" -ForegroundColor Yellow
        Write-Host "   Continuing with deployment..." -ForegroundColor Yellow
        if ($containerId) {
            docker stop $containerId 2>$null
            docker rm $containerId 2>$null
        }
    }
}

# Step 3: Build for GCR
Write-Host ""
Write-Host "📦 Step 2: Building image for Google Container Registry..." -ForegroundColor Green
docker build -t $IMAGE_NAME .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

# Step 4: Authenticate with GCR
Write-Host ""
Write-Host "🔐 Step 3: Authenticating Docker with GCR..." -ForegroundColor Green
gcloud auth configure-docker

# Step 5: Push to GCR
Write-Host ""
Write-Host "📤 Step 4: Pushing image to GCR..." -ForegroundColor Green
docker push $IMAGE_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image pushed successfully!" -ForegroundColor Green
Write-Host ""

# Step 6: Deploy to Cloud Run
Write-Host "🚀 Step 5: Deploying to Cloud Run..." -ForegroundColor Green
# Note: PORT is automatically set by Cloud Run, don't include it in env vars
$envVars = "GITHUB_TOKEN=$env:GITHUB_TOKEN,HUNTER_API_KEY=$env:HUNTER_API_KEY"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --region $REGION `
    --project $PROJECT_ID `
    --allow-unauthenticated `
    --port 8100 `
    --set-env-vars=$envVars `
    --memory 512Mi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cloud Run deployment failed!" -ForegroundColor Red
    exit 1
}

# Step 7: Get service URL
Write-Host ""
Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Service URL:" -ForegroundColor Cyan
$SERVICE_URL = gcloud run services describe $SERVICE_NAME `
    --region $REGION `
    --project $PROJECT_ID `
    --format='value(status.url)'

Write-Host "   $SERVICE_URL"
Write-Host ""
Write-Host "🔗 A2A Agent Card:" -ForegroundColor Cyan
Write-Host "   $SERVICE_URL/.well-known/agent-card.json"
Write-Host ""
Write-Host "💡 Set this in your ADK agent environment:" -ForegroundColor Yellow
Write-Host "   RECRUITMENT_MCP_SERVER_URL=$SERVICE_URL"
Write-Host ""

