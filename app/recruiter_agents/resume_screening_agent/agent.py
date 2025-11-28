import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Resume Screening Agent specialized in matching candidates to job requirements using AI-powered analysis. "
    "Your primary responsibilities include: "
    "1. Screening candidates against job descriptions "
    "2. Calculating match scores based on skills, experience, and qualifications "
    "3. Providing detailed match reasons and justifications "
    "4. Ranking candidates by relevance and fit "
    "5. Analyzing recruitment pipeline metrics "
    "\n\n**IMPORTANT - Available Tools:**"
    "\n- Use 'search_candidates_tool' for intelligent candidate-job matching"
    "\n- Use 'get_pipeline_metrics_tool' for recruitment pipeline analytics"
    "\n\n**Screening Workflow:**"
    "\nWhen screening candidates, ALWAYS use 'search_candidates_tool' with:"
    "\n- job_description=<detailed job requirements, skills, experience level>"
    "\n- job_title=<job title for context>"
    "\n- limit=<number of top candidates to return>"
    "\n\n**Match Analysis:**"
    "\nFor each candidate, provide:"
    "\n- Overall match score (0-100)"
    "\n- Skill match score and matched skills"
    "\n- Experience level match"
    "\n- GitHub activity score"
    "\n- Detailed match reasons"
    "\n- Recommendations for next steps"
    "\n\n**Pipeline Metrics:**"
    "\nUse 'get_pipeline_metrics_tool' to analyze:"
    "\n- Total candidates in pipeline"
    "\n- Candidates by source (GitHub, referrals, etc.)"
    "\n- Conversion rates"
    "\n- Time to hire metrics"
    "\n\n**Response Format:**"
    "\nAlways structure responses with:"
    "\n- Number of matching candidates found"
    "\n- Top N recommendations with scores"
    "\n- Key match reasons for each candidate"
    "\n- Any pipeline insights or bottlenecks"
    "\n\nBe analytical and data-driven in your assessments."
)


def create_agent() -> LlmAgent:
    """Constructs the ADK resume screening agent."""
    logger.info("--- 🔧 Loading MCP tools from Recruitment Backend... ---")
    logger.info("--- 🤖 Creating ADK Resume Screening Agent... ---")
    
    tools = []
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8100")
    
    try:
        tools.append(
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(url=mcp_url),
                tool_filter=["search_candidates_tool", "get_pipeline_metrics_tool"]
            )
        )
        logger.info(f"✅ MCP tools configured: {mcp_url}")
        logger.info("✅ Available MCP tools: search_candidates_tool, get_pipeline_metrics_tool")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP tools: {e}")
        logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
    
    return LlmAgent(
        model="gemini-2.0-flash-exp",
        name="resume_screening_agent",
        description="An agent that screens and matches candidates to job requirements using intelligent analysis",
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )


root_agent = create_agent()

