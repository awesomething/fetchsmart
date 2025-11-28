"""
Talent Analytics Orchestrator Agent

This agent orchestrates and coordinates the workflow between analytics-focused agents using
the ADK (Agent Development Kit) framework with A2A (Agent-to-Agent) communication protocol.

Architecture:
- Built on google.adk.Agent with LLM capabilities
- Uses A2AClient and A2ACardResolver for agent discovery and communication
- Implements RemoteAgentConnections for managing analytics agent connections

Capabilities:
- Orchestrate the analytics workflow: compensation analysis → productivity tracking
- Manage A2A communication between compensation and productivity agents
- Ensure proper data flow and context sharing between analytics agents
- Provide comprehensive reports on compensation and productivity insights

A2A Agent Connections:
- Compensation Agent (localhost:8107): Salary benchmarking and compensation analysis
- Recruiter Productivity Agent (localhost:8108): Time tracking and productivity analytics

Workflows:
1. Full Analytics Workflow:
   - Compensation Agent: Analyzes salary benchmarks and competitive positioning
   - Recruiter Productivity Agent: Tracks time allocation and productivity metrics

2. Compensation Only Workflow:
   - Compensation Agent analysis only

Tools Available:
- send_message: Send structured messages to other agents
- execute_analytics_workflow: Orchestrate complete analytics analysis
- execute_compensation_workflow: Execute compensation analysis only

Environment Variables:
- COMPENSATION_AGENT_URL: URL for Compensation Agent (default: http://localhost:8107)
- RECRUITER_PRODUCTIVITY_AGENT_URL: URL for Recruiter Productivity Agent (default: http://localhost:8108)
- GOOGLE_API_KEY: API key for Google Gemini model
- MODEL_NAME: Model name (default: gemini-2.0-flash-exp)

Usage:
Run this agent on port 8106 to coordinate talent analytics through A2A protocol.
"""

