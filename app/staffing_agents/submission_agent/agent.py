"""
Submission Agent - Sub-agent for creating candidate submissions.
Replaces purchase_order_agent from supply chain.
"""
import logging
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Candidate Submission Agent specialized in creating candidate submission packages. "
    "Your primary responsibilities include: "
    "1. Creating candidate submissions for job openings "
    "2. Linking candidates to specific job positions "
    "3. Tracking submission status in the hiring pipeline "
    "4. Generating submission numbers and tracking metadata "
    "\n\n**IMPORTANT - Available Tools:**"
    "\n- Use 'create_candidate_submission' tool to create submissions"
    "\n\n**Submission Workflow:**"
    "\nWhen creating a submission, use 'create_candidate_submission' with:"
    "\n- job_opening_id=<integer job ID from job_flow table>"
    "\n- candidate_name=<candidate's full name>"
    "\n- candidate_email=<candidate's email>"
    "\n- candidate_github=<GitHub profile URL, optional>"
    "\n- candidate_linkedin=<LinkedIn profile URL, optional>"
    "\n- recruiter_id=<UUID of recruiter, optional>"
    "\n- match_score=<0.0-1.0 match score, optional>"
    "\n- notes=<additional notes, optional>"
    "\n\n**Response Format:**"
    "\nAlways provide:"
    "\n- Submission number (SUB-YYYYMMDD-XXXXXX)"
    "\n- Job opening ID and title"
    "\n- Candidate details"
    "\n- Submission status"
    "\n- Pipeline stage (automatically set to 'screening')"
    "\n\nEnsure all required fields are provided before creating submissions."
)

def create_agent() -> LlmAgent:
    """Constructs the ADK submission agent."""
    logger.info("--- 🔧 Loading MCP tools from Staffing Backend... ---")
    logger.info("--- 🤖 Creating ADK Submission Agent... ---")
    
    tools = []
    mcp_url = os.getenv("STAFFING_MCP_SERVER_URL", "http://localhost:8100/mcp")
    
    try:
        mcp_toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(url=mcp_url),
            tool_filter=["create_candidate_submission"]
        )
        tools.append(mcp_toolset)
        logger.info(f"✅ MCP tools configured: {mcp_url}")
        logger.info("✅ Available MCP tools: create_candidate_submission")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP tools: {e}")
        logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        logger.warning("⚠️  Agent will continue without MCP tools - submissions will be limited")
    
    return LlmAgent(
        model="gemini-2.0-flash-exp",
        name="submission_agent",
        description="An agent that creates candidate submissions for job openings",
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )

