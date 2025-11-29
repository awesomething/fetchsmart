"""
Weave (Weights & Biases) OpenTelemetry Span Exporter

This module provides integration between OpenTelemetry tracing and Weave/W&B
for visualizing agent and tool call traces using Weave's native SDK.
"""

import logging
import os
from collections.abc import Sequence
from typing import Any

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

logger = logging.getLogger(__name__)

try:
    import weave
    import wandb
except ImportError:
    weave = None
    wandb = None
    logger.warning("weave or wandb not installed. Weave tracing will be disabled.")


class WeaveSpanExporter(SpanExporter):
    """
    OpenTelemetry span exporter that sends traces to Weave (Weights & Biases) using Weave's native SDK.

    This exporter converts OpenTelemetry spans to Weave traces and logs them using Weave's API.
    It works alongside Cloud Trace to provide dual export of traces for comprehensive
    observability of ADK agents and MCP tool calls.
    """

    def __init__(
        self,
        project: str | None = None,
        entity: str | None = None,
        api_key: str | None = None,
        service_name: str = "adk-agent",
        debug: bool = False,
    ) -> None:
        """
        Initialize the Weave span exporter using Weave's native SDK.

        :param project: W&B project name (defaults to WANDB_PROJECT env var)
        :param entity: W&B entity/username (defaults to WANDB_ENTITY env var)
        :param api_key: W&B API key (defaults to WANDB_API_KEY env var)
        :param service_name: Service name for span attribution
        :param debug: Enable debug logging
        """
        if weave is None or wandb is None:
            raise ImportError(
                "weave and wandb not installed. Install with: pip install weave wandb"
            )

        self.service_name = service_name
        self.debug = debug

        # Get configuration from parameters or environment variables
        self.project = project or os.environ.get("WANDB_PROJECT")
        self.entity = entity or os.environ.get("WANDB_ENTITY")
        self.api_key = api_key or os.environ.get("WANDB_API_KEY")

        if not self.project:
            raise ValueError(
                "W&B project not specified. Set WANDB_PROJECT environment variable or pass project parameter."
            )

        # Set up W&B authentication
        if self.api_key:
            os.environ["WANDB_API_KEY"] = self.api_key

        # Initialize wandb (required for Weave)
        try:
            # Initialize wandb run for tracing (entity is set via wandb, not weave)
            wandb.init(
                project=self.project,
                entity=self.entity,
                name=f"{self.service_name}-traces",
                job_type="tracing",
                reinit=True,
                mode="online" if self.api_key else "disabled",
            )
            
            # Initialize Weave (only accepts project_name, entity is handled by wandb)
            weave.init(project_name=self.project)
            
            if self.debug:
                logger.info(
                    f"✅ Weave initialized: project={self.project}, entity={self.entity or 'default'}, wandb_run={wandb.run.id if wandb.run else 'None'}"
                )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Weave: {e}")
            if self.debug:
                import traceback
                logger.error(traceback.format_exc())
            raise

        # Track spans for batch export
        self._span_buffer: list[dict[str, Any]] = []


    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans to Weave using Weave's native API.

        :param spans: A sequence of spans to export
        :return: The result of the export operation
        """
        if not spans:
            return SpanExportResult.SUCCESS

        try:
            for span in spans:
                self._export_span_to_weave(span)

            if self.debug:
                logger.debug(f"✅ Exported {len(spans)} span(s) to Weave")

            return SpanExportResult.SUCCESS
        except Exception as e:
            logger.error(f"❌ Failed to export spans to Weave: {e}")
            if self.debug:
                import traceback
                logger.error(traceback.format_exc())
            return SpanExportResult.FAILURE

    def _export_span_to_weave(self, span: ReadableSpan) -> None:
        """
        Convert an OpenTelemetry span to a Weave trace and log it.

        :param span: The OpenTelemetry span to export
        """
        try:
            span_context = span.get_span_context()
            if span_context is None:
                return

            # Convert span to Weave trace format
            trace_data = {
                "name": span.name,
                "start_time_ms": span.start_time // 1_000_000,  # Convert nanoseconds to milliseconds
                "end_time_ms": span.end_time // 1_000_000 if span.end_time else None,
                "duration_ms": (span.end_time - span.start_time) // 1_000_000 if span.end_time else None,
                "status": str(span.status.status_code),
                "attributes": self._format_attributes(span.attributes or {}),
                "service_name": self.service_name,
            }

            # Add trace context
            if span_context:
                trace_data["trace_id"] = format(span_context.trace_id, "x")
                trace_data["span_id"] = format(span_context.span_id, "x")
                if span.parent:
                    trace_data["parent_span_id"] = format(span.parent.span_id, "x")

            # Add events if present
            if span.events:
                trace_data["events"] = [
                    {
                        "name": event.name,
                        "timestamp_ms": event.timestamp // 1_000_000,
                        "attributes": self._format_attributes(event.attributes or {}),
                    }
                    for event in span.events
                ]

            # Log to Weave using weave.log_call() which is the proper API for logging traces
            # Weave tracks function calls, so we create a synthetic call for each span
            try:
                # Ensure wandb run is active (required for Weave)
                if not wandb.run:
                    wandb.init(
                        project=self.project,
                        entity=self.entity,
                        name=f"{self.service_name}-traces",
                        job_type="tracing",
                        reinit=True,
                        mode="online" if self.api_key else "disabled",
                    )
                
                # Use weave.log_call() to log the span as a trace
                # This is the proper way to send traces to Weave
                import time
                
                # Create a call object that Weave can visualize
                call_data = {
                    "name": span.name,
                    "inputs": trace_data.get("attributes", {}),
                    "output": {
                        "status": trace_data.get("status"),
                        "duration_ms": trace_data.get("duration_ms"),
                        "trace_id": trace_data.get("trace_id"),
                        "span_id": trace_data.get("span_id"),
                    },
                    "metadata": {
                        "service_name": self.service_name,
                        "start_time_ms": trace_data.get("start_time_ms"),
                        "end_time_ms": trace_data.get("end_time_ms"),
                    }
                }
                
                # Log the call to Weave using weave.log_call() - the proper API
                if hasattr(weave, "log_call"):
                    weave.log_call(
                        op=span.name,
                        inputs=trace_data.get("attributes", {}),
                        output=call_data["output"],
                        attributes=call_data["metadata"],
                    )
                else:
                    # Fallback: log to wandb in structured format
                    wandb.log({
                        f"trace/{span.name}": call_data,
                        "span_name": span.name,
                        "trace_id": trace_data.get("trace_id"),
                        "span_id": trace_data.get("span_id"),
                    }, step=int(trace_data.get("start_time_ms", 0) / 1000) if trace_data.get("start_time_ms") else None)

                if self.debug:
                    logger.debug(f"  - Logged span to Weave: {span.name} (run_id: {wandb.run.id if wandb.run else 'None'})")
            except Exception as e:
                logger.error(f"❌ Failed to log span to Weave: {e}")
                if self.debug:
                    import traceback
                    logger.error(traceback.format_exc())
                # Don't raise - allow tracing to continue even if Weave export fails
                pass

        except Exception as e:
            logger.error(f"❌ Failed to export span {span.name} to Weave: {e}")
            if self.debug:
                import traceback
                logger.error(traceback.format_exc())

    def _format_attributes(self, attributes: dict[str, Any]) -> dict[str, Any]:
        """
        Format span attributes for Weave export.

        :param attributes: Raw span attributes
        :return: Formatted attributes dictionary
        """
        formatted = {}
        for key, value in attributes.items():
            try:
                # Convert non-serializable types to strings
                if isinstance(value, (bytes, bytearray)):
                    formatted[key] = value.decode("utf-8", errors="ignore")
                elif isinstance(value, (list, tuple)):
                    # Truncate very long lists
                    if len(value) > 100:
                        formatted[key] = f"[{len(value)} items, truncated]"
                    else:
                        formatted[key] = [
                            str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                            for v in value
                        ]
                elif isinstance(value, dict):
                    # Recursively format nested dicts
                    formatted[key] = self._format_attributes(value)
                elif isinstance(value, str) and len(value) > 10000:
                    # Truncate very long strings
                    formatted[key] = value[:10000] + "... [truncated]"
                else:
                    formatted[key] = value
            except Exception as e:
                # If we can't format the value, store as string representation
                formatted[key] = f"<unserializable: {type(value).__name__}>"
                if self.debug:
                    logger.warning(f"Could not format attribute {key}: {e}")

        return formatted

    def shutdown(self) -> None:
        """
        Shutdown the exporter and clean up resources.
        """
        try:
            # Weave doesn't need explicit shutdown, but we can finish any active runs
            if hasattr(weave, "finish"):
                weave.finish()
            logger.info("Weave exporter shut down")
        except Exception as e:
            logger.warning(f"Error shutting down Weave exporter: {e}")

