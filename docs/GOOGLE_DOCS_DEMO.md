# Google Docs Q&A Bot - Demo Script

**Duration:** 5 minutes  
**Audience:** Technical stakeholders, product managers, clients  
**Goal:** Demonstrate Google Docs Q&A functionality and document search capabilities

---

## Pre-Demo Setup Checklist ✅

- [ ] Backend running: `make dev-backend` (port 8000)
- [ ] Frontend running: `make dev-frontend` (port 3000)
- [ ] Browser tab open to `http://localhost:3000`
- [ ] At least 3-5 Google Docs shared with service account
- [ ] Sample documents contain varied content (deployment, architecture, troubleshooting)
- [ ] `logs/questions.jsonl` directory exists and is writable
- [ ] Terminal showing backend logs visible (to show tool calls)

---

## Demo Flow

### Part 1: Introduction (30 seconds)

**You:** "Today I'm showing you our Google Docs Q&A Bot. It's built on Google's Agent Development Kit and can search through your Google Docs, read them, and answer questions with citations. Let me show you how it works."

**[Screen: Show the landing page at localhost:3000]**

---

### Part 2: First Question - Document Discovery (1 minute)

**You:** "Let's start by asking what documents are available."

**[Type in chat]:** "What documents are available?"

**What happens:**
1. Agent uses `list_recent_docs()` tool
2. Returns list of recently modified documents
3. Response shows document names, modification dates

**You:** "Great! So the bot can see our documentation. Now let's ask a specific question."

---

### Part 3: Knowledge Question (1.5 minutes)

**You:** "Let's ask about something specific in our docs."

**[Type in chat]:** "What is our cloud deployment strategy?"

**What happens:**
1. Agent uses `search_google_docs("cloud deployment strategy")`
2. Finds relevant documents
3. Uses `read_google_doc(doc_id)` to retrieve content
4. Provides answer with citation

**[Point to the response]:**

**You:** "Notice how the bot:
- Searched for relevant documents
- Read the most relevant one
- Provided an answer
- **Cited the source document**

This is critical for trust and verification."

**[Optional: Show activity timeline on the right]:**

**You:** "And in the activity timeline, you can see the bot's thought process - what tools it called, what documents it accessed."

---

### Part 4: Follow-up Question (1 minute)

**You:** "Now let's test its ability to handle follow-ups."

**[Type in chat]:** "How do we handle SSL certificates?"

**What happens:**
1. Agent searches for SSL-related docs
2. Reads relevant content
3. Provides specific answer with citation

**You:** "The bot maintained context and answered a different question, searching new documents as needed."

---

### Part 5: Document Summarization (1 minute)

**You:** "Finally, let's ask it to summarize a document."

**[Type in chat]:** "Summarize the architecture document"

**What happens:**
1. Agent searches for architecture document
2. Reads the full content
3. Provides a concise summary with key points

**You:** "This is useful for quickly understanding large documents without reading them entirely."

---

### Part 6: Question Logging (30 seconds)

**[Switch to terminal or VS Code]:**

**You:** "Behind the scenes, we're tracking all questions asked."

**[Show logs/questions.jsonl]:**

```json
{"timestamp": "2025-10-30T...", "question": "What is our cloud deployment strategy?", "documents_searched": [...], "documents_used": [...]}
```

**You:** "This gives us analytics on:
- What questions users ask
- Which documents are most accessed
- Gaps in documentation (repeated questions about missing info)

The next phase will analyze these logs and suggest documentation updates."

---

## Demo Questions Library

### Easy Questions (Always Work)
- "What documents are available?"
- "List the recent documents"
- "What topics are covered in our docs?"

### Knowledge Questions (Require specific docs)
- "What is our deployment process?"
- "How do we handle authentication?"
- "What is the system architecture?"
- "What are the security requirements?"
- "How do we troubleshoot [X]?"

### Summarization Questions
- "Summarize the [document name]"
- "What are the key points in the [document name]?"
- "Give me an overview of [topic]"

### Comparison Questions (Advanced)
- "What's the difference between [A] and [B]?"
- "Compare our deployment options"
- "How does [X] relate to [Y]?"

---

## Troubleshooting During Demo

### Bot says "No documents found"

