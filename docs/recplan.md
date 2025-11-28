# Recruiting Dashboard Integration (MVP, Docker Compose)

## Goal

Add the ref dashboard UI to this repo’s `nextjs`, power it with a mock Recruiting API, and run both via Docker Compose. Keep room to later switch the backend to ADK agents on Vertex Agent Engine and the MCP server deployed on Cloud Run per `docs/ADK_DEPLOYMENT_GUIDE.md` and `mcp_server/mcpdocs/README.md`.

## Architecture (MVP)

- Frontend: Next.js app at [nextjs/](nextjs/), extended with a recruiter experience ported from `refs/ai_agent_rocket`. Single app serves all routes on the same host/port (`http://localhost:3000`).
- Backend: Mock Recruiting API (FastAPI) at [services/recruitment_api/](services/recruitment_api/) serving dashboard data and search; CORS enabled.
- Orchestration: Docker Compose at [docker-compose.yml](docker-compose.yml) for local, containerized dev.
- Ports: frontend `3000`, mock API `8085`. Existing ADK dev server remains on `8000` (unchanged).

## Compatibility & Safety (No Breaks)

- No changes to existing ADK code or `app/` behavior.
- No changes to `nextjs/src/lib/config.ts` or current `BACKEND_URL` usage (remains default `http://127.0.0.1:8000`).
- Recruiter UI reads from a new env var `NEXT_PUBLIC_RECRUITING_API_URL`; legacy UI continues using `BACKEND_URL`.
- Existing Makefile targets (`dev`, `dev-backend`, `dev-frontend`, `deploy-adk`) remain unchanged; Docker Compose is additive.
- Routes stay under the single Next.js app: `/` for current home, `/recruiter` landing, `/recruiter/dashboard/*` for detailed pages.

## Key Files to Add/Change

- Add: [docker-compose.yml](docker-compose.yml)
- Add: [services/recruitment_api/pyproject.toml](services/recruitment_api/pyproject.toml)
- Add: [services/recruitment_api/main.py](services/recruitment_api/main.py)
- Add: [services/recruitment_api/Dockerfile](services/recruitment_api/Dockerfile)
- Add: [services/recruitment_api/.env.example](services/recruitment_api/.env.example)
- Add: [nextjs/.env.local.example](nextjs/.env.local.example) with `NEXT_PUBLIC_RECRUITING_API_URL`
- Add: [nextjs/src/lib/recruiting-api.ts](nextjs/src/lib/recruiting-api.ts)
- Add: [nextjs/src/types/recruiting.ts](nextjs/src/types/recruiting.ts)
- Add: Recruiter routes/pages and components under [nextjs/src/app/recruiter/](nextjs/src/app/recruiter/) (ported from ref)
- Update: Add navigation entry (e.g., header/sidebar) linking to `/recruiter`
- Optional: [Makefile](Makefile) new targets `dev-docker`, `down-docker` (no changes to existing targets)

## Mock Recruiting API (FastAPI)

- Endpoints (JSON):
- `GET /health` → `{ status: "ok" }`
- `GET /dashboard/metrics` → summary KPIs for cards/charts
- `GET /candidates?query=&skills=&location=` → list with GitHub fields
- `GET /candidates/{id}` → detail
- `GET /jobs?stack=&level=` → list
- `GET /applications?stage=` → list
- `GET /productivity/summary?window=7d|30d` → time tracking rollups (for Productivity view)
- Implementation: in-memory seed (JSON) first; optional SQLite via SQLModel later. Pydantic models for types, `fastapi.middleware.cors` for CORS, `uvicorn` on 0.0.0.0:8085.

## Frontend Integration (Next.js)

- Keep the existing home page at `/` untouched.
- Add recruiter landing at `/recruiter`.
- Add dashboard hub at `/recruiter/dashboard` with subroutes:
- `/recruiter/dashboard/candidates`
- `/recruiter/dashboard/jobs`
- `/recruiter/dashboard/applications`
- `/recruiter/dashboard/productivity`
- Create typed API client `src/lib/recruiting-api.ts` using `fetch` against `NEXT_PUBLIC_RECRUITING_API_URL`.
- Add shared chart/table components (ported from ref) wired to the mock API endpoints.
- Types live in `src/types/recruiting.ts` (Candidate, Job, Application, Metrics, ProductivityBucket, etc.).
- Env (local dev): `nextjs/.env.local` → `NEXT_PUBLIC_RECRUITING_API_URL=http://127.0.0.1:8085`. Do not change `BACKEND_URL`.
- Update navigation (e.g., `nextjs/src/components/chat/ChatHeader.tsx` or other global nav) to expose `/recruiter` entry.

## Docker Compose (local)

Create [docker-compose.yml](docker-compose.yml):

- `frontend` (node:20):
- context: `nextjs/`
- command: `npm ci && npm run dev`
- ports: `3000:3000`
- env: `NEXT_PUBLIC_RECRUITING_API_URL=http://recruitment-api:8085`, `NODE_ENV=development`
- depends_on: `recruitment-api`
- `recruitment-api` (python:3.11-slim):
- context: `services/recruitment_api/`
- command: `uvicorn main:app --host 0.0.0.0 --port 8085`
- ports: `8085:8085`
- env: from `.env` (CORS origins, seed toggles)
- Network: default bridge; healthchecks for both services.

## Makefile (optional convenience)

- `dev-docker`: `docker compose up --build`
- `down-docker`: `docker compose down -v`
- Keep existing `dev`, `dev-backend`, `dev-frontend` targets unchanged.

## Configuration

- Keep `BACKEND_URL` semantics and `nextjs/src/lib/config.ts` unchanged for existing features.
- The new recruiter UI exclusively uses `NEXT_PUBLIC_RECRUITING_API_URL`.
- Future: `AGENT_ENGINE_ENDPOINT` and `MCP_SERVER_URL` remain documented for Phase 2 and are not part of the MVP.

## Verification (MVP)

1. `docker compose up --build`
2. Open `http://localhost:3000/` → existing home works.
3. Navigate to `http://localhost:3000/recruiter` → recruiter landing renders.
4. Navigate to `http://localhost:3000/recruiter/dashboard/...` pages → data loads from mock API, no CORS errors.
5. `curl http://localhost:8085/health` returns ok.
6. Existing chat/ADK UI paths continue to function via unchanged `BACKEND_URL` defaults.

## Phase 2 (Later): Wire to Agent Engine + MCP

- Replace mock API data providers with calls to ADK agents (Agent Engine) and MCP tools:
- Configure `MCP_SERVER_URL=https://<cloud-run>/mcp` in agent env (per `mcp_server/mcpdocs/README.md`).
- Expose API endpoints in ADK backend mirroring the mock API shapes to keep the UI unchanged.
- Deploy agents via `make deploy-adk` (per `docs/ADK_DEPLOYMENT_GUIDE.md`). Update frontend env to point to the ADK backend URL or Agent Engine direct endpoints as needed.

## Rollback

- The recruiter experience is additive under `src/app/recruiter/`. Removing that folder plus `docker-compose.yml` reverts the repo to pre-dashboard state.