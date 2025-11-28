"""
Recruiter Email Pipeline Agent.

Implements a workflow to generate, display, and optionally refine
personalized outreach emails. The refiner only runs if the user requests it.
"""

from google.adk.agents import SequentialAgent

from .subagents.email_generator.agent import email_generator
from .subagents.email_refiner.agent import email_refiner
from .subagents.email_reviewer.agent import email_reviewer
from .subagents.email_presenter.agent import email_presenter


root_agent = SequentialAgent(
    name="RecruiterEmailPipeline",
    description="Generates recruiter outreach emails, displays them to the user, and optionally refines them if requested.",
    sub_agents=[email_generator, email_reviewer, email_refiner, email_presenter],
)

