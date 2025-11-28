"""
Configuration for ADK Agent Engine Deployment

This file handles all configuration needed to deploy your agent to Google Cloud.

Expected Environment Variables:
================================

Required (in .env file):
- GOOGLE_CLOUD_PROJECT: Your GCP project ID (e.g., "baseshare")
- GOOGLE_CLOUD_LOCATION: GCP region (e.g., "us-central1")
- GOOGLE_CLOUD_STAGING_BUCKET: Bucket for staging artifacts

Agent-Specific (override per deployment):
- AGENT_NAME: Unique agent name (e.g., "plannin-agent", "docqabot")
- GOOGLE_CLOUD_STAGING_BUCKET: Can be overridden per agent

Optional:
- MODEL: AI model to use (default: "gemini-2.5-flash")
- GOOGLE_SERVICE_ACCOUNT_KEY_BASE64: Base64 encoded service account key (for Google Drive, etc.)
- ENABLE_WEAVE_TRACING: Enable Weave/W&B tracing (default: "false")
- WANDB_PROJECT: W&B project name (required if ENABLE_WEAVE_TRACING=true)
- WANDB_ENTITY: W&B entity/username (optional)
- WANDB_API_KEY: W&B API key (required if ENABLE_WEAVE_TRACING=true)
- WEAVE_DEBUG: Enable debug logging for Weave (default: "false")

Example Usage:
==============

# Deploy with .env settings:
make deploy-adk

# Deploy different agent (override agent name and bucket):
AGENT_NAME=docqabot GOOGLE_CLOUD_STAGING_BUCKET=docqabot-staging make deploy-adk

# Windows PowerShell:
$env:AGENT_NAME="docqabot"; $env:GOOGLE_CLOUD_STAGING_BUCKET="docqabot-staging"; make deploy-adk
"""

import os
from dataclasses import dataclass
from pathlib import Path

import google.auth
import vertexai

# =============================================================================
# STEP 1: Load Environment Variables
# =============================================================================


def load_environment_variables() -> None:
    """Load environment variables from .env file if it exists."""
    try:
        from dotenv import load_dotenv

        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            print(f"[OK] Loaded environment variables from {env_file}")
        else:
            print(f"[INFO] No .env file found at {env_file}")
    except ImportError:
        print("[INFO] python-dotenv not installed, skipping .env file loading")


# =============================================================================
# STEP 2: Basic Configuration
# =============================================================================


@dataclass
class AgentConfiguration:
    """Main configuration for your agent.
    
    Environment variables are loaded dynamically to support:
    - Multiple agents in the same project
    - Runtime environment variable overrides
    - Flexible deployment without multiple .env files
    """

    # The AI model to use (you can change this if needed)
    model: str = ""
    #os.environ.get("MODEL", "gemini-2.5-flash")

    # Deployment name (can have hyphens, used for display in Agent Engine)
    deployment_name: str = ""
    # deployment_name: str = os.environ.get("AGENT_NAME", "plannin-agent")

    # Google Cloud settings
    project_id: str | None = None
    location: str = "us-central1"
    staging_bucket: str | None = None

    def __post_init__(self) -> None:
        """Load environment variables and validate required settings.
        
        This method reads from environment variables at runtime, allowing:
        - Override via command: AGENT_NAME=docqabot make deploy-adk
        - Multiple agents in same project with different names/buckets
        - Single .env file for shared config, env vars for agent-specific config
        """

        # Load environment variables first (.env file if exists)
        load_environment_variables()

        # Load model (with default fallback)
        self.model = os.environ.get("MODEL", "gemini-2.5-flash")

        # Load deployment name (with default fallback)
        self.deployment_name = os.environ.get("AGENT_NAME", "plannin-agent")

        # Validate and set project_id
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            # Try fallback to gcloud default
            try:
                _, self.project_id = google.auth.default()
            except Exception:
                pass

        if not self.project_id:
            raise ValueError(
                "[ERROR] Missing GOOGLE_CLOUD_PROJECT environment variable!\n"
                "Please set it in your .env file or run:\n"
                "  gcloud config set project YOUR_PROJECT_ID"
            )

        # Set location (with validation and default fallback)
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not self.location:
            raise ValueError(
                "[ERROR] Missing GOOGLE_CLOUD_LOCATION environment variable!\n"
                "Please set it in your .env file (e.g., 'us-central1')"
            )

        # Set staging bucket (required for Agent Engine deployment)
        self.staging_bucket = os.environ.get("GOOGLE_CLOUD_STAGING_BUCKET")
        if not self.staging_bucket:
            raise ValueError(
                "[ERROR] Missing GOOGLE_CLOUD_STAGING_BUCKET environment variable!\n"
                "This is required for Agent Engine deployment.\n"
                "Please add it to your .env file or set via environment:\n"
                "  Windows: $env:GOOGLE_CLOUD_STAGING_BUCKET='your-bucket'\n"
                "  Linux/Mac: GOOGLE_CLOUD_STAGING_BUCKET=your-bucket"
            )

    @property
    def internal_agent_name(self) -> str:
        """
        Convert deployment name to a valid Python identifier.

        Replaces hyphens with underscores and ensures it's a valid identifier.
        """
        # Convert hyphens to underscores and make it a valid identifier
        name = self.deployment_name.replace("-", "_")

        # Ensure it starts with a letter or underscore
        if not name[0].isalpha() and name[0] != "_":
            name = f"agent_{name}"

        return name


