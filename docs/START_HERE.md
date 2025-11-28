# 🚀 Multi-Agent AI Assistant - START HERE

## What Is This?

A production-ready **multi-agent system** that helps with:
1. **Goal Planning**: Break down goals into actionable tasks
2. **Document Q&A**: Search and answer questions about Google Docs

The system automatically routes your request to the right specialist agent!

**Built with:** Google ADK Multi-Agent Architecture + Next.js + Vertex AI Gemini

**Time to demo:** 10-15 minutes

**Pattern:** Follows [Google's ADK best practices](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk)

---

## 🎯 Quick Navigation

Choose your path:

### 👉 **Want to get started ASAP?**
→ Read: [`QUICKSTART_GOOGLE_DOCS.md`](QUICKSTART_GOOGLE_DOCS.md)  
→ 10 minutes from zero to running chatbot

### 👉 **Need detailed Google Drive setup?**
→ Read: [`GOOGLE_DRIVE_SETUP.md`](GOOGLE_DRIVE_SETUP.md)  
→ Step-by-step service account creation and API enablement

### 👉 **Preparing for a demo?**
→ Read: [`GOOGLE_DOCS_DEMO.md`](GOOGLE_DOCS_DEMO.md)  
→ 5-minute demo script with Q&A preparation

### 👉 **Want technical details?**
→ Read: [`MULTI_AGENT_ARCHITECTURE.md`](MULTI_AGENT_ARCHITECTURE.md)  
→ Complete multi-agent architecture guide

→ Read: [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)  
→ Google Docs Q&A implementation details

### 👉 **Need a project summary?**
→ Read: [`POC_DELIVERABLES.md`](POC_DELIVERABLES.md)  
→ Complete deliverables and acceptance criteria

---

## ⚡ Super Quick Start

```bash
# 1. Install everything
make install

# 2. Set up Google Drive (follow GOOGLE_DRIVE_SETUP.md)
#    - Enable Drive & Docs APIs
#    - Create service account
#    - Share your docs with service account

# 3. Create app/.env
cat > app/.env << 'EOF'
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STAGING_BUCKET=YOUR_BUCKET
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=./service-account-key.json
MODEL=gemini-2.0-flash-exp
AGENT_NAME=google-docs-qa-agent
EXTRA_PACKAGES=./app
REQUIREMENTS_FILE=.requirements.txt
EOF

# 4. Test connection
uv run python test_google_drive.py

# 5. Start the app
make dev

# 6. Open http://localhost:3000 and ask questions!
```

---

## 📋 What You Need

### Prerequisites
- Python 3.10-3.12
- Node.js 18+
- Google Cloud Project
- At least 1 Google Doc to query

### Google Cloud Setup
1. Enable Google Drive API
2. Enable Google Docs API
3. Create service account
4. Download service account key
5. Share your Google Docs with service account email

**Detailed instructions:** [`GOOGLE_DRIVE_SETUP.md`](GOOGLE_DRIVE_SETUP.md)

---

## 🎬 Demo in 5 Minutes

Once setup is complete:

1. **Start:** `make dev`
2. **Open:** `http://localhost:3000`
3. **Ask:** "What documents are available?"
4. **Ask:** "What is [topic in your docs]?"
5. **Show:** Activity timeline (tool calls) and question logs

**Full demo script:** [`GOOGLE_DOCS_DEMO.md`](GOOGLE_DOCS_DEMO.md)

---

## 🔍 Test Your Setup

Run this before demoing:

```bash
uv run python test_google_drive.py
```

This tests:
- ✅ Service account authentication
- ✅ Google Drive API connection
- ✅ Document access
- ✅ Search functionality

---

## 📚 Documentation Index

| File | Purpose | When to Read |
|------|---------|-------------|
| **[START_HERE.md](START_HERE.md)** | Overview & navigation | Right now! |
| **[QUICKSTART_GOOGLE_DOCS.md](QUICKSTART_GOOGLE_DOCS.md)** | 10-min setup guide | First time setup |
| **[GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)** | Detailed API setup | Need step-by-step |
| **[GOOGLE_DOCS_DEMO.md](GOOGLE_DOCS_DEMO.md)** | 5-min demo script | Before demoing |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | Technical details | For developers |
| **[POC_DELIVERABLES.md](POC_DELIVERABLES.md)** | Project overview | For stakeholders |
| **[README.md](README.md)** | Original ADK template docs | For context |

---

## 🎯 Example Questions to Ask

### Planning Queries (🟢 Planning Agent)
- "Plan a marketing campaign for a new product"
- "Break down: Build a mobile app"
- "Create a project timeline for data migration"
- "How do I set up a CI/CD pipeline?"

### Q&A Queries (🔵 Q&A Agent)
- "What documents are available?"
- "What is our deployment process?"
- "Summarize the architecture document"
- "How do we handle SSL certificates?"

**The system automatically routes to the right agent!**

---

## ⚠️ Common Issues & Fixes

### "No documents found"
**Fix:** Share your Google Docs with the service account email  
**Email:** `your-service-account@YOUR_PROJECT.iam.gserviceaccount.com`

### "HttpError 403: Insufficient permissions"
**Fix:** Give service account "Viewer" access to documents

### "Backend won't start (port 8000 in use)"
**Fix:** `npx kill-port 8000 --yes` then restart

### "Service account key not found"
**Fix:** Verify `GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY` path in `app/.env`

**Full troubleshooting:** [`QUICKSTART_GOOGLE_DOCS.md`](QUICKSTART_GOOGLE_DOCS.md#troubleshooting)

---

## 🏗️ Architecture Overview

```
User Question
     ↓
Frontend (Next.js @ localhost:3000)
     ↓
API Route (SSE Streaming)
     ↓
ADK Agent (app/agent.py)
     ↓
Google Drive Tools:
  • search_google_docs()
  • read_google_doc()
  • list_recent_docs()
     ↓
Google Drive/Docs API
     ↓
Your Documents
     ↓
Agent Response (with citations)
     ↓
Question Logger (logs/questions.jsonl)
```

---

## 💰 Cost Estimate

**Gemini 2.0 Flash Pricing:**
- Input: $0.10 per 1M tokens
- Output: $0.40 per 1M tokens

**Typical Q&A:**
- ~1,000 tokens per question
- **Cost: ~$0.001 per question**

**100 questions/day = $3/month**

---

## 🚀 Production Deployment

This POC is production-ready! Deploy to:

### Backend Options
1. **Vertex AI Agent Engine** (recommended)
   - Fully managed, autoscaling
   - `make deploy-adk`
   
2. **Google Kubernetes Engine (GKE)**
   - More control, custom config
   - Deploy as container

### Frontend Options
1. **Vercel** (recommended)
   - One-click deploy
   - Automatic SSL

2. **Cloud Run**
   - Google Cloud native
   - Pay per request

**Deployment guide:** [`ADK_DEPLOYMENT_GUIDE.md`](ADK_DEPLOYMENT_GUIDE.md) (original template docs)

---

## ✅ Success Checklist

Before considering the POC complete:

- [ ] Backend starts without errors
- [ ] Frontend loads at `localhost:3000`
- [ ] Test script passes: `uv run python test_google_drive.py`
- [ ] "What documents are available?" returns your docs
- [ ] Questions about doc content get cited answers
- [ ] Activity timeline shows tool calls
- [ ] `logs/questions.jsonl` is populated
- [ ] Demo script tested with sample questions

---

## 🎓 What's Next?

### Immediate (Week 1)
- ✅ Core functionality (COMPLETE)
- ✅ Documentation (COMPLETE)
- ✅ Demo readiness (COMPLETE)

### Short Term (Week 2-3)
- [ ] Question analytics dashboard
- [ ] Doc update suggestions
- [ ] Multi-format support (PDFs)

### Medium Term (Month 2)
- [ ] Slack/Teams integration
- [ ] Semantic search (embeddings)
- [ ] Multi-document reasoning
- [ ] Custom branding

---

## 💬 Questions?

1. **Setup issues?** → [`QUICKSTART_GOOGLE_DOCS.md`](QUICKSTART_GOOGLE_DOCS.md)
2. **Demo prep?** → [`GOOGLE_DOCS_DEMO.md`](GOOGLE_DOCS_DEMO.md)
3. **Technical details?** → [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)
4. **Project overview?** → [`POC_DELIVERABLES.md`](POC_DELIVERABLES.md)

---

## 🎉 You're Ready!

**Next step:** Open [`QUICKSTART_GOOGLE_DOCS.md`](QUICKSTART_GOOGLE_DOCS.md) and follow the 10-minute setup.

**Questions?** All documentation files are in the root directory.

**Good luck with your demo!** 🚀

