"""
Recruiter Orchestrator Agent

This is the root orchestrator agent for the recruitment system, coordinating between
Candidate Operations and Talent Analytics orchestrators.

Architecture:
- Built on google.adk.Agent with LLM capabilities
- Uses A2AClient and A2ACardResolver for agent discovery and communication
- Implements RemoteAgentConnections for managing sub-orchestrator connections

Capabilities:
- Orchestrate complete recruitment workflows
- Manage A2A communication between candidate operations and talent analytics
- Coordinate multi-stage recruitment processes
- Provide comprehensive recruitment reports

A2A Agent Connections:
- Candidate Operations Orchestrator (localhost:8102): Manages sourcing, screening, portfolio
- Talent Analytics Orchestrator (localhost:8106): Manages compensation and productivity

Workflows:
1. Full Recruitment Workflow:
   - Candidate Operations: Source → Screen → Portfolio
   - Talent Analytics: Compensation → Productivity

2. Candidate Operations Only:
   - Focus on candidate workflow only

3. Talent Analytics Only:
   - Focus on analytics workflow only

Tools Available:
- send_message: Send structured messages to sub-orchestrators
- execute_full_recruitment_workflow: Complete end-to-end recruitment
- execute_candidate_operations: Candidate workflow only
- execute_talent_analytics: Analytics workflow only

Environment Variables:
- CANDIDATE_OPS_ORCHESTRATOR_URL: URL for Candidate Ops Orchestrator (default: http://localhost:8102)
- TALENT_ANALYTICS_ORCHESTRATOR_URL: URL for Talent Analytics Orchestrator (default: http://localhost:8106)
- GOOGLE_API_KEY: API key for Google Gemini model
- MODEL_NAME: Model name (default: gemini-2.0-flash-exp)

Usage:
Run this agent on port 8101 to coordinate all recruitment operations through A2A protocol.
"""

