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
    "You are a Job Search Agent specialized in finding job openings from JSearch API with Supabase fallback. "
    "Your primary responsibilities include: "
    "1. Searching job openings by title, location, salary range, and remote options "
    "2. Filtering jobs based on tech stack, experience level, and work type "
    "3. Providing detailed job information including salary, location, and application links "
    "4. Handling fallback to Supabase when JSearch API is unavailable "
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
    "\n\n**Error Handling - CRITICAL:**"
    "\nWhen search_jobs tool returns status='error', you MUST:"
    "\n1. Read the 'message' field from the JSON response - this contains the EXACT error"
    "\n2. Read the 'error_details.suggestions' array - this contains actionable fixes"
    "\n3. Report the EXACT error message to the user - DO NOT use generic phrases like 'tool configuration issue'"
    "\n4. Include the suggestions from error_details.suggestions in your response"
    "\n5. Example error response format:"
    "\n   {"
    "\n     'status': 'error',"
    "\n     'message': 'Job search failed. JSEARCHRAPDKEY not configured; Supabase credentials not configured',"
    "\n     'error_details': {"
    "\n       'suggestions': ['Set JSEARCHRAPDKEY...', 'Set SUPABASE_URL...']"
    "\n     }"
    "\n   }"
    "\n6. When reporting errors, use this format:"
    "\n   'Job search failed: [EXACT MESSAGE FROM TOOL]'"
    "\n   'To fix this: [SUGGESTIONS FROM error_details.suggestions]'"
    "\n7. NEVER say 'tool configuration issue' or 'try again later' - always be specific"
    "\n\n**Response Format:**"
    "\n**CRITICAL**: After calling search_jobs tool, you MUST provide a comprehensive text summary."
    "\nDo NOT just return the tool result - analyze it and write a detailed response."
    "\n\nYour text response must include:"
    "\n- Total number of jobs found"
    "\n- List each job with: title, company, location, salary (if available)"
    "\n- Application links for each job"
    "\n- Data source (JSearch API or Supabase)"
    "\n\nExample response:"
    "\n'I found 5 React Developer jobs:"
    "\n\n1. Senior React Developer at TechCorp"
    "\n   Location: San Francisco, CA (Remote available)"
    "\n   Salary: $120k-$160k/year"
    "\n   Apply: https://jobs.com/12345"
    "\n\n2. React Engineer at StartupXYZ..."
    "\n\nBe thorough and provide all relevant job details in readable text format."
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
        description="An agent that searches job openings from JSearch API with Supabase fallback",
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )

