# Multi-Agent Architecture with Google ADK

## Overview

This application implements a **multi-agent system** following Google ADK best practices as described in the [official blog post](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk).

Instead of a single "super agent" trying to do everything, we have a team of specialized agents coordinated by a root agent.

## Architecture Pattern

```
User Query
     ↓
Root Agent (Coordinator)
     ├── Analyzes Intent
     ├── Routes to Specialist
     ↓
┌────────────────────────────────────────────┐
│  Specialized Agents                        │
│                                            │
│  • Planning Agent                          │
│    - Goal decomposition                    │
│    - Task breakdown                        │
│    - Strategic planning                    │
│                                            │
│  • Q&A Agent                              │
│    - Google Docs search                    │
│    - Document reading                      │
│    - Cited answers                         │
│                                            │
│  • Recruiter Orchestrator                  │
│    - Candidate search                       │
│    - GitHub sourcing                       │
│    - Pipeline metrics                      │
│                                            │
│  • Recruiter Email Pipeline                │
│    - Outreach email generation             │
│    - Email refinement                      │
│                                            │
│  • Staffing Recruiter Orchestrator         │
│    - Job search                            │
│    - Candidate matching                    │
│                                            │
│  • Staffing Employer Orchestrator         │
│    - Candidate review                      │
│    - Interview scheduling                  │
└────────────────────────────────────────────┘
     ↓
Response to User
```

## Why Multi-Agent?

### ❌ Problems with Monolithic Agents

1. **Instruction overload**: Too many capabilities confuse the model
2. **Inaccurate outputs**: Jack of all trades, master of none
3. **Brittle systems**: Hard to debug and improve
4. **Poor scaling**: Adding features degrades existing functionality

### ✅ Benefits of Multi-Agent Systems

1. **Specialization**: Each agent is an expert in its domain
2. **Higher fidelity**: Focused agents produce better results
3. **Better control**: Easy to improve individual agents
4. **True scalability**: Add new agents without breaking existing ones
5. **Clear boundaries**: Separation of concerns

## Implementation Details

### 1. Specialized Agents

#### Planning Agent
**File:** `app/agent.py` - `planning_agent`

**Purpose:** Goal planning and task decomposition

**Capabilities:**
- Analyzes user goals
- Breaks down complex goals into tasks
- Creates subtasks with dependencies
- Provides execution plans

**When to use:**
- "Plan a marketing campaign"
- "How do I build a mobile app?"
- "Create a project timeline"
- "Break down: Launch a product"

**Technology:**
- Uses `BuiltInPlanner` from ADK
- Thinking enabled (`include_thoughts=True`)
- Structured output format

#### Q&A Agent
**File:** `app/agent.py` - `qa_agent`

**Purpose:** Answer questions from Google Docs

**Capabilities:**
- Searches Google Drive for documents
- Reads full document content
- Provides cited answers
- Summarizes documents

**When to use:**
- "What is our deployment process?"
- "Summarize the architecture document"
- "What documents are available?"
- "How do we handle SSL certificates?"

**Technology:**
- Uses Google Drive API tools
- Three tools: `search_google_docs`, `read_google_doc`, `list_recent_docs`
- Thinking enabled for complex queries

#### Recruiter Orchestrator
**File:** `app/recruiter_agents/recruiter_orchestrator_agent/adk_agent.py`

**Purpose:** Candidate search, GitHub sourcing, pipeline metrics, compensation checks

**Capabilities:**
- Searches for candidates using AI-powered matching
- Scrapes GitHub profiles for recruitment sourcing
- Provides pipeline metrics and analytics
- Checks compensation data and market rates

**When to use:**
- "Find 8 senior React engineers"
- "Show me sourced vs advanced metrics"
- "Check compensation rates for Python developers"

**Technology:**
- Uses MCP tools: `search_candidates_tool`, `scrape_github_profiles_tool`, `analyze_portfolio_tool`
- Connects to recruitment backend MCP server

#### Recruiter Email Pipeline
**File:** `app/recruiter_agents/candidate_operations_orchestrator/agent.py`

**Purpose:** Generate, review, and refine recruiter outreach emails

**Capabilities:**
- Generates personalized outreach emails
- Reviews and refines emails through iterative loop
- Enhances emails with candidate context (GitHub profiles, experience)

**When to use:**
- "Write an outreach email for candidate X"
- "Refine the candidate email with GitHub context"
- "Review this email and improve it"

**Technology:**
- Multi-agent loop: Email Generator → Email Reviewer → Email Refiner → Email Presenter
- Uses candidate data and GitHub profiles for personalization

#### Staffing Recruiter Orchestrator
**File:** `app/staffing_agents/recruiter_orchestrator_agent/adk_agent.py`

**Purpose:** Staffing agency recruiter workflow (job search → candidate matching → submission)

**Capabilities:**
- Searches for open job positions
- Matches candidates to job openings
- Submits candidates to employers

**When to use:**
- "Find React developer jobs"
- "Match candidates to this role"
- "Submit John for Senior Frontend position"

**Technology:**
- Uses job search and candidate matching tools
- Coordinates with Staffing Employer Orchestrator

#### Staffing Employer Orchestrator
**File:** `app/staffing_agents/employer_orchestrator_agent/adk_agent.py`

**Purpose:** Client company employer workflow (candidate review → interview scheduling)

**Capabilities:**
- Reviews submitted candidates against job requirements
- Coordinates interview scheduling
- Tracks candidates through hiring pipeline

**When to use:**
- "Review candidates for DevOps role"
- "Schedule interview with Jane"
- "Show hiring pipeline status"

**Technology:**
- Uses candidate review and interview scheduling tools
- Manages hiring pipeline status

### 2. Root Agent (Coordinator)

**File:** `app/agent.py` - `root_agent`

**Purpose:** Intelligent request router

**How it works:**
1. **Receives** user request
2. **Analyzes** the intent (planning vs. documentation)
3. **Routes** to the appropriate specialist
4. **Returns** the specialist's response

**Routing Logic:**
```python
User Request → Intent Analysis
                   ↓
        ┌──────────┴──────────┐
        │                     │
    Planning?             Q&A?
        │                     │
        ↓                     ↓
Planning Agent          Q&A Agent
        │                     │
    Recruiter?          Email?
        │                     │
        ↓                     ↓
RecruiterOrch        EmailPipeline
        │                     │
    Staffing?         Employer?
        │                     │
        ↓                     ↓
StaffingRec          StaffingEmp
        │                     │
        └──────────┬──────────┘
                   ↓
          Response to User
```

**Key Pattern:** Uses `sub_agents` parameter from ADK
```python
root_agent = LlmAgent(
    name="RootAgent",
    sub_agents=[
        planning_agent,
        qa_agent,
        recruiter_orchestrator_agent,
        recruiter_email_agent,
        staffing_recruiter_agent,
        employer_orchestrator_agent,
    ],
    instruction="Route requests to specialists...",
)
```

## How Requests Are Routed

### Planning Requests
**Indicators:**
- Keywords: "plan", "create", "build", "design", "strategy"
- Questions about "how to do" something
- Requests for step-by-step guidance

**Example Queries:**
- "Plan a data migration project"
- "How do I set up a CI/CD pipeline?"
- "Create a go-to-market strategy"

**Routed to:** `PlanningAgent`

**Response Format:**
```markdown
## Goal Analysis
[Understanding of the goal]

## Task Breakdown
### Task 1: [Name]
- Description
- Subtasks
- Success criteria
- Dependencies

## Execution Plan
[Step-by-step plan]

## Next Steps
[Immediate actions]
```

### Q&A Requests
**Indicators:**
- Questions about existing documentation
- Requests to search or summarize
- "What", "Where", "When" questions about docs

**Example Queries:**
- "What is our security policy?"
- "Summarize the API documentation"
- "Where can I find deployment instructions?"

**Routed to:** `QAAgent`

**Response Format:**
```markdown
**Answer:** [Answer from documents]

**Source(s):**
- [Document Name] (link)

**Key Points:**
- [Detail 1]
- [Detail 2]
```

### Recruiter Requests
**Indicators:**
- Keywords: "find candidates", "source", "GitHub", "pipeline", "metrics"
- Requests for candidate search or sourcing

**Example Queries:**
- "Find 8 senior React engineers"
- "Show me sourced vs advanced metrics"
- "Check compensation rates for Python developers"

**Routed to:** `RecruiterOrchestrator`

### Email Requests
**Indicators:**
- Keywords: "email", "outreach", "message", "draft", "refine"
- Requests for email generation or improvement

**Example Queries:**
- "Write an outreach email for candidate X"
- "Refine the candidate email with GitHub context"
- "Review this email and improve it"

**Routed to:** `RecruiterEmailPipeline`

### Staffing Recruiter Requests
**Indicators:**
- Keywords: "job search", "match candidates", "submit", "staffing"
- Requests from staffing agency recruiters

**Example Queries:**
- "Find React developer jobs"
- "Match candidates to this role"
- "Submit John for Senior Frontend position"

**Routed to:** `StaffingRecruiterOrchestrator`

### Staffing Employer Requests
**Indicators:**
- Keywords: "review candidate", "schedule interview", "hiring pipeline", "employer"
- Requests from client companies

**Example Queries:**
- "Review candidates for DevOps role"
- "Schedule interview with Jane"
- "Show hiring pipeline status"

**Routed to:** `StaffingEmployerOrchestrator`

## User Experience

### Automatic Routing
The system automatically determines which agent to use based on the query. Users don't need to specify which mode they want.

**Planning Example:**
```
User: "Plan a marketing campaign for a new product launch"
System: [Routes to Planning Agent]
Response: Detailed task breakdown with execution plan
```

**Q&A Example:**
```
User: "What is our deployment process?"
System: [Routes to Q&A Agent]
Response: Answer from documentation with citations
```

### UI Indicators
The landing page shows examples of both types of queries:
- 🟢 **Green badges**: Planning queries
- 🔵 **Blue badges**: Q&A queries

This helps users understand the system's capabilities.

## Technical Implementation

### ADK Sub-Agent Pattern

Following the [Google ADK blog post](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk), we use the `sub_agents` parameter:

```python
# Create specialized agents
planning_agent = LlmAgent(name="PlanningAgent", ...)
qa_agent = LlmAgent(name="QAAgent", ...)

# Create coordinator with sub-agents
root_agent = LlmAgent(
    name="Coordinator",
    sub_agents=[planning_agent, qa_agent],
    instruction="Analyze requests and route to specialists"
)
```

**Key Behavior:**
- When root agent calls a sub-agent, **responsibility is transferred**
- The sub-agent handles the request completely
- The root agent passes the sub-agent's response to the user

### Alternative Pattern: Agent Tools (Not Used Here)

The blog post also describes using agents as tools:

```python
# Convert agents to tools (alternative approach)
planning_tool = agent_tool.AgentTool(agent=planning_agent)
qa_tool = agent_tool.AgentTool(agent=qa_agent)

root_agent = LlmAgent(
    name="Coordinator",
    tools=[planning_tool, qa_tool],
    instruction="Use tools to complete multi-step workflows"
)
```

**Difference:**
- **Sub-agents**: Request is delegated completely
- **Agent tools**: Root agent orchestrates multi-step workflows

**Our choice:** We use **sub-agents** because each request typically needs only one specialist.

## Adding New Agents

To add a new specialized agent:

### 1. Define the Agent

```python
# In app/agent.py
new_specialist_agent = LlmAgent(
    name="SpecialistAgent",
    model=config.model,
    description="Specialized agent for X",
    tools=[...],  # Optional tools
    instruction="""
    You are a specialist in X...
    """,
    output_key="specialist_output",
)
```

### 2. Add to Root Agent

```python
root_agent = LlmAgent(
    name=config.internal_agent_name,
    sub_agents=[
        planning_agent,
        qa_agent,
        recruiter_orchestrator_agent,
        recruiter_email_agent,
        staffing_recruiter_agent,
        employer_orchestrator_agent,
        new_specialist_agent,  # Add here
    ],
    instruction=f"""
    ...existing routing logic...
    
    7. **SpecialistAgent**: For X-related queries
       - Use when user asks about X
       - Examples: "..."
    """,
)
```

