# ruff: noqa: E501
# pylint: disable=logging-fstring-interpolation
import asyncio
import json
import os
import uuid
from typing import Any
import httpx
from a2a.client import A2ACardResolver
from a2a.types import (AgentCard, MessageSendParams, Part, SendMessageRequest, SendMessageResponse, SendMessageSuccessResponse, Task)
from remote_agent_connection import (RemoteAgentConnections, TaskUpdateCallback)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext

load_dotenv()

def create_send_message_payload(text: str, task_id: str | None = None, context_id: str | None = None) -> dict[str, Any]:
    """Helper function to create the payload for sending a task."""
    payload: dict[str, Any] = {'message': {'role': 'user', 'parts': [{'type': 'text', 'text': text}], 'messageId': uuid.uuid4().hex}}
    if task_id:
        payload['message']['taskId'] = task_id
    if context_id:
        payload['message']['contextId'] = context_id
    return payload

class RecruiterOrchestratorAgent:
    """The Recruiter Orchestrator agent - root coordinator for recruitment operations."""

    def __init__(self, task_callback: TaskUpdateCallback | None = None):
        self.task_callback = task_callback
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''

    async def _async_init_components(self, remote_agent_addresses: list[str]) -> None:
        """Asynchronous part of initialization."""
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(client, address)
                try:
                    card = await card_resolver.get_agent_card()
                    remote_connection = RemoteAgentConnections(agent_card=card, agent_url=address)
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                except httpx.ConnectError as e:
                    print(f'ERROR: Failed to get agent card from {address}: {e}')
                except Exception as e:
                    print(f'ERROR: Failed to initialize connection for {address}: {e}')
        agent_info = []
        for agent_detail_dict in self.list_remote_agents():
            agent_info.append(json.dumps(agent_detail_dict))
        self.agents = '\n'.join(agent_info)

    @classmethod
    async def create(cls, remote_agent_addresses: list[str], task_callback: TaskUpdateCallback | None = None) -> 'RecruiterOrchestratorAgent':
        """Create and asynchronously initialize an instance of the RecruiterOrchestratorAgent."""
        instance = cls(task_callback)
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        """Create an instance of the RecruiterOrchestratorAgent."""
        model_id = 'gemini-2.0-flash-exp'
        print(f'Using model: {model_id}')
        return Agent(
            model=model_id,
            name='Recruiter_Orchestrator_Agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=('This Recruiter Orchestrator agent coordinates all recruitment operations including candidate sourcing, screening, and analytics'),
            tools=[self.send_message, self.execute_full_recruitment_workflow, self.execute_candidate_operations, self.execute_talent_analytics],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate the root instruction for the RecruiterOrchestratorAgent."""
        current_agent = self.check_active_agent(context)
        return f"""
        **Role:** You are the master Recruiter Orchestrator. Your primary function is to coordinate all recruitment operations.

        **Core Directives:**
        * **Full Recruitment:** Use `execute_full_recruitment_workflow` for complete end-to-end recruitment (candidate ops + analytics)
        * **Candidate Operations:** Use `execute_candidate_operations` for sourcing, screening, and portfolio analysis only
        * **Talent Analytics:** Use `execute_talent_analytics` for compensation and productivity analysis only
        * **Task Delegation:** Use `send_message` for specific sub-orchestrator tasks
        * **Coordinated Execution:** Manage both candidate operations and analytics seamlessly
        * **Comprehensive Reporting:** Present detailed results from all recruitment stages

        **Recruitment Workflow Overview:**
        1. **Candidate Operations Orchestrator**: Manages sourcing → screening → portfolio
        2. **Talent Analytics Orchestrator**: Manages compensation → productivity

        **Available Sub-Orchestrators:**
        {self.agents}

        **Currently Active Orchestrator:** {current_agent['active_agent']}

        **Usage Instructions:**
        - For complete recruitment: Use `execute_full_recruitment_workflow` with job requirements
        - For candidate focus: Use `execute_candidate_operations`
        - For analytics focus: Use `execute_talent_analytics`
        - For specific tasks: Use `send_message` with orchestrator name
        """

    def check_active_agent(self, context: ReadonlyContext):
        state = context.state
        if 'session_id' in state and 'session_active' in state and state['session_active'] and 'active_agent' in state:
            return {'active_agent': f'{state["active_agent"]}'}
        return {'active_agent': 'None'}

    def before_model_callback(self, callback_context: CallbackContext, llm_request):
        state = callback_context.state
        if 'session_active' not in state or not state['session_active']:
            if 'session_id' not in state:
                state['session_id'] = str(uuid.uuid4())
            state['session_active'] = True

    def list_remote_agents(self):
        """List the available remote sub-orchestrators."""
        if not self.cards:
            return []
        remote_agent_info = []
        for card in self.cards.values():
            print(f'Found recruitment orchestrator card: {card.model_dump(exclude_none=True)}')
            remote_agent_info.append({'name': card.name, 'description': card.description})
        return remote_agent_info

    async def send_message(self, orchestrator_name: str, task: str, tool_context: ToolContext):
        """Sends a task to a specific sub-orchestrator."""
        if orchestrator_name not in self.remote_agent_connections:
            raise ValueError(f'Sub-orchestrator {orchestrator_name} not found')
        state = tool_context.state
        state['active_agent'] = orchestrator_name
        client = self.remote_agent_connections[orchestrator_name]
        if not client:
            raise ValueError(f'Client not available for {orchestrator_name}')
        task_id = state['task_id'] if 'task_id' in state else str(uuid.uuid4())
        context_id = state.get('context_id', str(uuid.uuid4()))
        message_id = state.get('input_message_metadata', {}).get('message_id', str(uuid.uuid4()))
        payload = {'message': {'role': 'user', 'parts': [{'type': 'text', 'text': task}], 'messageId': message_id, 'taskId': task_id, 'contextId': context_id}}
        message_request = SendMessageRequest(id=message_id, params=MessageSendParams.model_validate(payload))
        send_response: SendMessageResponse = await client.send_message(message_request=message_request)
        if not isinstance(send_response.root, SendMessageSuccessResponse):
            return None
        if not isinstance(send_response.root.result, Task):
            return None
        return send_response.root.result

    async def execute_full_recruitment_workflow(self, workflow_request: str, tool_context: ToolContext):
        """Executes complete recruitment workflow: candidate operations + talent analytics."""
        workflow_results = {'workflow_id': str(uuid.uuid4()), 'status': 'starting', 'orchestrators': []}
        try:
            print("Orchestrator 1: Candidate Operations")
            candidate_ops_task = f"Execute full candidate workflow (source, screen, portfolio): {workflow_request}"
            candidate_ops_result = await self.send_message("Candidate Operations Orchestrator Agent", candidate_ops_task, tool_context)
            workflow_results['orchestrators'].append({'orchestrator': 'Candidate Operations', 'result': candidate_ops_result})
            
            print("Orchestrator 2: Talent Analytics")
            analytics_task = f"Execute analytics workflow (compensation, productivity): {workflow_request}"
            analytics_result = await self.send_message("Talent Analytics Orchestrator Agent", analytics_task, tool_context)
            workflow_results['orchestrators'].append({'orchestrator': 'Talent Analytics', 'result': analytics_result})
            
            workflow_results['status'] = 'completed'
            workflow_results['summary'] = 'Full recruitment workflow completed successfully'
        except Exception as e:
            print(f"Full recruitment workflow failed: {e}")
            workflow_results['status'] = 'failed'
            workflow_results['error'] = str(e)
        return workflow_results

    async def execute_candidate_operations(self, operations_request: str, tool_context: ToolContext):
        """Executes candidate operations workflow only."""
        workflow_results = {'workflow_id': str(uuid.uuid4()), 'workflow_type': 'candidate_operations_only', 'status': 'starting'}
        try:
            print("Candidate Operations Only")
            candidate_ops_task = f"Execute candidate operations: {operations_request}"
            candidate_ops_result = await self.send_message("Candidate Operations Orchestrator Agent", candidate_ops_task, tool_context)
            workflow_results['result'] = candidate_ops_result
            workflow_results['status'] = 'completed'
            workflow_results['summary'] = 'Candidate operations completed'
        except Exception as e:
            print(f"Candidate operations failed: {e}")
            workflow_results['status'] = 'failed'
            workflow_results['error'] = str(e)
        return workflow_results

    async def execute_talent_analytics(self, analytics_request: str, tool_context: ToolContext):
        """Executes talent analytics workflow only."""
        workflow_results = {'workflow_id': str(uuid.uuid4()), 'workflow_type': 'talent_analytics_only', 'status': 'starting'}
        try:
            print("Talent Analytics Only")
            analytics_task = f"Execute talent analytics: {analytics_request}"
            analytics_result = await self.send_message("Talent Analytics Orchestrator Agent", analytics_task, tool_context)
            workflow_results['result'] = analytics_result
            workflow_results['status'] = 'completed'
            workflow_results['summary'] = 'Talent analytics completed'
        except Exception as e:
            print(f"Talent analytics failed: {e}")
            workflow_results['status'] = 'failed'
            workflow_results['error'] = str(e)
        return workflow_results

def _get_initialized_recruiter_orchestrator_sync() -> Agent:
    """Synchronously creates and initializes the RecruiterOrchestratorAgent."""
    async def _async_main() -> Agent:
        recruiter_orchestrator_instance = await RecruiterOrchestratorAgent.create(
            remote_agent_addresses=[
                os.getenv('CANDIDATE_OPS_ORCHESTRATOR_URL', 'http://localhost:8102'),
                os.getenv('TALENT_ANALYTICS_ORCHESTRATOR_URL', 'http://localhost:8106'),
            ]
        )
        return recruiter_orchestrator_instance.create_agent()
    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if 'asyncio.run() cannot be called from a running event loop' in str(e):
            print(f'Warning: Could not initialize RecruiterOrchestratorAgent with asyncio.run(): {e}.')
        raise

root_agent = _get_initialized_recruiter_orchestrator_sync()