@dataclass
class DeploymentConfiguration:
    """Configuration needed for deployment to Agent Engine."""

    project: str
    location: str
    agent_name: str
    requirements_file: str
    extra_packages: list[str]
    staging_bucket: str


# =============================================================================
# STEP 3: Initialize Configuration
# =============================================================================


def initialize_vertex_ai(config: AgentConfiguration) -> None:
    """Initialize Vertex AI with the provided configuration."""
    try:
        print("\n[INIT] Initializing Vertex AI...")
        print(f"  Project: {config.project_id}")
        print(f"  Location: {config.location}")
        print(f"  Staging Bucket: {config.staging_bucket or 'Not set'}")

        # Initialize Vertex AI (config values already validated in __post_init__)
        if config.staging_bucket:
            vertexai.init(
                project=config.project_id,
                location=config.location,
                staging_bucket=config.staging_bucket,
            )
        else:
            vertexai.init(project=config.project_id, location=config.location)

        print(f"[OK] Vertex AI initialized successfully!")

        if not config.staging_bucket:
            print(
                "[INFO] Add GOOGLE_CLOUD_STAGING_BUCKET to .env for Agent Engine deployment"
            )

    except Exception as e:
        print(f"[ERROR] Failed to initialize Vertex AI: {e}")
        print("\n[SETUP] Setup checklist:")
        print("  1. Set GOOGLE_CLOUD_PROJECT in .env file")
        print("  2. Run: gcloud auth application-default login")
        print("  3. Run: gcloud config set project YOUR_PROJECT_ID")
        print("  4. Enable required APIs in Google Cloud Console")


def get_deployment_config() -> DeploymentConfiguration:
    """
    Get deployment configuration with validation.

    This function validates all required settings before deployment.
    """
    # Use validated config values (already checked in __post_init__)
    project_id = config.project_id
    if not project_id:
        raise ValueError(
            "[ERROR] Project ID validation failed. This should not happen after __post_init__."
        )

    if not config.staging_bucket:
        raise ValueError(
            "[ERROR] Missing GOOGLE_CLOUD_STAGING_BUCKET environment variable!\n"
            "This is required for Agent Engine deployment.\n"
            "Please add it to your .env file."
        )

    # Use centralized agent name from config
    agent_name = config.deployment_name
    if not agent_name:
        raise ValueError(
            "[ERROR] Missing agent name. Please set AGENT_NAME in .env file (e.g., 'my-research-agent')"
        )

    # Check requirements file exists
    requirements_file = os.environ.get("REQUIREMENTS_FILE", ".requirements.txt")
    if not Path(requirements_file).exists():
        raise ValueError(
            f"[ERROR] Requirements file not found: {requirements_file}\n"
            "Please run 'uv export > .requirements.txt' to generate it"
        )

    # Parse extra packages (code to include in deployment)
    extra_packages_str = os.environ.get("EXTRA_PACKAGES", "./app")
    extra_packages = [
        pkg.strip() for pkg in extra_packages_str.split(",") if pkg.strip()
    ]

    if not extra_packages:
        raise ValueError(
            "[ERROR] No extra packages specified. Please set EXTRA_PACKAGES in .env file "
            "or ensure './app' directory exists"
        )

    return DeploymentConfiguration(
        project=project_id,
        location=config.location,
        agent_name=agent_name,
        requirements_file=requirements_file,
        extra_packages=extra_packages,
        staging_bucket=config.staging_bucket,
    )


def get_project_id() -> str | None:
    """Get project ID from config (already validated in __post_init__)."""
    return config.project_id


# =============================================================================
# STEP 4: Initialize Everything
# =============================================================================

# Create main configuration (this will now load .env and validate)
config = AgentConfiguration()

# Initialize Vertex AI
initialize_vertex_ai(config)

# Print summary with environment variable sources
print("\n[CONFIG] Configuration Summary:")
print(f"  Agent Name: {config.deployment_name}")
print(f"  Internal Name: {config.internal_agent_name}")
print(f"  Model: {config.model}")
print(f"  Project: {get_project_id()}")
print(f"  Location: {config.location}")

# Show if agent-specific vars are set (useful for multi-agent deployment)
agent_name_env = os.environ.get("AGENT_NAME")
bucket_env = os.environ.get("GOOGLE_CLOUD_STAGING_BUCKET")
if agent_name_env:
    print(f"\n[INFO] AGENT_NAME override detected: {agent_name_env}")
if bucket_env:
    print(f"[INFO] GOOGLE_CLOUD_STAGING_BUCKET override detected: {bucket_env}")

print("=" * 50)
