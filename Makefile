install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $$HOME/.local/bin/env; }
	uv sync && cd nextjs && npm install

dev:
	make dev-backend & make dev-frontend

dev-backend:
	uv run adk api_server app --allow_origins="*"

dev-frontend:
	@echo "🧹 Cleaning Next.js build cache..."
	@cd nextjs && npm run clean || true
	@echo "🚀 Starting Next.js dev server..."
	"$$PROGRAMFILES/nodejs/npm" --prefix nextjs run dev

dev-floating:
	cd nextjs && npm run electron:service

adk-web:
	uv run adk web --port 8501

# Recruitment MCP Server - Install dependencies
install-recruitment-deps:
	@echo "📦 Installing recruitment backend dependencies..."
	@cd mcp_server/recruitment_backend && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Recruitment MCP Server
dev-recruitment-mcp:
	@echo "🚀 Starting Recruitment MCP server locally..."
	@cd mcp_server/recruitment_backend && python server.py

test-docs:
	@.venv/Scripts/python test_docs.py

test-google-drive:
	@.venv/Scripts/python test_google_drive.py

# MCP Server local testing (requires separate venv in mcp_server/)
test-mcp:
	@echo "🧪 Testing MCP server locally..."
	@echo "Make sure MCP server is running: cd mcp_server && python mcppoagent.py"
	@cd mcp_server && python test_workflow.py

dev-mcp:
	@echo "🚀 Starting MCP server locally..."
	@cd mcp_server && python mcppoagent.py

# Staffing MCP Server - Install dependencies to shared venv
install-staffing-deps:
	@echo "📦 Installing staffing backend dependencies to shared venv..."
	@cd mcp_server && .venv/Scripts/pip install -q -r staffing_backend/requirements.txt
	@echo "✅ Dependencies installed to mcp_server/.venv"

# Staffing MCP Server testing (uses shared .venv from mcp_server/)
test-staffing-tools:
	@echo "🧪 Testing Staffing MCP Tools..."
	@echo "📦 Checking dependencies in shared venv..."
	@cd mcp_server && .venv/Scripts/python -c "import supabase" 2>/dev/null || (echo "⚠️  Dependencies not installed. Run 'make install-staffing-deps' first." && exit 1)
	@cd mcp_server && .venv/Scripts/python staffing_backend/test_tools.py

dev-staffing-mcp:
	@echo "🚀 Starting Staffing MCP server locally..."
	@echo "📦 Checking dependencies in shared venv..."
	@cd mcp_server && .venv/Scripts/python -c "import supabase" 2>/dev/null || (echo "⚠️  Dependencies not installed. Run 'make install-staffing-deps' first." && exit 1)
	@cd mcp_server && .venv/Scripts/python staffing_backend/mcpstaffingagent.py
	

# Create staging bucket for Recruiter agent
create-recruiter-bucket:
	@echo "📦 Creating staging bucket for Recruiter Agent..."
	@gcloud storage buckets create gs://recruiter-staging --project=baseshare --location=us-central1 2>/dev/null || echo "ℹ️  Bucket already exists or creation failed"
	@echo "✅ Bucket ready: gs://recruiter-staging"

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

# Deploy the agent remotely
deploy-adk:
	# Export dependencies to requirements file using uv export.
	uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate > .requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project > .requirements.txt && uv run app/agent_engine_app.py

# Docker Compose targets for recruiting dashboard MVP
dev-docker:
	@echo "🐳 Starting services with Docker Compose..."
	docker compose up --build

down-docker:
	@echo "🛑 Stopping Docker Compose services..."
	docker compose down -v
