Tracing the architecture to identify which agents handle GitHub queries and their responsibilities:


## Current state: what's working

### Agent handling GitHub queries
**`RecruiterOrchestrator`** (in `app/recruiter_agents/recruiter_orchestrator_agent/adk_agent.py`)

- Current role: directly handles candidate search queries
- Tool used: `search_candidates_tool` (calls `CandidateMatcher` from MCP server)
- Status: working — returns JSON with candidate profiles
- Architecture: simple `LlmAgent` that bypasses sub-orchestrators and calls the tool directly

### Flow
```
User Query → Root Agent → RecruiterOrchestrator → search_candidates_tool → CandidateMatcher → JSON Response
```

### Agent handling recruiter outreach emails
**`RecruiterEmailPipeline`** (in `app/recruiter_agents/candidate_operations_orchestrator/agent.py`)

- Current role: generates, reviews, and refines recruiter outreach emails
- Pattern: SequentialAgent (generator) + LoopAgent (reviewer + refiner)
- Tooling: Local GitHub profile lookup tool for concrete personalization
- Status: working — available via `[MODE:EMAIL]` or smart routing when the user asks for email drafts
- Output: Final email body only, ready to display in chat UI

### Email flow
```
User Request → Root Agent ([MODE:EMAIL]) → RecruiterEmailPipeline
  Step 1: EmailGenerator → requires JD
  Step 2: EmailReviewer → pass/fail + exit_loop
  Step 3: EmailRefiner → GitHub personalization
→ Final email returned to chat
```

---

## Full architecture (built but not fully connected)

### 1. Root Recruiter Orchestrator (Port 8101)
- Location: `app/recruiter_agents/recruiter_orchestrator_agent/`
- Current: Simple ADK agent with direct tool access
- Should do: Route to sub-orchestrators via A2A protocol
- Files: `agent.py` (full A2A orchestrator), `adk_agent.py` (current simple version)

### 2. Recruiter Email Loop Agent (Port 8102)
- Location: `app/recruiter_agents/candidate_operations_orchestrator/`
- Scope:
  - EmailGenerator (JD-aware first draft)
  - EmailReviewer (quality gate + exit_loop)
  - EmailRefiner (GitHub profile personalization tool)
- Status: Active – integrated into root agent via `[MODE:EMAIL]`

### 3. Talent Analytics Orchestrator (Port 8106)
- Location: `app/recruiter_agents/talent_analytics_orchestrator/`
- Should coordinate:
  - Compensation Agent (8107)
  - Recruiter Productivity Agent (8108)
- Status: Built but not actively routing

### 4. Specialist agents (ports 8103-8108)
All built with MCP tool access (two have now been retired in favor of direct tools on the RecruiterOrchestrator):
- Candidate Sourcing Agent (retired) — GitHub sourcing logic moved into RecruiterOrchestrator
- Resume Screening Agent (8104) — AI matching
- Candidate Portfolio Agent (retired) — Code review functionality now exposed through RecruiterOrchestrator tools
- Compensation Agent (8107) — Salary benchmarking
- Recruiter Productivity Agent (8108) — Time tracking

---

## What needs to happen next

### Option 1: Enhance current simple agent (quick wins)
- Add more tools to `RecruiterOrchestrator`:
  - `scrape_github_profiles_tool` — for sourcing new profiles
  - `analyze_portfolio_tool` — for deep portfolio analysis
  - `get_compensation_data_tool` — for salary questions
  - `get_pipeline_metrics_tool` — for analytics

### Option 2: Activate full multi-agent architecture (long-term)
- Switch `RecruiterOrchestrator` to use the full A2A orchestrator (`agent.py` instead of `adk_agent.py`)
- Start sub-orchestrators (ports 8102, 8106)
- Start specialist agents (ports 8103-8108)
- Route queries through the hierarchy:
  - Simple searches → Candidate Sourcing Agent
  - Matching/ranking → Resume Screening Agent
  - Deep analysis → Candidate Portfolio Agent
  - Compensation → Compensation Agent
  - Analytics → Recruiter Productivity Agent

