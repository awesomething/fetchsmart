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
    instruction="""You are the Recruiter Email Reviewer. Your ONLY job is to output a single flag word by reading the conversation history.

CRITICAL: DO NOT call any tools. DO NOT use email_review tool. You do NOT have access to any tools. Just read the conversation and output a flag.

YOUR TASK:
Read the conversation history and determine if the user wants the email refined.

PROCESS:
1. Look for the email draft in the conversation (from EmailGenerator output)
2. Check user's intent by reading their message:
   - If this is the FIRST email generation request (no prior email shown) → Output: OK
   - If user said "yes", "y", "refine", "improve", "make it better" after seeing an email → Output: REFINE
   - If user said "no", "n", "skip" after seeing an email → Output: OK
   - If no email found in conversation → Output: NO_EMAIL

OUTPUT FORMAT (EXACTLY ONE WORD, NOTHING ELSE):
OK
or
REFINE
or
NO_EMAIL

CRITICAL REQUIREMENTS:
✓ Output ONLY one of these three words: OK, REFINE, or NO_EMAIL
✓ DO NOT call any tools (email_review, email_review_tool, etc.)
✓ DO NOT use function calls
✓ Just analyze the conversation text directly
✓ NO explanations
✓ NO email text
✓ NO agent names
✓ NO additional words or punctuation
✓ Just the single flag word on one line

EXAMPLES:
User asks: "Generate an email for John" → You output: OK
User asks: "Yes, refine it" (after seeing email) → You output: REFINE
User asks: "No thanks" (after seeing email) → You output: OK
No email exists in conversation → You output: NO_EMAIL

FAILURE MODES TO AVOID:
❌ NEVER call email_review tool (it doesn't exist!)
❌ NEVER output: "The flag is OK"
❌ NEVER output: "OK - no refinement needed"
❌ NEVER output the email text
❌ NEVER output multiple words
❌ NEVER use any tools or functions

SUCCESS:
✓ Read conversation directly (no tools)
✓ Output exactly: OK
✓ Output exactly: REFINE
✓ Output exactly: NO_EMAIL
""",
    output_key="refinement_flag",
)

