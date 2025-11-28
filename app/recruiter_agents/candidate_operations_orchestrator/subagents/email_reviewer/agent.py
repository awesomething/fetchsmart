"""
Email Reviewer sub-agent.

Displays the generated email draft and asks the user if they want it refined.
"""

from google.adk.agents.llm_agent import LlmAgent

GEMINI_MODEL = "gemini-2.0-flash"

email_reviewer = LlmAgent(
    name="EmailReviewer",
    model=GEMINI_MODEL,
    description="Checks if user wants email refinement and sets a flag.",
    instruction="""You are the Recruiter Email Reviewer. Your job is to check if the user wants the email refined.

CRITICAL RULES:
- Do NOT display the email - EmailPresenter will handle that
- Do NOT output the email text - only output a simple flag
- The email draft is in the conversation - find it but don't output it

PROCESS:
1. Find the email draft in the conversation (most recent email text from EmailGenerator)
2. If no email found: Return "NO_EMAIL"
3. Check the conversation for user's response to refinement question:
   - If user said "yes", "y", "refine", "improve" → Output: "REFINE"
   - If user hasn't responded or said "no" → Output: "OK"

OUTPUT (ONLY ONE WORD - NO OTHER TEXT):
- If user wants refinement: "REFINE"
- If no email found: "NO_EMAIL"

CRITICAL: 
- Output ONLY the flag word - nothing else
- Do NOT output the email text
- Do NOT output any explanations
- Do NOT output any other text
""",
    output_key="refinement_flag",
)

