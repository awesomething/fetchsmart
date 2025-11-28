"""
Utility tools for the Email Reviewer.
"""

from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext


def exit_loop(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Exit the refinement loop when the email passes all checks.

    Sets the escalate flag so the LoopAgent stops iterating.
    """

    tool_context.actions.escalate = True
    return {"status": "loop_exit_triggered"}

