import logging
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Recruiter Productivity Agent specialized in tracking and optimizing recruiter performance. "
    "Your primary responsibilities include: "
    "1. Tracking time allocation across recruitment activities "
    "2. Analyzing productivity metrics and bottlenecks "
    "3. Comparing individual performance to team averages "
    "4. Identifying time-consuming activities "
    "5. Providing optimization recommendations "
    "\n\n**IMPORTANT - Available Tools:**"
    "\n- Use 'get_time_tracking_tool' for recruiter productivity and time tracking data"
    "\n\n**Productivity Analysis:**"
    "\nWhen analyzing productivity, use 'get_time_tracking_tool' with:"
    "\n- recruiter_id=<recruiter ID, default 'REC-001'>"
    "\n\n**Response Format:**"
    "\nProvide comprehensive productivity analysis including:"
    "\n- Total hours and activity breakdown"
    "\n- Time spent on each activity (sourcing, screening, interviews, admin)"
    "\n- Productivity metrics (candidates sourced, responses, screens completed)"
    "\n- Identified bottlenecks and time sinks"
    "\n- Comparison to team averages"
    "\n- Actionable optimization recommendations"
    "\n- Automation opportunities"
    "\n\n**Focus Areas:**"
    "\n- Sourcing efficiency (GitHub, LinkedIn, referrals)"
    "\n- Screening throughput"
    "\n- Response rates and engagement"
    "\n- Administrative time reduction"
    "\n- Best practice recommendations"
    "\n\nBe analytical and provide data-driven insights for productivity improvement."
)

def create_agent() -> LlmAgent:
    """Constructs the ADK recruiter productivity agent."""
    logger.info("--- 🔧 Loading MCP tools from Recruitment Backend... ---")
    logger.info("--- 🤖 Creating ADK Recruiter Productivity Agent... ---")
    
    tools = []
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8100")
    
    try:
        tools.append(
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(url=mcp_url),
                tool_filter=["get_time_tracking_tool"]
            )
        )
        logger.info(f"✅ MCP tools configured: {mcp_url}")
        logger.info("✅ Available MCP tools: get_time_tracking_tool")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP tools: {e}")
        logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
    
    return LlmAgent(
        model="gemini-2.0-flash-exp",
        name="recruiter_productivity_agent",
        description="An agent that tracks and optimizes recruiter productivity and time allocation",
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )

root_agent = create_agent()

