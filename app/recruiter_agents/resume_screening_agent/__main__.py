import logging
import os

import click
from dotenv import load_dotenv
import uvicorn

from agent import root_agent
from agent_executor import ADKAgentExecutor

from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)


logger = logging.getLogger(__name__)

load_dotenv()


@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=8104, help="Port to bind the server to")
def main(host: str, port: int):
    """Run the resume screening agent server."""
    logger.info("--- 🚀 Starting Resume Screening Agent Server... ---")
    
    skill = AgentSkill(
        id='resume_screening',
        name='Intelligent Resume Screening',
        description='Screens and matches candidates to job requirements using AI-powered analysis',
        tags=['screening', 'matching', 'candidates', 'ai-matching', 'recruitment'],
        examples=[
            'Screen candidates for Senior Engineer role',
            'Match candidates to this job description',
            'Find top 5 candidates for ML position'
        ],
    )

    agent_card = AgentCard(
        name='Resume Screening Agent',
        description='Screens and matches candidates to job requirements using intelligent AI-powered analysis',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    runner = Runner(
        app_name=agent_card.name,
        agent=root_agent,
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        artifact_service=InMemoryArtifactService(),
    )

    executor = ADKAgentExecutor(runner=runner, card=agent_card)

    app = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )
    )
    
    print(f"\n🚀 Resume Screening Agent Starting...")
    print(f"📍 URL: http://{host}:{port}")
    print(f"🎴 Agent Card: http://{host}:{port}/.well-known/agent-card.json")
    print(f"✅ Ready to screen candidates!\n")
    
    uvicorn.run(app.build(), host=host, port=port)


if __name__ == "__main__":
    main()