---

## Recommendation

Start with Option 1 to add more tools to the current working agent, then gradually activate the full architecture as needed. This keeps the current flow working while adding capabilities.

Analyzing recruiter agent usage across the codebase:


## Agent usage status

### Fully used (100%) — 2 agents

1. **Recruiter Orchestrator Agent** (`adk_agent.py`)
   - Status: Active and integrated
   - Location: `app/recruiter_agents/recruiter_orchestrator_agent/adk_agent.py`
   - Integration: Imported in `app/agent.py` as a sub-agent
   - Tools: `search_candidates_tool`, `find_candidate_emails_tool`, `find_emails_by_github_usernames_tool`
   - Usage: Handles all `[MODE:RECRUITER]` queries (candidate sourcing/matching)

2. **Recruiter Email Pipeline** (`candidate_operations_orchestrator/agent.py`)
   - Status: Active and integrated
   - Location: `app/recruiter_agents/candidate_operations_orchestrator/`
   - Flow: EmailGenerator → EmailReviewer (exit_loop) → EmailRefiner (GitHub lookup tool)
   - Usage: Handles all `[MODE:EMAIL]` queries (draft, review, refine outreach copy)

---

### Dormant (0% — built but not connected) — 4 agents

**1. Talent Analytics Orchestrator** (Port 8106)
- Location: `app/recruiter_agents/talent_analytics_orchestrator/`
- Status: Built but not used
- Should coordinate: Compensation + Productivity
- Current: Not called by RecruiterOrchestrator

**2. Resume Screening Agent** (Port 8104)
- Location: `app/recruiter_agents/resume_screening_agent/`
- Status: Built but not used
- MCP tools: `search_candidates_tool`, `get_pipeline_metrics_tool`
- Current: Not called by any orchestrator

**3. Compensation Agent** (Port 8107)
- Location: `app/recruiter_agents/compensation_agent/`
- Status: Built but not used
- Purpose: Salary benchmarking
- Current: Not called by any orchestrator

**4. Recruiter Productivity Agent** (Port 8108)
- Location: `app/recruiter_agents/recruiter_productivity_agent/`
- Status: Built but not used
- Purpose: Time tracking and productivity
- Current: Not called by any orchestrator

### Retired Agents
- Candidate Sourcing Agent (8103) — GitHub sourcing logic moved into RecruiterOrchestrator
- Candidate Portfolio Agent (8105) — Portfolio analysis logic handled by RecruiterOrchestrator tools

---

## Summary

| Category | Count | Percentage |
|----------|-------|------------|
| Fully used | 2 | 33% |
| Dormant | 4 | 67% |
| Total | 6 | 100% |

Retired agents (candidate sourcing & portfolio) are excluded from the totals because their folders were removed.

---

## Why this architecture

The current `RecruiterOrchestrator` (`adk_agent.py`) is a simplified version that:
- Directly calls MCP tools (bypasses sub-agents)
- Works without starting 6 separate services
- Handles candidate search and email lookup

The full multi-agent architecture exists (`agent.py` files) but requires:
- Starting 6 separate agent services (ports 8102-8108)
- A2A protocol routing between agents
- More complex orchestration

---

## Recommendation

Current approach (Option 1): Keep the simplified orchestrator and add more tools directly to `RecruiterOrchestrator`:
- `scrape_github_profiles_tool`
- `analyze_portfolio_tool`
- `get_compensation_data_tool`
- `get_pipeline_metrics_tool`

This keeps the system simple while adding capabilities.

Alternative (Option 2): Activate the full multi-agent architecture by:
- Switching to the full A2A orchestrator (`agent.py`)
- Starting all 6 specialist agents
- Implementing proper routing

Checking if we're using the loop workflow:


**Yes, we're using the LoopAgent workflow.**

From the code:

1. **`email_refinement_loop`** is a `LoopAgent` (line 16):
   - `max_iterations=2`
   - Sub-agents: `email_reviewer` → `email_refiner`
   - Iterates until the reviewer approves or the max is reached

2. **Root agent** is a `SequentialAgent` (line 23):
   - Runs: `email_generator` → `email_refinement_loop` → `email_presenter`
   - The loop is embedded in the sequential flow

**Flow:**
1. EmailGenerator creates the first draft
2. LoopAgent runs:
   - EmailReviewer evaluates
   - If not approved → EmailRefiner improves
   - Repeats up to 2 times
3. EmailPresenter shows the final result

This adds a quality gate and iterative refinement.

# Electron Floating Windows Integration Plan

## Overview

Add Electron support so recruiters can open LinkedIn/job/candidate sites inside always-on-top floating windows while chatting. Inspired by Pennywise but integrated with the Next.js UI via a header menu.

## Architecture

```
nextjs/
├── electron/
│   ├── main.js              # Main Electron process (IPC, main window)
│   ├── preload.js           # Secure bridge exposing electronAPI
│   └── windows/
│       └── floating.js      # Floating window creation/management
├── src/
│   ├── lib/
│   │   └── electron.ts      # Client-side helpers (openFloatingWindow, isElectron)
│   ├── components/chat/
│   │   └── FloatingWindowMenu.tsx  # Header dropdown for quick actions
│   └── types/
│       └── electron.d.ts    # Global typings for window.electronAPI
└── package.json             # Add electron deps & scripts
```

## Implementation Steps

### 1. Install Dependencies

- Add devDependencies: `electron`, `electron-builder`, `concurrently`, `wait-on`
- Update scripts: `electron:dev`, `electron:start`, `electron:build`

### 2. Main Electron Process (`electron/main.js`)

- Create BrowserWindow for main Next.js app
- Load `http://localhost:3000` in dev or exported HTML in prod
- Register IPC handlers: `floating-window:open`, `floating-window:close`, `floating-window:list`
- Wire app lifecycle (ready, activate, window-all-closed)

### 3. Preload Bridge (`electron/preload.js`)

- Use `contextBridge` to expose `electronAPI` with:
  - `openFloatingWindow(url, options)`
  - `closeFloatingWindow(windowId)`
  - `listFloatingWindows()`
  - `isElectron()` helper
- Communicate via `ipcRenderer.invoke`

### 4. Floating Window Manager (`electron/windows/floating.js`)

