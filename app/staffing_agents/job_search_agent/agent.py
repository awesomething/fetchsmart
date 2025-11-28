"""
Job Search Agent - Sub-agent for querying job openings from Supabase.
Replaces inventory_management_agent from supply chain.
"""
import logging
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Job Search Agent specialized in finding job openings from Supabase database with JSearch API fallback. "
    "Your primary responsibilities include: "
    "1. Searching job openings by title, location, salary range, and remote options "
    "2. Filtering jobs based on tech stack, experience level, and work type "
    "3. Providing detailed job information including salary, location, and application links "
    "4. Handling fallback to JSearch API when Supabase is unavailable "
    "\n\n**IMPORTANT - Available Tools:**"
    "\n- Use 'search_jobs' tool to query job openings"
    "\n\n**Search Workflow:**"
    "\nWhen searching for jobs, use 'search_jobs' with:"
    "\n- job_title=<search term in job title>"
    "\n- location=<job location, or leave empty for remote>"
    "\n- min_salary=<minimum salary filter>"
    "\n- max_salary=<maximum salary filter>"
    "\n- remote_only=<true/false>"
    "\n- limit=<number of results>"
    "\n\n**Error Handling:**"
    "\nIf the search_jobs tool fails or times out, provide a helpful error message to the user explaining that the job search service is temporarily unavailable and suggest they try again later."
    "\n\n**Response Format:**"
    "\nAlways provide:"
    "\n- Total number of jobs found"
    "\n- Job titles and locations"
    "\n- Salary ranges when available"
    "\n- Application links"
    "\n- Data source (Supabase or JSearch API)"
    "\n\nBe thorough and provide all relevant job details."
)

def create_agent() -> LlmAgent:
    """Constructs the ADK job search agent."""
    logger.info("--- 🔧 Loading MCP tools from Staffing Backend... ---")
    logger.info("--- 🤖 Creating ADK Job Search Agent... ---")
    
    tools = []
    mcp_url = os.getenv("STAFFING_MCP_SERVER_URL", "http://localhost:8100/mcp")
    
    try:
        mcp_toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(url=mcp_url),
            tool_filter=["search_jobs"]
        )
        tools.append(mcp_toolset)
        logger.info(f"✅ MCP tools configured: {mcp_url}")
        logger.info("✅ Available MCP tools: search_jobs")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP tools: {e}")
        logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        logger.warning("⚠️  Agent will continue without MCP tools - job search will be limited")
    
    return LlmAgent(
        model="gemini-2.0-flash-exp",
        name="job_search_agent",
        description="An agent that searches job openings from Supabase with JSearch API fallback",
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )

