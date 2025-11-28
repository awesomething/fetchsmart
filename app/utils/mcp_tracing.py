"""
MCP Tool Tracing Utilities

Provides OpenTelemetry instrumentation helpers for MCP tool calls.
Since ADK handles tool execution internally, this module provides utilities
to add tracing context and create spans for MCP operations.
"""

import logging
import time
from typing import Any

from opentelemetry import trace

logger = logging.getLogger(__name__)

tracer = trace.get_tracer(__name__)


def create_mcp_tool_span(
    tool_name: str,
    mcp_url: str,
    tool_filter: list[str] | None = None,
    agent_name: str | None = None,
) -> trace.Span:
    """
    Create an OpenTelemetry span for an MCP tool call.

    :param tool_name: Name of the MCP tool being called
    :param mcp_url: URL of the MCP server
    :param tool_filter: List of tool filters (if applicable)
    :param agent_name: Name of the agent making the call
    :return: OpenTelemetry span
    """
    span = tracer.start_span(
        name=f"mcp.tool.{tool_name}",
        attributes={
            "mcp.tool.name": tool_name,
            "mcp.server.url": mcp_url,
            "mcp.tool.agent": agent_name or "unknown",
        },
    )

    if tool_filter:
        span.set_attribute("mcp.tool.filter", ",".join(tool_filter))

    return span


def trace_mcp_tool_call(
    tool_name: str,
    mcp_url: str,
    parameters: dict[str, Any] | None = None,
    agent_name: str | None = None,
):
    """
    Context manager for tracing MCP tool calls.

    Usage:
        with trace_mcp_tool_call("search_jobs", mcp_url, {"job_title": "Engineer"}, "job_search_agent"):
            # Tool call happens here
            result = tool.call(...)

    :param tool_name: Name of the MCP tool
    :param mcp_url: URL of the MCP server
    :param parameters: Tool call parameters
    :param agent_name: Name of the agent making the call
    :return: Context manager that creates and manages a span
    """
    return _MCPToolCallTracer(tool_name, mcp_url, parameters, agent_name)


class _MCPToolCallTracer:
    """Context manager for tracing MCP tool calls."""

    def __init__(
        self,
        tool_name: str,
        mcp_url: str,
        parameters: dict[str, Any] | None = None,
        agent_name: str | None = None,
    ):
        self.tool_name = tool_name
        self.mcp_url = mcp_url
        self.parameters = parameters or {}
        self.agent_name = agent_name
        self.span: trace.Span | None = None
        self.start_time: float | None = None

    def __enter__(self) -> trace.Span:
        """Enter the context and create a span."""
        self.start_time = time.time()
        self.span = create_mcp_tool_span(
            self.tool_name, self.mcp_url, agent_name=self.agent_name
        )

        # Add parameters as span attributes (truncate if too large)
        if self.parameters:
            for key, value in self.parameters.items():
                attr_value = str(value)
                if len(attr_value) > 1000:
                    attr_value = attr_value[:1000] + "... [truncated]"
                self.span.set_attribute(f"mcp.tool.param.{key}", attr_value)

        return self.span

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        """Exit the context and finalize the span."""
        if self.span is None:
            return

        # Calculate duration
        if self.start_time:
            duration = time.time() - self.start_time
            self.span.set_attribute("mcp.tool.duration_seconds", duration)

        # Record error if exception occurred
        if exc_type is not None:
            self.span.record_exception(exc_val)
            self.span.set_status(
                trace.Status(trace.StatusCode.ERROR, str(exc_val) if exc_val else "")
            )
            logger.error(
                f"MCP tool call failed: {self.tool_name} - {exc_type.__name__}: {exc_val}"
            )
        else:
            self.span.set_status(trace.Status(trace.StatusCode.OK))

        self.span.end()


def add_mcp_tool_result_to_span(
    span: trace.Span,
    result: Any,
    result_size_limit: int = 10000,
) -> None:
    """
    Add tool call result to an existing span.

    :param span: OpenTelemetry span
    :param result: Tool call result
    :param result_size_limit: Maximum size of result to store (in characters)
    """
    try:
        result_str = str(result)
        if len(result_str) > result_size_limit:
            result_str = result_str[:result_size_limit] + "... [truncated]"
            span.set_attribute("mcp.tool.result_truncated", True)

        span.set_attribute("mcp.tool.result", result_str)
        span.set_attribute("mcp.tool.result_size", len(str(result)))
    except Exception as e:
        logger.warning(f"Failed to add result to span: {e}")
        span.set_attribute("mcp.tool.result_error", str(e))

