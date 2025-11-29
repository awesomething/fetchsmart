"""
Agent Engine App - Deploy your agent to Google Cloud

This file contains the logic to deploy your agent to Vertex AI Agent Engine.
"""

import copy
import datetime
import json
import os
from pathlib import Path
from typing import Any

import vertexai
from google.adk.artifacts import GcsArtifactService
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from app.agent import root_agent
from app.config import config, get_deployment_config
from app.utils.gcs import create_bucket_if_not_exists
from app.utils.tracing import CloudTraceLoggingSpanExporter
from app.utils.typing import Feedback


class AgentEngineApp(AdkApp):
    """
    ADK Application wrapper for Agent Engine deployment.

    This class extends the base ADK app with logging, tracing, and feedback capabilities.
    """

    def set_up(self) -> None:
        """Set up logging and tracing for the agent engine app."""
        # Set up OpenTelemetry tracer provider BEFORE calling super().set_up()
        # This ensures ADK uses our custom tracer provider with Weave exporter
        from opentelemetry.sdk.resources import Resource
        
        # Create resource with service name for proper trace attribution
        resource = Resource.create({
            "service.name": f"{config.deployment_name}-service",
            "service.version": "1.0.0",
        })
        
        provider = TracerProvider(resource=resource)
        
        # Add Cloud Trace exporter (existing)
        cloud_trace_processor = export.BatchSpanProcessor(
            CloudTraceLoggingSpanExporter(
                project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                service_name=f"{config.deployment_name}-service",
            )
        )
        provider.add_span_processor(cloud_trace_processor)
        
        # Add Weave exporter (if enabled)
        enable_weave = os.environ.get("ENABLE_WEAVE_TRACING", "false").lower() == "true"
        if enable_weave:
            try:
                from app.utils.weave_tracing import WeaveSpanExporter
                
                weave_exporter = WeaveSpanExporter(
                    service_name=f"{config.deployment_name}-service",
                    debug=os.environ.get("WEAVE_DEBUG", "false").lower() == "true",
                )
                weave_processor = export.BatchSpanProcessor(weave_exporter)
                provider.add_span_processor(weave_processor)
                print("✅ Weave tracing enabled")
            except Exception as e:
                print(f"⚠️  Failed to enable Weave tracing: {e}")
                import traceback
                if os.environ.get("WEAVE_DEBUG", "false").lower() == "true":
                    traceback.print_exc()
                print("   Continuing without Weave tracing...")
        
        # Set the tracer provider BEFORE ADK initializes
        trace.set_tracer_provider(provider)
        
        # Now call super().set_up() - ADK will use our tracer provider
        super().set_up()
        logging_client = google_cloud_logging.Client()
        self.logger = logging_client.logger(__name__)
        self.enable_tracing = True

    def register_feedback(self, feedback: dict[str, Any]) -> None:
        """Collect and log feedback from users."""
        feedback_obj = Feedback.model_validate(feedback)
        self.logger.log_struct(feedback_obj.model_dump(), severity="INFO")

    def register_operations(self) -> dict[str, list[str]]:
        """Register available operations for the agent."""
        operations = super().register_operations()
        operations[""] = operations[""] + ["register_feedback"]
        return operations

    def clone(self) -> "AgentEngineApp":
        """Create a copy of this application.

        Avoid deep-copying the agent graph to prevent cloning non-picklable
        objects (e.g., file handles) that may be attached by 3P libraries.
        The Agent Engine runtime safely handles independent instances.
        """
        template_attributes = self._tmpl_attrs

        return self.__class__(
            agent=template_attributes["agent"],
            enable_tracing=bool(template_attributes.get("enable_tracing", False)),
            session_service_builder=template_attributes.get("session_service_builder"),
            artifact_service_builder=template_attributes.get(
                "artifact_service_builder"
            ),
            env_vars=template_attributes.get("env_vars"),
        )


