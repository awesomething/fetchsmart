#!/bin/bash
# Deployment script for Recruitment Backend MCP Server
# Builds locally, tests, then deploys to Cloud Run

set -e  # Exit on error

PROJECT_ID="baseshare"
REGION="us-central1"
SERVICE_NAME="recruitment-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
LOCAL_IMAGE="${SERVICE_NAME}-local"

echo "🚀 Deploying Recruitment Backend MCP Server"
echo "=========================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_NAME}"
echo ""

# Check required environment variables
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  WARNING: GITHUB_TOKEN not set"
    echo "   This will need to be set in Cloud Run deployment"
fi

# Step 1: Build locally
echo "📦 Step 1: Building Docker image locally..."
docker build -t ${LOCAL_IMAGE} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Local build successful!"
echo ""

# Step 2: Test locally (optional)
read -p "🧪 Test locally before deploying? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if port 8100 is in use
    TEST_PORT=8100
    if lsof -Pi :8100 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep -q ":8100.*LISTEN"; then
        echo "⚠️  Port 8100 is already in use"
        echo "   Using port 8101 for testing instead"
        TEST_PORT=8101
    fi
    
    echo "🧪 Starting local container for testing..."
    echo "   Access at: http://localhost:${TEST_PORT}"
    echo "   Agent Card: http://localhost:${TEST_PORT}/.well-known/agent-card.json"
    echo "   Press Ctrl+C to stop and continue deployment"
    echo ""
    
    CONTAINER_ID=$(docker run -d -p ${TEST_PORT}:8100 \
        -e GITHUB_TOKEN="${GITHUB_TOKEN}" \
        -e HUNTER_API_KEY="${HUNTER_API_KEY}" \
        -e PORT=8100 \
        -e HOST=0.0.0.0 \
        ${LOCAL_IMAGE} 2>/dev/null)
    
    if [ -z "$CONTAINER_ID" ]; then
        echo "❌ Failed to start container"
        echo "   Skipping local test..."
    else
        echo "⏳ Waiting for server to start..."
        sleep 5
        
        # Check if container is still running
        if docker ps --filter "id=${CONTAINER_ID}" --format "{{.ID}}" | grep -q .; then
            echo "✅ Container is running"
            
            # Test endpoint
            echo "Testing endpoint..."
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:${TEST_PORT}/.well-known/agent-card.json || echo "000")
            if [ "$HTTP_CODE" = "200" ]; then
                echo "✅ Endpoint responding (Status: $HTTP_CODE)"
                curl -s --max-time 5 http://localhost:${TEST_PORT}/.well-known/agent-card.json | head -20
            else
                echo "⚠️  Endpoint test failed (HTTP: $HTTP_CODE)"
            fi
        else
            echo "⚠️  Container stopped unexpectedly"
            echo "   Check logs: docker logs ${CONTAINER_ID}"
        fi
        
        read -p "Press Enter to stop container and continue..."
        docker stop ${CONTAINER_ID} 2>/dev/null || true
        docker rm ${CONTAINER_ID} 2>/dev/null || true
    fi
fi

# Step 3: Build for GCR
echo ""
echo "📦 Step 2: Building image for Google Container Registry..."
docker build -t ${IMAGE_NAME} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Step 4: Authenticate with GCR
echo ""
echo "🔐 Step 3: Authenticating Docker with GCR..."
gcloud auth configure-docker

# Step 5: Push to GCR
echo ""
echo "📤 Step 4: Pushing image to GCR..."
docker push ${IMAGE_NAME}

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed!"
    exit 1
fi

echo "✅ Image pushed successfully!"
echo ""

# Step 6: Deploy to Cloud Run
echo "🚀 Step 5: Deploying to Cloud Run..."
# Note: PORT is automatically set by Cloud Run, don't include it in env vars
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --allow-unauthenticated \
    --port 8100 \
    --set-env-vars="GITHUB_TOKEN=${GITHUB_TOKEN},HUNTER_API_KEY=${HUNTER_API_KEY}" \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10

if [ $? -ne 0 ]; then
    echo "❌ Cloud Run deployment failed!"
    exit 1
fi

# Step 7: Get service URL
echo ""
echo "✅ Deployment successful!"
echo ""
echo "📋 Service URL:"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --format='value(status.url)')

echo "   ${SERVICE_URL}"
echo ""
echo "🔗 A2A Agent Card:"
echo "   ${SERVICE_URL}/.well-known/agent-card.json"
echo ""
echo "💡 Set this in your ADK agent environment:"
echo "   RECRUITMENT_MCP_SERVER_URL=${SERVICE_URL}"
echo ""

