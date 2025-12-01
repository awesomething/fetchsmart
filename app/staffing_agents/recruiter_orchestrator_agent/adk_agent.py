"""
ADK Recruiter Orchestrator Agent

Orchestrates recruiter workflow: job search → candidate matching → submission
Converts from buyer workflow to recruiter workflow.
"""
import logging
from google.adk.agents import LlmAgent
from app.config import config

# Import sub-agents
from app.staffing_agents.job_search_agent.agent import create_agent as create_job_search_agent
from app.staffing_agents.candidate_matching_agent.agent import create_agent as create_matching_agent
from app.staffing_agents.submission_agent.agent import create_agent as create_submission_agent

logger = logging.getLogger(__name__)

def get_recruiter_orchestrator_agent() -> LlmAgent:
    """Lazy initialization of recruiter orchestrator with graceful degradation."""
    sub_agents = []
    
    # Create sub-agents with error handling - continue even if some fail
    try:
        job_search_agent = create_job_search_agent()
        logger.info(f"[OK] Job search agent created: {job_search_agent.name}")
        sub_agents.append(job_search_agent)
    except Exception as e:
        logger.warning(f"[WARNING] Failed to create job_search_agent: {e}")
        logger.warning("[WARNING] Continuing without job search agent")
    
    try:
        matching_agent = create_matching_agent()
        logger.info(f"[OK] Matching agent created: {matching_agent.name}")
        sub_agents.append(matching_agent)
    except Exception as e:
        logger.warning(f"[WARNING] Failed to create matching_agent: {e}")
        logger.warning("[WARNING] Continuing without matching agent")
    
    try:
        submission_agent = create_submission_agent()
        logger.info(f"[OK] Submission agent created: {submission_agent.name}")
        sub_agents.append(submission_agent)
    except Exception as e:
        logger.warning(f"[WARNING] Failed to create submission_agent: {e}")
        logger.warning("[WARNING] Continuing without submission agent")
    
    # If no sub-agents were created, that's a problem
    if not sub_agents:
        raise RuntimeError("Failed to create any sub-agents for staffing recruiter orchestrator")
    
    try:
        return LlmAgent(
            name="StaffingRecruiterOrchestrator",
            model=config.model,
            description="Orchestrates recruiter workflow: job search → candidate matching → submission",
            sub_agents=sub_agents,
            instruction="""
You coordinate the recruiter workflow through specialized agents:

1. Job Search: Find open positions matching requirements
   - Delegate to JobSearchAgent to query job openings from Supabase
   - Filter by tech stack, location, work type, urgency, experience level
   - Review job descriptions and requirements

2. Candidate Matching: Match candidates to job requirements
   - Delegate to CandidateMatchingAgent to find suitable candidates
   - Use GitHub profiles to assess technical skills
   - Calculate match scores based on job requirements vs candidate skills
   - Rank candidates by relevance

3. Candidate Submission: Submit candidates to employers
   - Delegate to SubmissionAgent to create candidate submission packages
   - Generate personalized outreach emails to candidates
   - Track submission status in hiring pipeline
   - Coordinate employer communications

**Workflow Examples:**

"Find React developer jobs" → Use JobSearchAgent
"Match candidates to job SUB-20250120-123456" → Use CandidateMatchingAgent
"Submit candidate John Doe for Senior Frontend role" → Use SubmissionAgent
"Full recruiter workflow for DevOps positions" → Coordinate all three agents

**Decision Logic:**
- If user asks about available jobs → Use JobSearchAgent
- If user wants candidate recommendations → Use CandidateMatchingAgent
- If user wants to submit a candidate → Use SubmissionAgent
- If user wants end-to-end recruiting → Coordinate all agents sequentially

Always maintain context about job requirements, candidate profiles, and submission status.
Focus on finding the best candidate-job fit to maximize placement success.
""",
            output_key="recruiter_workflow_result",
        )
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize recruiter orchestrator: {e}")
        import traceback
        logger.error(f"[ERROR] Full traceback: {traceback.format_exc()}")
        # Return a minimal agent that will at least not crash
        return LlmAgent(
            name="StaffingRecruiterOrchestrator",
            model=config.model,
            description="Recruiter orchestrator (initialization failed - check logs)",
            instruction=f"The recruiter orchestrator failed to initialize. Error: {str(e)}. Please check the backend logs for details.",
            output_key="recruiter_workflow_result",
        )

# Lazy initialization - only create when actually needed
# This prevents import-time failures when MCP servers aren't available
def _get_staffing_recruiter_agent():
    """Lazy getter for staffing recruiter agent."""
    return get_recruiter_orchestrator_agent()

# Create at module level for backward compatibility, but with error handling
try:
    recruiter_orchestrator_agent = get_recruiter_orchestrator_agent()
except Exception as e:
    logger.warning(f"⚠️  Failed to initialize staffing recruiter agent at import time: {e}")
    logger.warning("⚠️  Agent will be created lazily when needed")
    # Create a placeholder that will be replaced when actually used
    recruiter_orchestrator_agent = None

