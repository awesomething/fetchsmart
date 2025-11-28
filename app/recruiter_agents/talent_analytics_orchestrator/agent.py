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

class TalentAnalyticsOrchestratorAgent:
    """The Talent Analytics Orchestrator agent."""

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
    async def create(cls, remote_agent_addresses: list[str], task_callback: TaskUpdateCallback | None = None) -> 'TalentAnalyticsOrchestratorAgent':
        """Create and asynchronously initialize an instance of the TalentAnalyticsOrchestratorAgent."""
        instance = cls(task_callback)
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        """Create an instance of the TalentAnalyticsOrchestratorAgent."""
        model_id = 'gemini-2.0-flash-exp'
        print(f'Using model: {model_id}')
        return Agent(
            model=model_id,
            name='Talent_Analytics_Orchestrator_Agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=('This Talent Analytics Orchestrator agent orchestrates compensation and productivity analysis'),
            tools=[self.send_message, self.execute_analytics_workflow, self.execute_compensation_workflow],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate the root instruction for the TalentAnalyticsOrchestratorAgent."""
        current_agent = self.check_active_agent(context)
        return f"""
        **Role:** You are an expert Talent Analytics Orchestrator. Your primary function is to coordinate compensation and productivity analysis.

        **Core Directives:**
        * **Full Analytics:** Use `execute_analytics_workflow` for complete compensation + productivity analysis
        * **Compensation Only:** Use `execute_compensation_workflow` for salary benchmarking only
        * **Task Delegation:** Use `send_message` for individual agent tasks
        * **Sequential Processing:** Compensation → Productivity (when both needed)
        * **Comprehensive Reporting:** Present detailed analytics results

        **Analytics Workflow Sequence:**
        1. **Compensation Agent**: Salary benchmarking and competitive analysis
        2. **Recruiter Productivity Agent**: Time tracking and productivity metrics

        **Available Analytics Agents:**
        {self.agents}

        **Currently Active Agent:** {current_agent['active_agent']}

        **Usage Instructions:**
        - For full analytics: Use `execute_analytics_workflow`
        - For compensation only: Use `execute_compensation_workflow`
        - For individual tasks: Use `send_message` with agent name
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
        """List the available remote analytics agents."""
        if not self.cards:
            return []
        remote_agent_info = []
        for card in self.cards.values():
            print(f'Found analytics agent card: {card.model_dump(exclude_none=True)}')
            remote_agent_info.append({'name': card.name, 'description': card.description})
        return remote_agent_info

    async def send_message(self, agent_name: str, task: str, tool_context: ToolContext):
        """Sends a task to a specific remote analytics agent."""
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f'Analytics agent {agent_name} not found')
        state = tool_context.state
        state['active_agent'] = agent_name
        client = self.remote_agent_connections[agent_name]
        if not client:
            raise ValueError(f'Client not available for {agent_name}')
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

    async def execute_analytics_workflow(self, workflow_request: str, tool_context: ToolContext):
        """Executes complete analytics workflow: compensation + productivity analysis."""
        workflow_results = {'workflow_id': str(uuid.uuid4()), 'status': 'starting', 'steps': []}
        try:
            print("Step 1: Compensation Analysis")
            comp_task = f"Analyze compensation and salary benchmarks for: {workflow_request}"
            comp_result = await self.send_message("Compensation Agent", comp_task, tool_context)
            workflow_results['steps'].append({'step': 1, 'agent': 'Compensation Agent', 'result': comp_result})
            
            print("Step 2: Productivity Analysis")
            prod_task = f"Analyze recruiter productivity and time tracking. Context: {workflow_request}"
            prod_result = await self.send_message("Recruiter Productivity Agent", prod_task, tool_context)
            workflow_results['steps'].append({'step': 2, 'agent': 'Recruiter Productivity Agent', 'result': prod_result})
            
            workflow_results['status'] = 'completed'
            workflow_results['summary'] = 'Analytics workflow completed successfully'
        except Exception as e:
            print(f"Analytics workflow execution failed: {e}")
            workflow_results['status'] = 'failed'
            workflow_results['error'] = str(e)
        return workflow_results

    async def execute_compensation_workflow(self, comp_request: str, tool_context: ToolContext):
        """Executes compensation analysis only."""
        workflow_results = {'workflow_id': str(uuid.uuid4()), 'workflow_type': 'compensation_only', 'status': 'starting', 'steps': []}
        try:
            print("Compensation Analysis")
            comp_task = f"Analyze compensation: {comp_request}"
            comp_result = await self.send_message("Compensation Agent", comp_task, tool_context)
            workflow_results['steps'].append({'step': 1, 'agent': 'Compensation Agent', 'result': comp_result})
            workflow_results['status'] = 'completed'
            workflow_results['summary'] = 'Compensation workflow completed'
        except Exception as e:
            print(f"Compensation workflow failed: {e}")
            workflow_results['status'] = 'failed'
            workflow_results['error'] = str(e)
        return workflow_results

def _get_initialized_talent_analytics_orchestrator_sync() -> Agent:
    """Synchronously creates and initializes the TalentAnalyticsOrchestratorAgent."""
    async def _async_main() -> Agent:
        talent_analytics_instance = await TalentAnalyticsOrchestratorAgent.create(
            remote_agent_addresses=[
                os.getenv('COMPENSATION_AGENT_URL', 'http://localhost:8107'),
                os.getenv('RECRUITER_PRODUCTIVITY_AGENT_URL', 'http://localhost:8108'),
            ]
        )
        return talent_analytics_instance.create_agent()
    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if 'asyncio.run() cannot be called from a running event loop' in str(e):
            print(f'Warning: Could not initialize TalentAnalyticsOrchestratorAgent with asyncio.run(): {e}.')
        raise

root_agent = _get_initialized_talent_analytics_orchestrator_sync()

