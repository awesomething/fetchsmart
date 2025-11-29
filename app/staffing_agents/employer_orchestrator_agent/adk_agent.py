"""
ADK Employer Orchestrator Agent

Orchestrates employer workflow: candidate review → interview scheduling → hiring decisions
Converts from supplier workflow to employer workflow.
"""
import logging
from google.adk.agents import LlmAgent
from app.config import config

# Import sub-agents
from app.staffing_agents.candidate_review_agent.agent import create_agent as create_review_agent
from app.staffing_agents.interview_scheduling_agent.agent import create_agent as create_scheduling_agent

logger = logging.getLogger(__name__)

def get_employer_orchestrator_agent() -> LlmAgent:
    """Lazy initialization of employer orchestrator with graceful degradation."""
    sub_agents = []
    
    # Create sub-agents with error handling - continue even if some fail
    try:
        review_agent = create_review_agent()
        logger.info(f"✅ Review agent created: {review_agent.name}")
        sub_agents.append(review_agent)
    except Exception as e:
        logger.warning(f"⚠️  Failed to create review_agent: {e}")
        logger.warning("⚠️  Continuing without review agent")
    
    try:
        scheduling_agent = create_scheduling_agent()
        logger.info(f"✅ Scheduling agent created: {scheduling_agent.name}")
        sub_agents.append(scheduling_agent)
    except Exception as e:
        logger.warning(f"⚠️  Failed to create scheduling_agent: {e}")
        logger.warning("⚠️  Continuing without scheduling agent")
    
    # If no sub-agents were created, that's a problem
    if not sub_agents:
        raise RuntimeError("Failed to create any sub-agents for employer orchestrator")
    
    return LlmAgent(
        name="StaffingEmployerOrchestrator",
        model=config.model,
        description="Orchestrates employer workflow: candidate review → interview scheduling → hiring decisions",
        sub_agents=sub_agents,
        instruction="""
You coordinate the employer workflow through specialized agents:

1. Candidate Review: Evaluate submitted candidates
   - Delegate to CandidateReviewAgent to assess candidate submissions
   - Review candidate profiles, GitHub activity, LinkedIn experience
   - Compare candidate skills against job requirements
   - Generate shortlists for interviews

2. Interview Scheduling: Manage interview pipeline
   - Delegate to InterviewSchedulingAgent to coordinate interviews
   - Track candidates through hiring stages (screening, technical, cultural fit)
   - Send interview confirmations and feedback requests
   - Update pipeline status

**Workflow Examples:**

"Review candidates for React Developer role" → Use CandidateReviewAgent
"Schedule technical interview for John Doe" → Use InterviewSchedulingAgent
"Show hiring pipeline status" → Use InterviewSchedulingAgent
"Process new candidate submissions" → Coordinate both agents

**Decision Logic:**
- If user wants to review candidates → Use CandidateReviewAgent
- If user wants to schedule interviews → Use InterviewSchedulingAgent
- If user asks about hiring status → Use InterviewSchedulingAgent
- If user wants full employer workflow → Coordinate both agents

Ensure candidates progress efficiently through the hiring pipeline.
Maintain clear communication with recruiters about candidate status.
""",
        output_key="employer_workflow_result",
    )

# Create at module level for backward compatibility, but with error handling
# This allows the agent to be imported even if initialization fails
try:
    employer_orchestrator_agent = get_employer_orchestrator_agent()
    logger.info("✅ Employer orchestrator agent initialized successfully")
except Exception as e:
    logger.warning(f"⚠️  Failed to initialize employer orchestrator agent at import time: {e}")
    logger.warning("⚠️  This is OK - agent will work with available sub-agents when deployed")
    # Create a minimal placeholder agent that won't crash
    employer_orchestrator_agent = LlmAgent(
        name="StaffingEmployerOrchestrator",
        model=config.model,
        description="Employer orchestrator (some sub-agents unavailable)",
        instruction="The employer orchestrator is partially initialized. Some features may be limited.",
        output_key="employer_workflow_result",
    )

