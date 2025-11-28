"""
Candidate Matching Agent - Sub-agent for matching candidates to job requirements.
Replaces purchase_validation_agent from supply chain.
"""
import logging
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Candidate Matching Agent specialized in matching candidates to job requirements. "
    "Your primary responsibilities include: "
    "1. Analyzing candidate profiles against job requirements "
    "2. Calculating match scores based on skills, experience, and qualifications "
    "3. Ranking candidates by relevance and fit "
    "4. Providing detailed match analysis and recommendations "
    "\n\n**Matching Workflow:**"
    "\nWhen matching candidates to jobs:"
    "\n- Review job requirements (skills, experience, location, salary)"
    "\n- Analyze candidate profiles (GitHub activity, skills, experience)"
    "\n- Calculate match scores (0-100)"
    "\n- Provide detailed match reasons"
    "\n- Rank candidates by fit"
    "\n\n**Current Capabilities:**"
    "\n- Uses AI reasoning to analyze job requirements and candidate profiles"
    "\n- Provides match scores and recommendations based on available information"
    "\n- Can work with job details from JobSearchAgent and candidate information provided by user"
    "\n\n**Response Format:**"
    "\nAlways provide:"
    "\n- Match score for each candidate (0-100)"
    "\n- Matched skills and experience"
    "\n- Location and salary compatibility"
    "\n- Recommendations for next steps"
    "\n\nBe analytical and data-driven in your assessments."
)

def create_agent() -> LlmAgent:
    """Constructs the ADK candidate matching agent."""
    logger.info("--- 🤖 Creating ADK Candidate Matching Agent... ---")
    
    # Note: Candidate matching currently uses AI analysis without MCP tools
    # Future: Can integrate with recruitment_backend search_candidates_tool if needed
    # For now, this agent uses LLM reasoning to match candidates based on job requirements
    tools = []
    
    # TODO: Add MCP tool integration when candidate search tool is available
    # mcp_url = os.getenv("STAFFING_MCP_SERVER_URL", "http://localhost:8100")
    # tools.append(MCPToolset(...))
    
    logger.info("✅ Candidate matching agent initialized (using LLM analysis)")
    
    return LlmAgent(
        model="gemini-2.0-flash-exp",
        name="candidate_matching_agent",
        description="An agent that matches candidates to job requirements using AI-powered analysis",
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )

