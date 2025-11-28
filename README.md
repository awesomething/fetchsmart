# Multi-Agent Recruitment System

Production-ready fullstack application demonstrating a Python ADK backend with a modern Next.js frontend, featuring streaming responses, intelligent agent routing, mcp servers and deployment paths to Vertex AI Agent Engine and Vercel.

This repo contains:

- **Backend**: Python app using Google ADK with **multi-agent architecture** (6 specialized agents)
- **Frontend**: Next.js app with chat UI, candidate grid display, activity timeline, and SSE streaming
- **Agents**: 6 specialized agents coordinated by a root agent:
  - **Planning Agent** - Recruiter-focused goal planning and task decomposition
  - **Q&A Agent** - Google Docs search and document Q&A
  - **Recruiter Orchestrator** - Candidate search, GitHub sourcing, pipeline metrics, email lookup
  - **Recruiter Email Pipeline** - Personalized outreach email generation and refinement (4 sub-agents)
  - **Staffing Recruiter Orchestrator** - Job search, candidate matching, submissions
  - **Staffing Employer Orchestrator** - Candidate review, hiring pipeline
- **MCP Servers**: Recruitment and Staffing backends providing tools for candidate sourcing, email lookup, job search, and hiring pipeline management
- **Coordinator**: Root agent with smart routing that automatically delegates to the right specialist
- **Make targets**: Scripts for local development, testing, and deployment

