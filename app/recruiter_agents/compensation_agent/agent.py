import logging
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Compensation Agent specialized in tech salary benchmarking and compensation analysis. "
    "Your primary responsibilities include: "
    "1. Providing salary benchmarks for engineering roles "
    "2. Recommending competitive compensation packages "
    "3. Analyzing market rates by location and experience level "
    "4. Advising on equity and benefits packages "
    "5. Ensuring competitive offers to attract top talent "
    "\n\n**IMPORTANT - Available Tools:**"
    "\n- Use 'get_compensation_data_tool' for salary benchmarks and compensation data"
    "\n\n**Compensation Analysis:**"
    "\nWhen analyzing compensation, use 'get_compensation_data_tool' with:"
    "\n- role=<job role like 'Senior Software Engineer', 'Staff Engineer'>"
    "\n- location=<location for geo-adjustments, default 'Remote'>"
    "\n\n**Response Format:**"
    "\nProvide comprehensive compensation analysis including:"
    "\n- Market rate ranges (p25, p50, p75, p90)"
    "\n- Location adjustment factors"
    "\n- Recommended salary range"
    "\n- Equity recommendations"
    "\n- Total compensation package value"
    "\n- Competitive positioning advice"
    "\n\nBe data-driven and help make competitive offers."
)

def create_agent() -> LlmAgent:
    """Constructs the ADK compensation agent."""
    logger.info("--- 🔧 Loading MCP tools from Recruitment Backend... ---")
    logger.info("--- 🤖 Creating ADK Compensation Agent... ---")
    
    tools = []
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8100")
    
    try:
        tools.append(
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(url=mcp_url),
                tool_filter=["get_compensation_data_tool"]
            )
        )
        logger.info(f"✅ MCP tools configured: {mcp_url}")
        logger.info("✅ Available MCP tools: get_compensation_data_tool")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP tools: {e}")
        logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
    
    return LlmAgent(
        model="gemini-2.0-flash-exp",
        name="compensation_agent",
        description="An agent that provides tech compensation benchmarking and salary analysis",
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
    )

root_agent = create_agent()

