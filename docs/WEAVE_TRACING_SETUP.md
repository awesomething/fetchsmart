# Weave Tracing Setup Guide

This guide explains how to set up Weave (Weights & Biases) tracing for your ADK multi-agent system to visualize agent and tool call traces alongside Cloud Trace.

## Overview

Weave tracing provides:
- **Visual trace visualization** in W&B UI
- **Agent and tool call observability** beyond what Vertex AI Agent Engine captures
- **MCP tool call tracing** with full context (parameters, responses, latency)
- **Dual export** - traces sent to both Cloud Trace and Weave simultaneously

## Prerequisites

- Weights & Biases account (free tier available)
- Python dependencies installed (`weave` and `wandb` packages)
- Access to set environment variables

## Step 1: Create W&B Account

1. Go to [https://wandb.ai](https://wandb.ai)
2. Sign up for a free account (or log in if you already have one)
3. Complete the onboarding process

## Step 2: Create W&B Project

1. In the W&B dashboard, click **"Create Project"**
2. Enter a project name (e.g., `adk-recruitment-traces`)
3. Select **"Other"** as the project type
4. Click **"Create"**

## Step 3: Get Your API Key

1. Click on your profile icon (top right)
2. Go to **"Settings"**
3. Navigate to **"API Keys"** section
4. Click **"Create API Key"**
5. Copy the API key (you'll need this for environment variables)

## Step 4: Configure Environment Variables

Add the following environment variables to your `.env` file or deployment configuration:

```bash
# Enable Weave tracing
ENABLE_WEAVE_TRACING=true

# W&B Configuration
WANDB_PROJECT=adk-recruitment-traces  # Your project name
WANDB_ENTITY=your-username           # Your W&B username/entity
WANDB_API_KEY=your-api-key-here      # Your API key from Step 3

# Optional: Enable debug logging for Weave
WEAVE_DEBUG=false
```

### For Local Development

Add to `app/.env`:

```bash
ENABLE_WEAVE_TRACING=true
WANDB_PROJECT=adk-recruitment-traces
WANDB_ENTITY=your-username
WANDB_API_KEY=your-api-key-here
```

### For Agent Engine Deployment

The deployment script (`app/agent_engine_app.py`) automatically passes these environment variables to the deployed agent when `ENABLE_WEAVE_TRACING=true`.

You can set them in your deployment environment or pass them when running `make deploy-adk`:

```bash
ENABLE_WEAVE_TRACING=true \
WANDB_PROJECT=adk-recruitment-traces \
WANDB_ENTITY=your-username \
WANDB_API_KEY=your-api-key \
make deploy-adk
```

## Step 5: Verify Installation

1. **Check dependencies are installed:**

```bash
pip list | grep -E "weave|wandb"
```

You should see:
- `weave` (version >= 0.1.0)
- `wandb` (version >= 0.16.0)

2. **Test local tracing:**

Start your local development server:

```bash
make dev
```

Send a test request to an agent that uses MCP tools. Check the console for:

```
✅ Weave tracing enabled
```

3. **Test Weave Tracing Setup:**

Run the test script to verify everything is configured correctly:

```bash
# Make sure environment variables are set
export ENABLE_WEAVE_TRACING=true
export WANDB_PROJECT=your-project-name
export WANDB_ENTITY=your-entity
export WANDB_API_KEY=your-api-key
export WEAVE_DEBUG=true

# Run the test script
python test_weave_tracing.py
```

This will:
- Verify environment variables are set
- Test Weave exporter initialization
- Create a test OpenTelemetry span
- Export it to Weave
- Confirm the setup is working

**If the test passes**, you should see a trace in your W&B project dashboard. If the test fails, check the error messages and verify your configuration.

4. **Check W&B Dashboard:**

- Go to your W&B project dashboard
- Navigate to **"Runs"** or **"Traces"** section
- You should see trace data appearing as agents execute

## Viewing Traces in Weave

### In W&B Dashboard

1. **Open your project** in W&B
2. **Navigate to "Traces"** or "Runs" section
3. **Filter by:**
   - Agent name
   - Tool name
   - Time range
   - Status (success/error)

### Trace Information Available

Each trace includes:

- **Agent Information:**
  - Agent name
  - Service name
  - Execution time

- **MCP Tool Calls:**
  - Tool name
  - MCP server URL
  - Parameters (truncated if large)
  - Response (truncated if large)
  - Duration
  - Error information (if any)

- **Span Hierarchy:**
  - Parent-child relationships
  - Trace ID and Span ID
  - Timing information

## Troubleshooting

### Weave Tracing Not Enabled

**Symptom:** No traces appear in W&B dashboard

**Solutions:**
1. **Verify environment variables are set:**
   ```bash
   echo $ENABLE_WEAVE_TRACING
   echo $WANDB_PROJECT
   echo $WANDB_API_KEY
   ```

2. **Check `ENABLE_WEAVE_TRACING=true` is set** (not "True" or "TRUE")

3. **Verify `WANDB_PROJECT` is set correctly** - must match your W&B project name exactly

4. **Check API key is valid:**
   ```bash
   wandb login
   # Or verify in W&B settings: https://wandb.ai/settings
   ```

5. **Enable debug mode** to see detailed logs:
   ```bash
   WEAVE_DEBUG=true ENABLE_WEAVE_TRACING=true make dev
   ```

6. **Check application logs** for errors:
   - Look for "Failed to enable Weave tracing" messages
   - Look for "Weave OTLP exporter initialized" confirmation
   - Check for OTLP export errors

7. **Verify spans are being created:**
   - ADK should automatically create spans for agent execution
   - If no spans are created, ADK might not have OpenTelemetry enabled
   - Check Cloud Trace to see if spans exist there (if they do, Weave should receive them too)

8. **Test OTLP connection:**
   ```bash
   curl -X POST https://api.wandb.ai/otlp/v1/traces \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json"
   ```

### Import Errors

**Symptom:** `ImportError: Weave SDK not installed`

**Solution:**
```bash
pip install weave wandb
# or
uv sync  # if using uv
```

### Authentication Errors

**Symptom:** `Authentication failed` or `Invalid API key`

**Solutions:**
1. Verify `WANDB_API_KEY` is correct
2. Check API key hasn't expired (regenerate if needed)
3. Ensure `WANDB_ENTITY` matches your W&B username

### Traces Not Appearing

**Symptom:** Tracing enabled but no data in W&B

**Solutions:**
1. **Wait a few minutes** - batching may delay export (spans are batched before sending)

2. **Check agent is actually executing:**
   - Send test requests to agents
   - Verify agents are processing requests
   - Check Cloud Trace to see if spans exist (if Cloud Trace has spans, Weave should too)

3. **Verify MCP tools are being called:**
   - Check agent logs for tool execution
   - Verify MCP servers are accessible
   - Tool calls should create spans automatically

4. **Enable debug mode:**
   ```bash
   WEAVE_DEBUG=true ENABLE_WEAVE_TRACING=true
   ```
   This will show detailed export logs

5. **Check W&B project name matches exactly:**
   - Project name is case-sensitive
   - Verify in W&B dashboard: https://wandb.ai/your-entity/projects

6. **Verify OTLP endpoint is correct:**
   - Default: `https://api.wandb.ai/otlp/v1/traces`
   - Can override with `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` env var

7. **Check network connectivity:**
   - Ensure your environment can reach `api.wandb.ai`
   - Firewall/proxy might block OTLP requests

8. **Verify ADK is creating spans:**
   - ADK should automatically create OpenTelemetry spans when `enable_tracing=True`
   - If ADK doesn't create spans, Weave won't receive any data
   - Check Cloud Trace to confirm spans are being created
   - Run `python test_weave_tracing.py` to verify the exporter works independently

9. **Test the exporter directly:**
   ```bash
   python test_weave_tracing.py
   ```
   This will create a test span and export it to Weave. If this works but ADK traces don't appear, the issue is with ADK span creation, not the Weave exporter.

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_WEAVE_TRACING` | Yes | `false` | Enable/disable Weave tracing |
| `WANDB_PROJECT` | Yes* | - | W&B project name |
| `WANDB_ENTITY` | No | - | W&B entity/username |
| `WANDB_API_KEY` | Yes* | - | W&B API key |
| `WEAVE_DEBUG` | No | `false` | Enable debug logging |

*Required when `ENABLE_WEAVE_TRACING=true`

## Best Practices

1. **Use separate projects** for different environments (dev, staging, prod)
2. **Set appropriate retention** in W&B project settings
3. **Monitor costs** - W&B free tier has limits
4. **Use entity/team** for organization-wide projects
5. **Rotate API keys** periodically for security

## Integration with Cloud Trace

Weave tracing works **alongside** Cloud Trace - both exporters run simultaneously:

- **Cloud Trace**: Google Cloud native tracing (always enabled)
- **Weave**: W&B visualization and analysis (optional, enabled via `ENABLE_WEAVE_TRACING`)

This dual export provides:
- **Cloud Trace**: Integration with GCP monitoring, alerting, and logging
- **Weave**: Rich visualization, team collaboration, and advanced analysis

## Next Steps

- **Explore traces** in W&B dashboard
- **Set up alerts** for error rates or latency spikes
- **Create dashboards** for monitoring agent performance
- **Share projects** with team members for collaboration

## Support

- **W&B Documentation**: [https://docs.wandb.ai](https://docs.wandb.ai)
- **Weave Documentation**: [https://wandb.ai/weave](https://wandb.ai/weave)
- **Issues**: Check application logs for detailed error messages