- Validate/sanitize URLs (prepend https:// when missing)
- Create BrowserWindow instances (always-on-top, resizable, no Node integration)
- Track windows in a Map and clean up on close
- Export helpers for main process IPC

### 5. Client Helper (`src/lib/electron.ts`)

- `isElectron()` detection (safe for SSR)
- `openFloatingWindow()` wrapper with browser fallback (`window.open`)
- Optional `closeFloatingWindow`/`listFloatingWindows` helpers

### 6. Type Definitions (`src/types/electron.d.ts`)

- Declare `window.electronAPI` interface + option type used by helpers
- Ensure TS recognizes the API across components

### 7. Header Menu UI (`src/components/chat/FloatingWindowMenu.tsx`)

- Button + dropdown (Radix-style) with:
  - URL input + validation (toast errors)
  - Quick actions (LinkedIn, GitHub, LinkedIn Jobs)
  - Optional list of open windows with close buttons (if `list` API available)
- Only render if `isElectron()` is true (defer until after mount to avoid hydration issues)
- Handle outside-click/escape to close

### 8. Update Header (`src/components/chat/ChatHeader.tsx`)

- Import and render `FloatingWindowMenu` between "Recruiter Hub" link and `UserIdInput`
- Button inherits existing header styles; hides automatically when not in Electron

### 9. Optional UI Hooks (Future)

- Candidate cards may call `openFloatingWindow` for deep links, but not required for MVP

### 10. Testing

- `npm run electron:dev` opens Next.js + Electron together
- Verify: main window loads, menu button appears only in Electron, floating windows open and stay on top, quick actions launch correct URLs, fallback works in browser, no console errors

## Security Notes

- `contextIsolation: true`, `nodeIntegration: false`
- Preload only exposes minimal API; floating windows load remote sites without preload
- URL sanitization prevents invalid protocols

PHASE 4

# 3-Day Staffing Agency Suite Deployment Plan

## Day 0: Cleanup Supply Chain Agents (1-2 hours)

### Remove Supply Chain Components

- Delete `app/supply_chain/` directory and all subdirectories:
  - `buyer_orchestrator_agent/`
  - `supplier_orchestrator_agent/`
  - `inventory_management_agent/`
  - `purchase_validation_agent/`
  - `purchase_order_agent/`
  - `order_intelligence_agent/`
  - `production_queue_management_agent/`
- Remove supply chain imports from `app/agent.py`:
  - Remove `from app.supply_chain.buyer_orchestrator_agent.adk_agent import buyer_orchestrator_agent`
  - Remove `from app.supply_chain.supplier_orchestrator_agent.adk_agent import supplier_orchestrator_agent`
- Remove supply chain agents from `app/agent.py` sub_agents list
- Remove supply chain routing instructions from `app/agent.py`:
  - Remove BuyerOrchestrator and SupplierOrchestrator descriptions
  - Remove "[MODE:BUYER]" and "[MODE:SUPPLIER]" routing logic
- Note: MCP tools in `mcp_server/mcppoagent.py` can remain (they're purchase order tools, not supply chain specific)

---

## Day 0: Complete Supply Chain Cleanup (2-3 hours)

### Remove All Supply Chain Agents

- Delete entire `app/supply_chain/` directory:
  - `buyer_orchestrator_agent/` (all files)
  - `supplier_orchestrator_agent/` (all files)
  - `inventory_management_agent/` (all files)
  - `purchase_validation_agent/` (all files)
  - `purchase_order_agent/` (all files)
  - `order_intelligence_agent/` (all files)
  - `production_queue_management_agent/` (all files)
  - `__init__.py` and `LICENSE` files

### Remove Supply Chain References from app/agent.py

- Remove imports:
  - `from app.supply_chain.buyer_orchestrator_agent.adk_agent import buyer_orchestrator_agent`
  - `from app.supply_chain.supplier_orchestrator_agent.adk_agent import supplier_orchestrator_agent`
- Remove from `sub_agents` list: `buyer_orchestrator_agent`, `supplier_orchestrator_agent`
- Remove routing instructions:
  - Remove "BuyerOrchestrator" description (lines 194-198)
  - Remove "SupplierOrchestrator" description (lines 199-203)
  - Remove "[MODE:BUYER]" routing logic (line 233)
  - Remove "[MODE:SUPPLIER]" routing logic (line 234)
  - Remove buyer/supplier routing examples (lines 219-220)
  - Update coordinator description to remove "Buyer, Supplier" references

### Remove Supply Chain MCP Tools

- Delete MCP tool files:
  - `mcp_server/restock_inventory_tool.py`
  - `mcp_server/purchase_queue_tool.py`
  - `mcp_server/po_record_tool.py`
  - `mcp_server/po_email_generator_tool.py`
- Remove from `mcp_server/mcppoagent.py`:
  - Remove imports: `RestockInventoryTool`, `PurchaseQueueTool`, `PORecordTool`, `POEmailGenerator`
  - Remove tool initializations: `purchase_queue`, `po_record`, `po_email`, `inventory_tool`
  - Remove all @mcp.tool() functions:
    - `generate_purchase_order` (lines 41-84)
    - `generate_latex_po` (lines 86-129)
    - `generate_purchase_order_document` (lines 132-153)
    - `validate_po_items` (lines 155-183)
    - `create_sample_po_data` (lines 185-252)
    - `get_financial_data` (lines 276-284)
    - `manage_purchase_queue` (lines 287-296)
    - `manage_po_records` (lines 299-309)
    - `generate_po_email` (lines 312-342)
    - `send_purchase_order_email` (lines 345-390)
    - `analyze_inventory` (lines 393-402)
  - Keep: `fetch_emails`, `parse_document`, `save_report`, `send_response_email`, `health_check` (these may be used by other agents)

### Verify Cleanup

- Run `grep -r "supply_chain\|buyer_orchestrator\|supplier_orchestrator\|purchase_order\|inventory_management\|production_queue" app/` to ensure no remaining references
- Test that `app/agent.py` imports and runs without errors
- Verify MCP server starts without supply chain tool errors

---

## Day 0: Complete Supply Chain Cleanup (2-3 hours)

### Phase 1: Remove Supply Chain Agents (30 min)

- Delete entire `app/supply_chain/` directory and all subdirectories:
  - `buyer_orchestrator_agent/`
  - `supplier_orchestrator_agent/`
  - `inventory_management_agent/`
  - `purchase_validation_agent/`
  - `purchase_order_agent/`
  - `order_intelligence_agent/`
  - `production_queue_management_agent/`
  - `__init__.py`, `LICENSE`

### Phase 2: Clean app/agent.py (30 min)

**Remove imports (lines 24-25):**

- Remove: `from app.supply_chain.buyer_orchestrator_agent.adk_agent import buyer_orchestrator_agent`
- Remove: `from app.supply_chain.supplier_orchestrator_agent.adk_agent import supplier_orchestrator_agent`

**Remove from sub_agents list (lines 262-263):**

- Remove: `buyer_orchestrator_agent,`
- Remove: `supplier_orchestrator_agent,`

**Update coordinator description (line 180):**

- Change: "Coordinator managing Planning, Q&A, Buyer, Supplier, Recruiter, and Recruiter Email agents"
- To: "Coordinator managing Planning, Q&A, Recruiter, and Recruiter Email agents"

**Remove routing instructions:**

- Remove BuyerOrchestrator section (lines 194-197)
- Remove SupplierOrchestrator section (lines 199-202)
- Remove buyer/supplier routing examples (lines 219-220)
- Remove "[MODE:BUYER]" routing (line 233)
- Remove "[MODE:SUPPLIER]" routing (line 234)
- Update mode extraction comment (line 241): Remove "BUYER, SUPPLIER" from list

### Phase 3: Remove Supply Chain MCP Tools (1 hour)

**Delete tool files:**

- `mcp_server/restock_inventory_tool.py`
- `mcp_server/purchase_queue_tool.py`
- `mcp_server/po_record_tool.py`
- `mcp_server/po_email_generator_tool.py`
- `mcp_server/document_generator_tool.py` (only used for PO generation)
- `mcp_server/email_monitoring_tool.py` (only used for PO email monitoring)
- `mcp_server/document_parser_tool.py` (only used for PO parsing)
- `mcp_server/financial_tool.py` (only used for purchase validation)
- `mcp_server/email_response_tool.py` (only used for PO email responses)
- `mcp_server/report_file_tool.py` (only used for inventory reports)

**Clean mcp_server/mcppoagent.py:**

- Remove imports (lines 6-15): All tool imports except keep structure
- Remove tool initializations (lines 28-37): `doc_generator`, `email_monitor`, `doc_parser`, `financial_tool`, `purchase_queue`, `po_record`, `po_email`, `inventory_tool`, `report_tool`, `email_response`
- Remove all @mcp.tool() functions:
  - `generate_purchase_order` (lines 41-84)
  - `generate_latex_po` (lines 86-129)
  - `generate_purchase_order_document` (lines 132-153)
  - `validate_po_items` (lines 155-183)
  - `create_sample_po_data` (lines 185-252)
  - `fetch_emails` (lines 255-262)
  - `parse_document` (lines 265-273)
  - `get_financial_data` (lines 276-284)
  - `manage_purchase_queue` (lines 287-296)
  - `manage_po_records` (lines 299-309)
  - `generate_po_email` (lines 312-342)
  - `send_purchase_order_email` (lines 345-390)
  - `analyze_inventory` (lines 393-402)
  - `save_report` (lines 405-424)
  - `send_response_email` (lines 427-446)
- Keep: `health_check` tool (lines 448-455) - generic utility
- Update server name/description if needed

### Phase 4: Verification (30 min)

- Run: `python -c "from app.agent import root_agent; print('✅ app/agent.py imports successfully')"`
- Verify no broken imports: `grep -r "supply_chain\|buyer_orchestrator\|supplier_orchestrator" app/` (should return nothing)
- Verify recruiter agents still work: Check that `recruiter_orchestrator_agent` imports correctly
- Test MCP server starts: `python mcp_server/mcppoagent.py` (should only show health_check tool)

**Safety Checks:**

- ✅ Recruiter agents use `mcp_server/recruitment_backend/server.py` (separate, unaffected)
- ✅ No cross-dependencies between supply chain and recruiter tools
- ✅ Planning and Q&A agents unaffected
- ✅ Email pipeline agent unaffected

---

## Day 1: MCP Tools & Database Setup (8-10 hours)

### Morning: Database Schema (2 hours)

- Create supporting tables in Supabase:
  - `employers` table (SQL from TODOSupply.md lines 89-104)
  - `recruiters` table (SQL from lines 140-151)
  - `hiring_pipeline` table (SQL from lines 154-169)
- Test queries on existing `job_flow` and `resume_submissions` tables

### Afternoon: MCP Tools Implementation (6 hours)

**Create `mcp_server/staffing_backend/` directory structure:**

- `job_search_tool.py` - Full implementation with Supabase + JSearch fallback (lines 228-510)
- `candidate_submission_tool.py` - Create submissions in `resume_submissions` (lines 512-604)
- `hiring_pipeline_tool.py` - Manage interview pipeline (lines 606-709)
- `requirements.txt` - Add dependencies (lines 713-719)
- `mcpstaffingagent.py` - Main MCP server file (register all tools)

**Key files to create:**

- `mcp_server/staffing_backend/job_search_tool.py` (282 lines)
- `mcp_server/staffing_backend/candidate_submission_tool.py` (93 lines)
- `mcp_server/staffing_backend/hiring_pipeline_tool.py` (100 lines)
- `mcp_server/staffing_backend/mcpstaffingagent.py` (new, ~150 lines)

**Test locally:**

- Verify Supabase connection
- Test job search with existing `job_flow` data
- Test JSearch API fallback
- Test candidate submission creation

---

## Day 2: ADK Agents & Frontend Integration (8-10 hours)

### Morning: ADK Agents (4 hours)

**Create `app/staffing_agents/` directory:**

- `recruiter_orchestrator_agent/adk_agent.py` (lines 744-827)
- `employer_orchestrator_agent/adk_agent.py` (lines 832-908)
- `job_search_agent/agent.py` - Sub-agent for job search
- `candidate_matching_agent/agent.py` - Sub-agent for matching
- `submission_agent/agent.py` - Sub-agent for submissions
- `candidate_review_agent/agent.py` - Sub-agent for review
- `interview_scheduling_agent/agent.py` - Sub-agent for scheduling

**Update `app/agent.py`:**

- Import `recruiter_orchestrator_agent` and `employer_orchestrator_agent`
- Add to `sub_agents` list
- Add routing instructions (lines 958-968)

### Afternoon: Frontend Integration (4 hours)

**Update `nextjs/src/components/chat/ChatProvider.tsx`:**

- Add "recruiter" and "employer" to `AgentMode` type (line 943)
- Add mode routing logic

**Update `nextjs/src/components/chat/JsonToHtmlRenderer.tsx`:**

- Add `renderJobSearchResults()` function (lines 985-1036)
- Add `renderCandidateSubmissions()` renderer
- Add `renderHiringPipeline()` renderer
- Add action buttons: "Find Candidates", "Submit Candidate"

**Test end-to-end:**

- Test recruiter mode: "Find customer service jobs"
- Test employer mode: "Review candidates for React Developer role"
- Verify UI renders job cards correctly

---

## Day 3: Testing & Deployment (8-10 hours)

### Morning: Local Testing & Bug Fixes (3 hours)

- Test all MCP tools locally
- Test ADK agent routing
- Test frontend UI components
- Fix any integration issues
- Verify Supabase queries work with real data
- Test JSearch fallback when Supabase unavailable

### Afternoon: Cloud Run Deployment (5 hours)

**Create deployment files:**

- `mcp_server/staffing_backend/Dockerfile` (lines 1209-1230)
- Update `.env` with all credentials:
  - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
  - `JSEARCH_HOST`, `JSEARCHRAPDKEY`
  - `STAFFING_MCP_SERVER_URL`

**Deploy to Cloud Run:**

```bash
cd mcp_server/staffing_backend
gcloud builds submit --tag gcr.io/baseshare/staffing-backend --project baseshare
gcloud run deploy staffing-backend \
  --image gcr.io/baseshare/staffing-backend \
  --platform managed \
  --region us-central1 \
  --project baseshare \
  --allow-unauthenticated \
  --port 8100 \
  --set-env-vars "SUPABASE_URL=${SUPABASE_URL},SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY},JSEARCH_HOST=${JSEARCH_HOST},JSEARCHRAPDKEY=${JSEARCHRAPDKEY}"
```

**Update ADK backend:**

- Set `STAFFING_MCP_SERVER_URL` environment variable
- Test agent calls to deployed MCP server

**Final verification:**

- Test recruiter workflow end-to-end in production
- Test employer workflow end-to-end in production
- Verify JSearch fallback works
- Check Cloud Run logs for errors

---

## Critical Success Factors

1. **Database first**: Ensure all tables exist before building tools
2. **Test incrementally**: Test each MCP tool before moving to agents
3. **Use existing schema**: Don't modify `job_flow` or `resume_submissions` structure
4. **Fallback priority**: JSearch API must work when Supabase pauses
5. **Error handling**: All tools must handle missing data gracefully

## Risk Mitigation

- If MCP tools take longer: Defer non-critical features (employer management tool)
- If frontend integration lags: Use basic JSON rendering, enhance later
- If Cloud Run deployment fails: Test locally first, fix issues before deploying

## Deliverables by End of Day 3

- Working MCP server on Cloud Run
- Recruiter mode: Job search → Candidate matching → Submission
- Employer mode: Candidate review → Interview scheduling
- Frontend UI with job cards and action buttons
- JSearch API fallback operational
- All credentials configured and tested

Investigating Weave tracing and creating a test script to validate it. 


The Weave tracing implementation uses the wrong API. Weave uses `@weave.op()` decorators, not `weave.log()`. Fixing the implementation and updating the test script:


Remove emojis from the test script to avoid Unicode issues:


## Weave tracing fixes

### Issues found
1. Incorrect Weave initialization: `weave.init()` was called with an `entity` parameter, which it doesn't accept.
2. Wrong API usage: The code tried to use `weave.log()` which doesn't exist.
3. Missing wandb initialization: Weave requires an active wandb run.

### Fixes applied
1. Fixed Weave initialization:
   - Removed `entity` parameter from `weave.init()` (entity is handled by wandb)
   - Ensured wandb is initialized before Weave

2. Updated span export:
   - Switched to `weave.log_call()` with correct parameters (`op`, `inputs`, `output`, `attributes`)
   - Added fallback to `wandb.log()` if `weave.log_call()` is unavailable

3. Test script:
   - Created `test_weave_simple.py` that validates the setup
   - Test passes and successfully logs traces to Weave

### Test results
The test script confirms:
- Weave exporter initializes successfully
- OpenTelemetry spans are created
- Spans are exported to Weave using `weave.log_call()`
- Traces are visible at: https://wandb.ai/godutch/workflo/weave

### Next steps
1. Check the Weave dashboard: https://wandb.ai/godutch/workflo/weave
2. Run the test: `uv run python test_weave_simple.py`
3. Enable debug mode: Set `WEAVE_DEBUG=true` in your `.env` for detailed logs

The Weave tracing implementation is now working and will display traces on the Weave dashboard when your agents run.