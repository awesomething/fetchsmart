# Generic Agent Deployment Script
# Usage: .\scripts\deploy-agent.ps1 -AgentName "myagent" -Bucket "myagent-staging"

param(
    [Parameter(Mandatory=$true)]
    [string]$AgentName,
    
    [Parameter(Mandatory=$false)]
    [string]$Bucket = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Project = "baseshare",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "us-central1"
)

# Set bucket to agent name + staging if not provided
if ([string]::IsNullOrEmpty($Bucket)) {
    $Bucket = "$AgentName-staging"
}

Write-Host "🚀 Deploying Agent: $AgentName" -ForegroundColor Cyan
Write-Host "📦 Bucket: gs://$Bucket" -ForegroundColor Gray
Write-Host "📍 Project: $Project" -ForegroundColor Gray
Write-Host "🌍 Location: $Location" -ForegroundColor Gray
Write-Host ""

# Set environment variables
$env:AGENT_NAME = $AgentName
$env:GOOGLE_CLOUD_STAGING_BUCKET = $Bucket
$env:GOOGLE_CLOUD_PROJECT = $Project
$env:GOOGLE_CLOUD_LOCATION = $Location

# Deploy
make deploy-adk

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Agent '$AgentName' deployed successfully!" -ForegroundColor Green
    Write-Host "🔗 View in console: https://console.cloud.google.com/vertex-ai/agent-builder" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed. Check logs above." -ForegroundColor Red
    exit 1
}