**Multi-Agent Pattern:** Follows [Google's ADK best practices](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk) for building specialized agent teams instead of monolithic "super agents".

## Quickstart

Prerequisites:

- Python 3.10–3.12
- Node.js 18+ (recommended: LTS)
- uv (installed automatically by Makefile if missing)
- Google Cloud SDK for cloud deployment

Setup and run locally (backend + frontend):

```bash
make install
cp app/.env.example app/.env  # if present, otherwise see Backend env below
make dev
```

By default the frontend runs at `http://localhost:3000` and proxies chat requests to the local ADK backend at `http://127.0.0.1:8000` via `nextjs/src/app/api/run_sse/route.ts`.

## Features

### Multi-Agent System
- **6 Specialized Agents** coordinated by intelligent root agent
- **Smart Routing** - Automatically detects intent and routes to the right specialist
- **Explicit Mode Override** - UI can force routing to specific agents via `[MODE:XXX]` directives
- **Recruiter-Focused Planning** - Goal decomposition tailored for hiring workflows
- **Document Q&A** - Google Docs search with cited answers
- **Candidate Sourcing** - GitHub profile search with intelligent matching
- **Email Generation** - Personalized outreach emails (75-125 words) with refinement pipeline
- **Staffing Workflows** - Job search, candidate matching, and employer review workflows

### Frontend Features
- **Chat UI** with streaming responses and real-time updates
- **Candidate Grid** - Beautiful card-based display of candidate profiles
- **Smart JSON Collapsing** - Large JSON responses automatically collapsed when candidate data is displayed
- **Activity Timeline** - Visual progress tracking for multi-step workflows
- **Mode Selection** - Switch between Smart Routing, Planning, Q&A, Recruiter, Email, Staffing modes
- **Session Management** - Multiple conversation sessions with history
- **Health Monitoring** - Backend health checks with visual indicators

### Technical Features
- **SSE Streaming** - Real-time streaming from local backend or Vertex AI Agent Engine
- **MCP Integration** - Model Context Protocol servers for recruitment and staffing tools
- **Environment Detection** - Auto-detects deployment mode (local, Agent Engine, Cloud Run)
- **Google Drive API** - Document search and retrieval for Q&A agent
- **GitHub Integration** - Candidate profile scraping and email lookup via Hunter API
- **Weave Tracing** - Observability and tracing integration (optional)

## Tech Stack

- Backend: Python, `google-adk`, `vertexai`, `python-dotenv`
- Frontend: Next.js 15, React 19, TailwindCSS, shadcn/ui
- Tooling: `uv` for Python deps, ESLint + Jest for the frontend, Ruff + Mypy for backend linting/type-checking

## Project Structure

```
app/                                    # Python ADK backend
  agent.py                              # Root coordinator agent (6 sub-agents)
  agent_engine_app.py                   # Deployment helper for Vertex AI Agent Engine
  config.py                             # Env loading, Vertex init, deployment config
  recruiter_agents/                     # Recruiter-focused agents
    recruiter_orchestrator_agent/       # Candidate search, GitHub sourcing, metrics
    candidate_operations_orchestrator/  # Email pipeline (4 sub-agents)
      subagents/
        email_generator/                # Initial email generation
        email_reviewer/                 # Email review and validation
        email_refiner/                  # Email refinement
        email_presenter/                 # Final email presentation
    resume_screening_agent/              # Resume screening and analysis
    compensation_agent/                  # Compensation benchmarking
    recruiter_productivity_agent/       # Productivity tracking
    talent_analytics_orchestrator/       # Analytics and insights
  staffing_agents/                       # Staffing agency workflows
    recruiter_orchestrator_agent/       # Job search, candidate matching
    employer_orchestrator_agent/        # Candidate review, 
    candidate_matching_agent/           # Intelligent candidate matching
    candidate_review_agent/              # Candidate evaluation
    job_search_agent/                   # Job posting search
    interview_scheduling_agent/         # Interview coordination
    submission_agent/                   # Candidate submission
  tools/                                # Shared tools
    google_drive.py                     # Google Drive API integration
  utils/                                # GCS, tracing, and logging helpers

nextjs/                                 # Next.js frontend
  src/app/
    api/
      health/                           # Health check proxy
      run_sse/                          # SSE streaming endpoint
      recruitment/                      # Recruitment API routes
        candidates/                     # Candidate search endpoint
        chat/                           # Recruitment chat endpoint
    page.tsx                            # Main chat interface
  src/components/
    chat/                               # Chat UI components
      ChatContainer.tsx                 # Main chat container with candidate grid
      ChatProvider.tsx                  # Context provider with smart routing
      MarkdownRenderer.tsx              # JSON collapsing and markdown rendering
      BackendHealthChecker.tsx          # Health monitoring
      EmptyState.tsx                    # Initial state with sample prompts
    recruiting/                         # Recruitment-specific components
      CandidateGrid.tsx                 # Candidate card grid display
      CandidateCard.tsx                 # Individual candidate card
      CandidateCardSkeleton.tsx          # Loading skeleton
  src/lib/
    config.ts                           # Environment detection + endpoint resolution
    handlers/                           # Streaming handlers (local/agent-engine)
    recruiting-api.ts                   # Recruitment API client
    utils/
      candidate-parser.ts               # Candidate data parsing

mcp_server/                             # Model Context Protocol servers
  recruitment_backend/                  # Recruitment MCP server
    recruitment_service.py              # Candidate search, GitHub scraping
    github_scraper.py                   # GitHub profile scraping
    candidate_matcher.py                # Intelligent candidate matching
  staffing_backend/                     # Staffing MCP server
    job_search_tool.py                  # Job posting search
    candidate_submission_tool.py        # Candidate submission
    hiring_pipeline_tool.py             # Hiring pipeline management

services/                               # Additional services
  recruitment_api/                      # Mock FastAPI service (MVP dashboard)

Makefile                                # install/dev/lint + deployment helpers
pyproject.toml                          # Python deps and linters
docker-compose.yml                      # Docker Compose for local services
```

## Backend

### Agents

`app/agent.py` defines a multi-agent system with 6 specialized agents coordinated by a root agent:

1. **Root Agent (Coordinator)** - Intelligent router that analyzes requests and delegates to specialists
   - Supports smart routing (automatic intent detection)
   - Supports explicit mode overrides via `[MODE:XXX]` directives from UI
   - Routes to: Planning, Q&A, Recruiter, Email, Staffing Recruiter, or Staffing Employer

2. **Planning Agent** - Recruiter-focused goal planning and task decomposition
   - Uses ADK `LlmAgent` with `BuiltInPlanner` (thinking enabled)
   - Specialized for hiring workflows, daily/weekly task planning
   - Breaks down recruitment goals into actionable tasks

3. **Q&A Agent** - Google Docs search and document Q&A
   - Uses ADK `LlmAgent` with Google Drive tools
   - Searches, reads, and answers questions from Google Docs
   - Provides cited answers with source documents

4. **Recruiter Orchestrator** - Candidate sourcing and recruitment operations
   - GitHub profile search with intelligent matching
   - Pipeline metrics and analytics
   - Email lookup via Hunter API
   - Compensation benchmarking
   - Returns candidate data as JSON for frontend display

5. **Recruiter Email Pipeline** - Outreach email generation and refinement
   - Sequential agent with 4 sub-agents:
     - **Email Generator**: Creates initial email drafts (75-125 words)
     - **Email Reviewer**: Validates email quality
     - **Email Refiner**: Refines emails when user requests improvement
     - **Email Presenter**: Formats and presents final email
   - Enforces strict length limits (500-900 characters max)

6. **Staffing Recruiter Orchestrator** - Staffing agency workflows
   - Job search across multiple platforms
   - Candidate matching to job openings
   - Candidate submission to employers
   - Uses MCP tools from staffing backend

7. **Staffing Employer Orchestrator** - Client company workflows
   - Candidate review and evaluation
   -  and coordination
   - Hiring pipeline status tracking
   - Uses MCP tools from staffing backend

**Model Configuration:** Defaults to `gemini-2.0-flash-exp` (can be changed via `MODEL` env var). Some agents use `gemini-2.0-flash` for faster responses.

**Architecture Details:** See `docs/MULTI_AGENT_ARCHITECTURE.md` for complete documentation.

### Environment

Create `app/.env` with at least the following for local development and deployment:

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Staging bucket for Vertex AI/Agent Engine packaging
# Provide a valid bucket identifier. Example: my-staging-bucket
# (Do not include gs:// prefix.)
GOOGLE_CLOUD_STAGING_BUCKET=my-staging-bucket

# Optional
MODEL=gemini-2.5-flash
AGENT_NAME=goal-planning-agent
EXTRA_PACKAGES=./app
REQUIREMENTS_FILE=.requirements.txt
```

Notes:

- Configuration is validated at import time in `app/config.py` and initializes Vertex AI.
- The Makefile’s deploy target will generate `.requirements.txt` for Agent Engine using `uv export`.

### Run the backend (dev)

The Makefile starts the ADK API server for you:

```bash
make dev-backend
# or run both backend and frontend together
make dev
```

This uses `uv run adk api_server app --allow_origins="*"` which serves the ADK HTTP API at `http://127.0.0.1:8000`.

## Frontend

### Environment

Create `nextjs/.env.local`:

Local backend (default):

```bash
BACKEND_URL=http://127.0.0.1:8000
NODE_ENV=development
```

Agent Engine (direct streaming):

```bash
AGENT_ENGINE_ENDPOINT=https://us-central1-aiplatform.googleapis.com/v1/projects/your-project/locations/us-central1/reasoningEngines/YOUR_ENGINE_ID

# Required when calling Agent Engine directly (e.g. Vercel):
# Base64-encoded service account JSON with permissions for Agent Engine
GOOGLE_SERVICE_ACCOUNT_KEY_BASE64=eyJ0eXAiOiJKV1QiLCJh...  # base64 JSON

NODE_ENV=production
```

Cloud Run (if you host your own proxy backend):

```bash
CLOUD_RUN_SERVICE_URL=https://your-service-url.a.run.app
NODE_ENV=production
```

The frontend auto-detects the deployment mode in `nextjs/src/lib/config.ts` and will:

- Use Agent Engine when `AGENT_ENGINE_ENDPOINT` is set
- Use Cloud Run when `CLOUD_RUN_SERVICE_URL` (or Cloud env vars) are present
- Default to local backend otherwise

### Run the frontend (dev)

```bash
npm --prefix nextjs install
npm --prefix nextjs run dev
```

Open `http://localhost:3000`.

## MCP Servers

The application uses Model Context Protocol (MCP) servers to provide tools for agents:

### Recruitment MCP Server

**Location:** `mcp_server/recruitment_backend/`

**Capabilities:**
- Candidate search with intelligent matching
- GitHub profile scraping and analysis
- Email lookup via Hunter API
- Pipeline metrics and analytics
- Compensation benchmarking

**Local Development:**
```bash
# Install dependencies
make install-recruitment-deps

# Start MCP server
make dev-recruitment-mcp
# Server runs on http://localhost:8100
```

**Testing:**
```bash
cd mcp_server/recruitment_backend
python test_service.py
```

**Deployment:** See `mcp_server/mcpdocs/README.md` for Cloud Run deployment instructions.

### Staffing MCP Server

**Location:** `mcp_server/staffing_backend/`

**Capabilities:**
- Job search across multiple platforms
- Candidate submission management
- Hiring pipeline tracking
-  (planned)

**Local Development:**
```bash
# Install dependencies
make install-staffing-deps

# Start MCP server
make dev-staffing-mcp
# Server runs on http://localhost:8100
```

**Testing:**
```bash
make test-staffing-tools
```

**Deployment:** See `mcp_server/staffing_backend/README.md` for deployment instructions.

**Note:** MCP servers can be deployed to Cloud Run and accessed by agents via `MCP_SERVER_URL` environment variable.

## Streaming Architecture

- API route `nextjs/src/app/api/run_sse/route.ts` orchestrates streaming and delegates to:
  - `run-sse-local-backend-handler.ts` for local ADK backend
  - `run-sse-agent-engine-handler.ts` when using Agent Engine
- For Agent Engine, JSON fragments are transformed into SSE format on the server so the UI can render incremental `text` and `thought` parts consistently.

## Lint, Type-Check, and Tests

Python (from repo root):

```bash
make lint
```

Node/TypeScript (from repo root):

```bash
npm --prefix nextjs run lint
npm --prefix nextjs run test
```

## Frontend Features

### Chat Interface

The main chat interface (`nextjs/src/app/page.tsx`) provides:

- **Streaming Responses** - Real-time SSE streaming from agents
- **Candidate Grid** - Side-by-side display of candidate profiles when sourcing
- **Smart Routing** - Automatic agent selection based on query intent
- **Mode Selection** - Manual override to specific agents (Planning, Q&A, Recruiter, Email, Staffing)
- **Session Management** - Multiple conversation sessions with history
- **JSON Collapsing** - Large JSON responses automatically collapsed when candidate data is displayed
- **Activity Timeline** - Visual progress tracking for multi-step workflows (email generation, employer review)

### Candidate Display

When agents return candidate data:
- Automatically parsed and displayed in a card grid
- GitHub profiles with stats (repos, stars, followers, commits)
- Skills, experience level, and match scores
- Email addresses (when available via Hunter API)
- Skeleton loaders during search operations

### Sample Prompts

The UI includes sample prompts for common tasks:
- "Fetch senior engineers on GitHub"
- "Find software engineer jobs in U.S"
- "Find email addresses for displayed candidates"
- "How does this app work?"

**Tip:** Prefer linting and type-checking for fast feedback during development instead of full builds.

## Deployments

### Deploy the Agent to Vertex AI Agent Engine

Prerequisites:

- `gcloud auth application-default login`
- `gcloud config set project YOUR_PROJECT_ID`
- A GCS bucket for packaging (match `GOOGLE_CLOUD_STAGING_BUCKET` in `app/.env`)

**Create Staging Bucket (if needed):**
```bash
# For recruiter agent
make create-recruiter-bucket
# Creates: gs://recruiter-staging
```

**Deploy:**

```bash
# Deploy with specific agent name and bucket
AGENT_NAME=recruiter-agent GOOGLE_CLOUD_STAGING_BUCKET=recruiter-staging make deploy-adk

# Or set in app/.env and run:
make deploy-adk
```

What it does:

- Exports Python dependencies to `.requirements.txt` using uv
- Packages and deploys the ADK app via `app/agent_engine_app.py`
- Creates a logs/data bucket for artifacts if missing
- Outputs deployment metadata to `logs/deployment_metadata.json`

**After deployment:**
1. Copy the returned Reasoning Engine endpoint
2. Set `AGENT_ENGINE_ENDPOINT` in `nextjs/.env.local` (or Vercel environment variables)
3. Set `GOOGLE_SERVICE_ACCOUNT_KEY_BASE64` (base64-encoded service account JSON) for authentication

**Agent Deployment Reference:** See `docs/AGENTS_REFERENCE.md` for managing multiple agent deployments.

### Deploy the Frontend (Vercel)

**Prerequisites:**
- Next.js app builds successfully (`npm run build` in `nextjs/` directory)
- Environment variables configured

**Required Environment Variables in Vercel:**

For Agent Engine deployment:
```bash
AGENT_ENGINE_ENDPOINT=https://us-central1-aiplatform.googleapis.com/v1/projects/...
GOOGLE_SERVICE_ACCOUNT_KEY_BASE64=<base64-encoded-service-account-json>
NODE_ENV=production
```

For local backend (development):
```bash
BACKEND_URL=http://127.0.0.1:8000
NODE_ENV=development
```

**Optional Environment Variables:**
```bash
RECRUITMENT_BACKEND_URL=http://localhost:8100  # MCP server URL
NEXT_PUBLIC_RECRUITING_API_URL=http://127.0.0.1:8085  # Mock API (if using)
```

**Deployment Steps:**

1. Push your code to GitHub
2. Import the `nextjs` directory as a Vercel project
3. Set environment variables in Vercel dashboard
4. Deploy

**Full Guide:** See `docs/NEXTJS_VERCEL_DEPLOYMENT_GUIDE.md` for detailed step-by-step instructions.

**Note:** The Next.js app is ready for Vercel deployment. Build errors have been resolved (TypeScript types, unused variables).

## Health Checks

`GET /api/health` on the frontend forwards to the backend health endpoint (`/health`). Configure backend URL/endpoint via env as described above.

## Troubleshooting

### Backend Issues

- **Missing Google Cloud envs**: `app/config.py` validates env on import. Ensure `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `GOOGLE_CLOUD_STAGING_BUCKET` are set in `app/.env`.
- **Agent Engine authentication**: Frontend requires `GOOGLE_SERVICE_ACCOUNT_KEY_BASE64` with correct scopes (`https://www.googleapis.com/auth/cloud-platform`).
- **Local streaming issues**: Verify `BACKEND_URL` in `nextjs/.env.local` and that `make dev-backend` is running.
- **MCP server connection**: Ensure MCP servers are running and `MCP_SERVER_URL` or `RECRUITMENT_BACKEND_URL` is correctly configured.

### Frontend Issues

- **Build errors**: Run `npm run clean` in `nextjs/` directory to clear `.next` cache before building.
- **Candidate grid not updating**: Ensure you're using "Recruiter" mode or smart routing detects recruiter queries. Check browser console for errors.
- **JSON not collapsing**: Verify `MarkdownRenderer.tsx` is detecting candidate JSON correctly. Check that candidate data is being parsed in `ChatProvider.tsx`.

### Agent Routing Issues

- **Wrong agent selected**: Use explicit mode selection in UI (`[MODE:RECRUITER]`, etc.) or check smart routing keywords in `ChatProvider.tsx`.
- **Email not generating**: Ensure job description is provided. Check email generator agent logs.
- **Email too long**: Email pipeline enforces 75-125 words (500-900 characters). Check `email_generator`, `email_refiner`, and `email_presenter` agents.

### MCP Server Issues

- **Connection errors**: Verify MCP server is running on correct port (default: 8100 for recruitment, 8100 for staffing).
- **Tool not found**: Check MCP server logs and ensure tools are properly registered in `server.py`.
- **Testing**: Use `make test-staffing-tools` or `python test_service.py` in respective MCP server directories.

**Additional Resources:**
- `docs/TESTING_GUIDE.md` - Comprehensive testing instructions
- `mcp_server/mcpdocs/LOCAL_TESTING.md` - MCP server testing guide
- `docs/ENV_VARS_GUIDE.md` - Complete environment variable reference

## License

Apache-2.0 (unless noted otherwise in third-party files).