def deploy_agent_engine_app() -> agent_engines.AgentEngine:
    """
    Deploy the agent to Vertex AI Agent Engine.

    This function:
    1. Gets deployment configuration from environment variables
    2. Creates required Google Cloud Storage buckets
    3. Deploys the agent to Agent Engine
    4. Saves deployment metadata to logs/deployment_metadata.json

    Returns:
        The deployed agent engine instance
    """
    print("🚀 Starting Agent Engine deployment...")

    # Step 1: Get deployment configuration
    deployment_config = get_deployment_config()
    print(f"📋 Deploying agent: {deployment_config.agent_name}")
    print(f"📋 Project: {deployment_config.project}")
    print(f"📋 Location: {deployment_config.location}")
    print(f"📋 Staging bucket: {deployment_config.staging_bucket}")

    # Step 2: Set up environment variables for the deployed agent
    env_vars = {}

    # Configure worker parallelism
    env_vars["NUM_WORKERS"] = "1"

    # Pass Google Drive credentials to the deployed qa agent
    google_service_account_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY_BASE64")
    if google_service_account_key:
        env_vars["GOOGLE_SERVICE_ACCOUNT_KEY_BASE64"] = google_service_account_key
        print("✅ Google Drive credentials will be available to deployed agent")
    else:
        print("⚠️  GOOGLE_SERVICE_ACCOUNT_KEY_BASE64 not set - Google Drive tools will not work")

    # Pass MCP server URLs for recruiter and staffing agents
    print("\n" + "="*60)
    print("🔗 MCP Server Configuration")
    print("="*60)
    
    recruitment_mcp_url = os.environ.get("RECRUITMENT_MCP_SERVER_URL")
    if recruitment_mcp_url:
        env_vars["RECRUITMENT_MCP_SERVER_URL"] = recruitment_mcp_url
        print(f"✅ Recruitment MCP server URL configured: {recruitment_mcp_url}")
        print(f"   → This will be passed to deployed agent as RECRUITMENT_MCP_SERVER_URL")
    else:
        # Also check for MCP_SERVER_URL (used by some recruiter agents)
        mcp_url = os.environ.get("MCP_SERVER_URL")
        if mcp_url:
            env_vars["MCP_SERVER_URL"] = mcp_url
            print(f"✅ MCP server URL configured (fallback): {mcp_url}")
            print(f"   → This will be passed to deployed agent as MCP_SERVER_URL")
        else:
            print("⚠️  RECRUITMENT_MCP_SERVER_URL not set")
            print("   → Recruiter agents will try to use local backend (will fail in production)")
            print("   → To fix: Set RECRUITMENT_MCP_SERVER_URL before deploying")
    
    staffing_mcp_url = os.environ.get("STAFFING_MCP_SERVER_URL")
    if staffing_mcp_url:
        env_vars["STAFFING_MCP_SERVER_URL"] = staffing_mcp_url
        print(f"✅ Staffing MCP server URL configured: {staffing_mcp_url}")
        print(f"   → This will be passed to deployed agent as STAFFING_MCP_SERVER_URL")
    else:
        print("⚠️  STAFFING_MCP_SERVER_URL not set")
        print("   → Staffing agents will use localhost (will fail in production)")
        print("   → To fix: Set STAFFING_MCP_SERVER_URL before deploying")
    
    print("="*60 + "\n")

    # Pass Weave/W&B configuration if enabled
    enable_weave = os.environ.get("ENABLE_WEAVE_TRACING", "false").lower() == "true"
    if enable_weave:
        wandb_project = os.environ.get("WANDB_PROJECT")
        wandb_entity = os.environ.get("WANDB_ENTITY")
        wandb_api_key = os.environ.get("WANDB_API_KEY")
        
        if wandb_project:
            env_vars["ENABLE_WEAVE_TRACING"] = "true"
            env_vars["WANDB_PROJECT"] = wandb_project
            if wandb_entity:
                env_vars["WANDB_ENTITY"] = wandb_entity
            if wandb_api_key:
                env_vars["WANDB_API_KEY"] = wandb_api_key
            print("✅ Weave tracing configuration will be available to deployed agent")
        else:
            print("⚠️  ENABLE_WEAVE_TRACING is true but WANDB_PROJECT not set - Weave tracing disabled")

    # Step 3: Create required Google Cloud Storage buckets
    artifacts_bucket_name = (
        f"{deployment_config.project}-{deployment_config.agent_name}-logs-data"
    )

    print(f"📦 Creating artifacts bucket: {artifacts_bucket_name}")

    create_bucket_if_not_exists(
        bucket_name=artifacts_bucket_name,
        project=deployment_config.project,
        location=deployment_config.location,
    )

    # Step 4: Initialize Vertex AI for deployment
    vertexai.init(
        project=deployment_config.project,
        location=deployment_config.location,
        staging_bucket=f"gs://{deployment_config.staging_bucket}",
    )

    # Step 5: Read requirements file
    with open(deployment_config.requirements_file) as f:
        requirements = f.read().strip().split("\n")

    # Step 6: Create the agent engine app
    agent_engine = AgentEngineApp(
        agent=root_agent,
        artifact_service_builder=lambda: GcsArtifactService(
            bucket_name=artifacts_bucket_name
        ),
    )

    # Step 7: Configure the agent for deployment
    agent_config = {
        "agent_engine": agent_engine,
        "display_name": deployment_config.agent_name,
        "description": "A simple goal planning agent",
        "extra_packages": deployment_config.extra_packages,
        "env_vars": env_vars,
        "requirements": requirements,
    }

    # Step 8: Deploy or update the agent
    existing_agents = list(
        agent_engines.list(filter=f"display_name={deployment_config.agent_name}")
    )

    if existing_agents:
        print(f"🔄 Updating existing agent: {deployment_config.agent_name}")
        remote_agent = existing_agents[0].update(**agent_config)
    else:
        print(f"🆕 Creating new agent: {deployment_config.agent_name}")
        remote_agent = agent_engines.create(**agent_config)

    # Step 9: Save deployment metadata
    metadata = {
        "remote_agent_engine_id": remote_agent.resource_name,
        "deployment_timestamp": datetime.datetime.now().isoformat(),
        "agent_name": deployment_config.agent_name,
        "project": deployment_config.project,
        "location": deployment_config.location,
    }

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    metadata_file = logs_dir / "deployment_metadata.json"

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print("✅ Agent deployed successfully!")
    print(f"📄 Deployment metadata saved to: {metadata_file}")
    print(f"🆔 Agent Engine ID: {remote_agent.resource_name}")

    return remote_agent


if __name__ == "__main__":
    print(
        """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🤖 DEPLOYING AGENT TO VERTEX AI AGENT ENGINE 🤖         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    )

    deploy_agent_engine_app()