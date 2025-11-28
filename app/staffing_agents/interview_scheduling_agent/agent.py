"""
Interview Scheduling Agent - Sub-agent for managing interview pipeline.
Replaces production_queue_management_agent from supply chain.
"""
import logging
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are an Interview Scheduling Agent specialized in managing the hiring pipeline. "
    "Your primary responsibilities include: "
    "1. Tracking candidates through hiring stages (screening, technical-interview, cultural-fit, offer, hired) "
    "2. Updating pipeline status and stage information "
    "3. Managing interview schedules and feedback "
    "4. Providing pipeline status reports "
    "\n\n**IMPORTANT - Available Tools:**"
    "\n- Use 'get_pipeline_status' to view pipeline status"
    "\n- Use 'update_pipeline_stage' to update candidate stages"
    "\n\n**Pipeline Workflow:**"
    "\nWhen managing the pipeline:"
    "\n- Use 'get_pipeline_status' with optional job_opening_id to view pipeline"
    "\n- Use 'update_pipeline_stage' to move candidates through stages:"
    "\n  - submission_id=<integer submission ID>"
    "\n  - new_stage=<screening|technical-interview|cultural-fit|offer|hired>"
    "\n  - stage_status=<pending|in-progress|completed|rejected>"
    "\n  - feedback=<interview feedback or notes>"
    "\n\n**Response Format:**"
    "\nAlways provide:"
    "\n- Current pipeline stage for each candidate"
    "\n- Total candidates in pipeline"
    "\n- Candidates grouped by stage"
    "\n- Updated status after changes"
    "\n\nEnsure candidates progress efficiently through the hiring pipeline."
)

def create_agent() -> LlmAgent:
    """Constructs the ADK interview scheduling agent."""
    logger.info("--- 🔧 Loading MCP tools from Staffing Backend... ---")
    logger.info("--- 🤖 Creating ADK Interview Scheduling Agent... ---")
    
    tools = []
    mcp_url = os.getenv("STAFFING_MCP_SERVER_URL", "http://localhost:8100/mcp")
    
    try:
        tools.append(
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(url=mcp_url),
                tool_filter=["get_pipeline_status", "update_pipeline_stage"]
            )
        )
        logger.info(f"✅ MCP tools configured: {mcp_url}")
        logger.info("✅ Available MCP tools: get_pipeline_status, update_pipeline_stage")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP tools: {e}")
        logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
    
    return LlmAgent(
        model="gemini-2.0-flash-exp",
        name="interview_scheduling_agent",
        description="An agent that manages the hiring pipeline and interview scheduling",
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )

