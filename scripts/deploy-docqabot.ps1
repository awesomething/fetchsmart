# Deploy Doc Q&A Bot to Agent Engine
# Usage: .\deploy-docqabot.ps1

Write-Host "🚀 Deploying Doc Q&A Bot..." -ForegroundColor Cyan

$AGENT_NAME="docqabot"
make deploy-adk

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Doc Q&A Bot deployed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Deployment failed. Check logs above." -ForegroundColor Red
}