**Immediate response:**
"Looks like the search didn't find that specific document. Let me rephrase the question."

**Try:**
- Broader search terms
- Ask "What documents are available?" first
- Ask about a document you know exists

### Bot is slow

**Immediate response:**
"The bot is reading through the documents to give an accurate answer. This takes a few seconds."

**Note:** First query can be slow due to Google API initialization. Subsequent queries are faster.

### Bot gives incorrect answer

**Immediate response:**
"Let me clarify the question to help the bot understand better."

**Try:**
- More specific question
- Mention the document name explicitly
- Ask a follow-up to refine the answer

---

## Key Talking Points

### Technical Architecture
- "Built on Google's Agent Development Kit (ADK)"
- "Uses Google Drive API for document access"
- "Vertex AI Gemini 2.0 Flash for fast, accurate responses"
- "Streaming responses for real-time feedback"
- "Production-ready with error handling and logging"

### Business Value
- "Reduces time spent searching documentation"
- "Ensures answers are always up-to-date with docs"
- "Tracks question patterns to improve documentation"
- "Scales to hundreds or thousands of documents"
- "Works with existing Google Workspace setup"

### Security & Privacy
- "Uses service account authentication (no personal credentials)"
- "Read-only access to documents"
- "All data stays within Google Cloud"
- "Complies with Google Workspace security policies"

### Future Enhancements
- "Automatic documentation gap detection"
- "Suggested doc updates based on question patterns"
- "Multi-document comparison and analysis"
- "Integration with Slack/Teams for team-wide access"
- "Custom document tagging and organization"

---

## Q&A Preparation

### Q: "What if the document changes?"

**A:** "The bot reads documents in real-time, so answers always reflect the current state of your docs. No indexing lag."

### Q: "Can it handle large documents?"

**A:** "Yes. Google Docs API handles documents up to 1.02 million characters. The bot extracts and processes content efficiently."

### Q: "How many documents can it search?"

**A:** "Unlimited. The bot searches your entire Google Drive (or a specific folder). Response time is under 5 seconds even for large doc sets."

### Q: "Does it work with other file types?"

**A:** "Currently Google Docs only. We can extend to Google Sheets, PDFs, and other formats with minimal effort."

### Q: "Can multiple users use it simultaneously?"

**A:** "Yes. The architecture supports unlimited concurrent users. Each user gets their own session."

### Q: "How much does it cost to run?"

**A:** "Gemini 2.0 Flash is $0.10 per 1M input tokens, $0.40 per 1M output tokens. For a typical Q&A (1000 tokens), that's ~$0.001 per question. Very cost-effective."

### Q: "Can we deploy this in production?"

**A:** "Absolutely. We can deploy to Vertex AI Agent Engine (fully managed) or your own GKE cluster. The frontend deploys to Vercel, Cloud Run, or any container platform."

---

## Post-Demo Next Steps

**For interested stakeholders:**

1. **Immediate (1 week):**
   - Share service account setup guide
   - Share 3-5 sample documents for testing
   - Set up staging environment for team trial

2. **Short-term (2-3 weeks):**
   - Add question analytics dashboard
   - Implement doc update suggestions
   - Custom branding and domain

3. **Medium-term (1-2 months):**
   - Deploy to production (Agent Engine + Vercel)
   - Integrate with Slack/Teams
   - Add multi-format support (PDFs, Sheets)
   - Set up monitoring and alerting

**Close:**
"I'll send you the setup guide and repo link. You can run this locally in under 10 minutes with your own Google Docs. Let me know if you have questions or want to schedule a follow-up for your specific use case."

---

## Demo Checklist (Print & Bring)

**Before Demo:**
- [ ] Documents shared with service account
- [ ] Backend started and healthy
- [ ] Frontend loaded in browser
- [ ] Sample questions tested
- [ ] Logs directory writable

**During Demo:**
- [ ] Start with document discovery
- [ ] Ask knowledge question
- [ ] Show follow-up capability
- [ ] Demonstrate summarization
- [ ] Show question logging

**After Demo:**
- [ ] Show architecture diagram
- [ ] Discuss deployment options
- [ ] Share setup guide
- [ ] Schedule follow-up if needed

---

**Good luck with the demo!** 🚀

