# Google Docs Q&A Bot - Quick Start Guide

Get the Google Docs Q&A bot running in under 10 minutes.

## Prerequisites

- Python 3.10-3.12
- Node.js 18+
- Google Cloud Project
- At least 1 Google Doc to query

## Step 1: Install Dependencies

```bash
make install
```

This installs:
- `uv` (fast Python package manager)
- Python dependencies (ADK, Google API client)
- Node.js dependencies (Next.js, React)

## Step 2: Set Up Google Drive API

### A. Enable APIs

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable drive.googleapis.com
gcloud services enable docs.googleapis.com
```

### B. Create Service Account

```bash
# Create service account docs-qa-bot
gcloud iam service-accounts create docs-qa-bot \
    --display-name="Google Docs QA Bot"

# Create key file
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=docs-qa-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

This creates `service-account-key.json` in your current directory.

### C. Share Your Google Docs

1. Open your Google Doc(s)
2. Click "Share"
3. Add the service account email: `docs-qa-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com`
4. Give it "Viewer" access
5. Click "Send"

**Pro Tip:** Share an entire folder to give access to all docs in that folder.

## Step 3: Configure Environment

Create `app/.env`:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STAGING_BUCKET=YOUR_STAGING_BUCKET

# Google Drive (use your actual path)
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=./service-account-key.json

# Optional: Limit to specific folder
# GOOGLE_DRIVE_FOLDER_ID=your-folder-id

# Model
MODEL=gemini-2.0-flash-exp
AGENT_NAME=google-docs-qa-agent
```

**Quick Copy:**

```bash
cat > app/.env << 'EOF'
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STAGING_BUCKET=YOUR_STAGING_BUCKET
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=./service-account-key.json
MODEL=gemini-2.0-flash-exp
AGENT_NAME=google-docs-qa-agent
EXTRA_PACKAGES=./app
REQUIREMENTS_FILE=.requirements.txt
EOF
```

Replace `YOUR_PROJECT_ID` and `YOUR_STAGING_BUCKET` with your actual values.

## Step 4: Test Google Drive Connection

```bash
# Verify service account can access your docs
.venv/Scripts/python test_docs.py
OR
make test-docs
```

Expected output: JSON with your recent Google Docs.

If you get an error:
- Check service account key path in `.env`
- Verify you shared docs with the service account email
- Ensure Drive and Docs APIs are enabled

## Step 5: Start the Application

```bash
# Start backend + frontend together
make dev
```

Or start separately:

```bash
# Terminal 1: Backend
make dev-backend

# Terminal 2: Frontend  
make dev-frontend
```

## Step 6: Try It Out

Open `http://localhost:3000` in your browser.

### Test Questions

**Start simple:**
```
What documents are available?
```

**Ask about content:**
```
What is [topic from your docs]?
```

**Get a summary:**
```
Summarize the [document name]
```

**Follow-up:**
```
Tell me more about [specific detail]
```

## Verify It's Working

### Backend Logs

You should see in the backend terminal:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Frontend

- Chat UI loads at `localhost:3000`
- Title says "Google Docs Q&A Bot"
- Input placeholder mentions Google Docs

### Activity Timeline

On the right side, you'll see:
- "Tool call: search_google_docs"
- "Tool call: read_google_doc"
- Agent thinking process

### Question Logs

Check `logs/questions.jsonl` - it should contain your questions:

```bash
cat logs/questions.jsonl
```

## Troubleshooting

### "GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY not set"

**Fix:** Create `app/.env` with the service account key path.

### "No documents found"

**Fixes:**
1. Verify docs are shared with service account email
2. Check service account email has "Viewer" access
3. Try: "What documents are available?" first

### "HttpError 403: Insufficient permissions"

**Fix:** Share the document with the service account email (step 2C).

### "HttpError 404: File not found"

**Fix:** Document ID is wrong, or service account doesn't have access.

### Backend won't start

**Fix:** Port 8000 might be in use.

```bash
# Kill process on port 8000
npx kill-port 8000 --yes

# Then restart
make dev-backend
```

### Frontend errors

**Fix:** Make sure backend is running first.

```bash
# Check backend health
curl http://localhost:8000/health
```

## Next Steps

### Add More Documents

Share more Google Docs with the service account to expand the bot's knowledge base.

### Limit to Specific Folder

Get folder ID from Drive URL:
```
https://drive.google.com/drive/folders/1abc123xyz456
                                        ^^^^^^^^^^^^^^^^
```

Add to `app/.env`:
```bash
GOOGLE_DRIVE_FOLDER_ID=1abc123xyz456
```

### Deploy to Production

See `ADK_DEPLOYMENT_GUIDE.md` for deploying to:
- Vertex AI Agent Engine (backend)
- Vercel (frontend)

### View Question Analytics

```bash
# See recent questions
uv run python -c "
from app.utils.question_logger import get_question_logger
logger = get_question_logger()
stats = logger.get_question_stats()
print(f'Total questions: {stats[\"total_questions\"]}')
print(f'Most accessed docs: {stats[\"most_accessed_documents\"][:3]}')
"
```

### Run the Demo

See `GOOGLE_DOCS_DEMO.md` for a polished 5-minute demo script.

## Common Use Cases

### Internal Documentation Q&A
- Company policies
- Technical documentation  
- Onboarding guides
- SOPs and runbooks

### Knowledge Management
- FAQ automation
- Documentation gap analysis
- Question trend tracking

### Customer Support
- Product documentation
- Troubleshooting guides
- Feature documentation

## Support

For detailed setup: `GOOGLE_DRIVE_SETUP.md`  
For demo script: `GOOGLE_DOCS_DEMO.md`  
For deployment: `ADK_DEPLOYMENT_GUIDE.md`

---

**You're all set!** Ask the bot questions about your Google Docs. 🚀

