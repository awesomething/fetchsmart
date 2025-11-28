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
    """Lazy initialization of employer orchestrator."""
    try:
        # Create sub-agents with error handling
        try:
            review_agent = create_review_agent()
            logger.info(f"✅ Review agent created: {review_agent.name}")
        except Exception as e:
            logger.error(f"❌ Failed to create review_agent: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise
        
        try:
            scheduling_agent = create_scheduling_agent()
            logger.info(f"✅ Scheduling agent created: {scheduling_agent.name}")
        except Exception as e:
            logger.error(f"❌ Failed to create scheduling_agent: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise
        
        return LlmAgent(
            name="StaffingEmployerOrchestrator",
            model=config.model,
            description="Orchestrates employer workflow: candidate review → interview scheduling → hiring decisions",
            sub_agents=[review_agent, scheduling_agent],
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
    except Exception as e:
        logger.error(f"❌ Failed to initialize employer orchestrator: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        # Return a minimal agent that will at least not crash
        return LlmAgent(
            name="StaffingEmployerOrchestrator",
            model=config.model,
            description="Employer orchestrator (initialization failed - check logs)",
            instruction=f"The employer orchestrator failed to initialize. Error: {str(e)}. Please check the backend logs for details.",
            output_key="employer_workflow_result",
        )

employer_orchestrator_agent = get_employer_orchestrator_agent()

