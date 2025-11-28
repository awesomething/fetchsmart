# Google Drive API Setup Guide

This guide explains how to set up Google Drive API access for the Google Docs Q&A chatbot.

## Prerequisites

1. A Google Cloud Project with billing enabled
2. Access to create service accounts
3. Google Docs you want the bot to access

## Setup Steps

### 1. Enable Required APIs

In your Google Cloud Console, enable these APIs:
- Google Drive API
- Google Docs API

```bash
gcloud services enable drive.googleapis.com
gcloud services enable docs.googleapis.com
```

### 2. Create a Service Account

```bash
gcloud iam service-accounts create docs-qa-bot \
    --display-name="Google Docs Q&A Bot" \
    --description="Service account for reading Google Docs"
```

### 3. Create and Download Service Account Key

```bash
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=docs-qa-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

This creates a `service-account-key.json` file. **Keep this file secure!**

### 4. Share Google Docs with the Service Account

For the bot to access your Google Docs, you must share them with the service account email:

1. Open the Google Doc(s) you want the bot to access
2. Click "Share"
3. Add the service account email: `docs-qa-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com`
4. Give it "Viewer" access
5. Click "Send"

**Pro Tip:** Share an entire Google Drive folder with the service account to give it access to all docs in that folder.

### 5. Configure Environment Variables

Create `app/.env` file with the following:

```bash
# Google Cloud Configuration (existing)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STAGING_BUCKET=my-staging-bucket

# Model Configuration (existing)
MODEL=gemini-2.0-flash-exp
AGENT_NAME=google-docs-qa-agent

# Google Drive Configuration (NEW)
# Option 1: Path to service account JSON file
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=./service-account-key.json

# Option 2: JSON content as environment variable (for deployment)
# GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY='{"type": "service_account", "project_id": "...", ...}'

# Optional: Limit search to a specific folder (get ID from Drive URL)
# GOOGLE_DRIVE_FOLDER_ID=1abc123xyz456

# Deployment Configuration (existing)
EXTRA_PACKAGES=./app
REQUIREMENTS_FILE=.requirements.txt
```

### 6. Get Folder ID (Optional)

If you want to limit the bot to a specific folder:

1. Open the folder in Google Drive
2. Look at the URL: `https://drive.google.com/drive/folders/1abc123xyz456`
3. The folder ID is the part after `/folders/`: `1abc123xyz456`
4. Set `GOOGLE_DRIVE_FOLDER_ID=1abc123xyz456` in your `.env` file

## Verification

Test the setup:

```bash
# Install dependencies
uv sync

# Start the backend
make dev-backend
```

In another terminal:

```bash
# Test the Google Drive tools
uv run python -c "
from app.tools.google_drive import list_recent_docs
print(list_recent_docs())
"
```

You should see a JSON response with your recent Google Docs.

## Security Best Practices

1. **Never commit service account keys to Git**
   - Add `service-account-key.json` to `.gitignore`
   - Add `app/.env` to `.gitignore` (should already be there)

2. **Use least privilege access**
   - Only share necessary documents with the service account
   - Use "Viewer" access, not "Editor"

3. **For production deployment**
   - Store service account key in Secret Manager
   - Use Workload Identity if deploying to GKE
   - Rotate keys periodically

## Troubleshooting

### Error: "GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY environment variable not set"

**Solution:** Make sure you've created `app/.env` and set the variable.

### Error: "No documents found"

**Solutions:**
1. Verify you've shared documents with the service account email
2. Check that the service account email has "Viewer" access
3. If using `GOOGLE_DRIVE_FOLDER_ID`, verify the folder ID is correct

### Error: "HttpError 403: insufficientFilePermissions"

**Solution:** The service account doesn't have access to the document. Share it with the service account email.

### Error: "HttpError 404: File not found"

**Solution:** The document ID is incorrect, or the document was deleted, or the service account doesn't have access.

## Next Steps

Once setup is complete:
1. Start the backend: `make dev-backend`
2. Start the frontend: `make dev-frontend`
3. Open `http://localhost:3000`
4. Ask a question about your docs!

Example questions:
- "What documents are available?"
- "What is our deployment process?"
- "Summarize the architecture document"