### 3. Update UI (Optional)

Add examples to `EmptyState.tsx`:
```typescript
<span className="px-3 py-1 bg-yellow-700/30 text-yellow-300 ...">
  Example query for new agent
</span>
```

## Best Practices

### 1. Clear Agent Boundaries
Each agent should have a **single, well-defined responsibility**:
- ✅ Good: "Planning Agent" for all planning tasks
- ❌ Bad: "General Helper Agent" that does everything

### 2. Explicit Routing Instructions
Give the coordinator **clear rules** for routing:
```python
instruction="""
Use PlanningAgent when:
- User wants to plan something
- User asks "how to do X"
- User needs strategic guidance

Use QAAgent when:
- User asks about documentation
- User wants to search docs
- User needs factual information from docs
"""
```

### 3. Thinking Enabled
Enable `include_thoughts=True` for **transparency**:
- Users see which agent was chosen
- Users see the agent's reasoning process
- Easier to debug routing decisions

### 4. Consistent Output Formats
Each agent should have a **predictable structure**:
- Planning: Always uses "Goal Analysis", "Task Breakdown", etc.
- Q&A: Always cites sources

## Monitoring & Debugging

### Activity Timeline
The UI's activity timeline shows:
- Which agent was invoked
- What tools were called
- The agent's thinking process

**Example:**
```
[RootAgent] Analyzing request...
[RootAgent] This is a Q&A question, routing to QAAgent
[QAAgent] Searching for documents about "deployment"
[QAAgent] Tool call: search_google_docs("deployment")
[QAAgent] Found 3 documents, reading most relevant...
[QAAgent] Tool call: read_google_doc("1abc...")
[QAAgent] Generating answer with citation...
```

### Question Logging
The `question_logger` tracks which agent handled each request:
```json
{
  "question": "What is our deployment process?",
  "agent_used": "QAAgent",
  "documents_accessed": ["Deployment Guide"],
  "timestamp": "2025-10-30T..."
}
```

## Future Enhancements

### Parallel Execution
For independent tasks, use `ParallelAgent`:

```python
from google.adk.agents import ParallelAgent

# Run multiple agents concurrently
parallel_agent = ParallelAgent(
    name="ParallelCoordinator",
    sub_agents=[agent1, agent2, agent3],
)
```

### Sequential Workflows
For multi-step processes, use `SequentialAgent`:

```python
from google.adk.agents import SequentialAgent

# Execute agents in order
workflow = SequentialAgent(
    name="Workflow",
    sub_agents=[step1_agent, step2_agent, step3_agent],
)
```

### Feedback Loops
Add review agents that validate outputs:

```python
review_agent = LlmAgent(
    name="ReviewAgent",
    instruction="Review the output and provide feedback",
)

workflow = SequentialAgent(
    sub_agents=[main_agent, review_agent, validator_agent],
)
```

## References

- **Google ADK Blog Post**: [How to build a simple multi-agentic system using Google's ADK](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk)
- **ADK Documentation**: [Agent Development Kit Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/overview)
- **This Implementation**: `app/agent.py`

## Summary

✅ **What we built:**
- Multi-agent system with 6 specialists:
  - Planning Agent (goal planning & task decomposition)
  - Q&A Agent (Google Docs search)
  - Recruiter Orchestrator (candidate search, GitHub sourcing)
  - Recruiter Email Pipeline (outreach email generation)
  - Staffing Recruiter Orchestrator (job search, candidate matching)
  - Staffing Employer Orchestrator (candidate review, interview scheduling)
- Root agent coordinator that intelligently routes requests
- Clean separation of concerns
- Production-ready architecture

✅ **Benefits:**
- Better accuracy (specialized agents)
- Easier to maintain (modular design)
- Scalable (add agents without breaking existing ones)
- Transparent (users see which agent handled their request)

✅ **Next steps:**
- Start the app: `make dev`
- Try planning queries: "Plan a marketing campaign"
- Try Q&A queries: "What is our deployment process?"
- Try recruiter queries: "Find 8 senior React engineers"
- Try email queries: "Write an outreach email for candidate X"
- Watch the activity timeline to see routing in action

