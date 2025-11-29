"""
Email Refiner sub-agent.

Uses review feedback plus live GitHub profile lookups to personalize the outreach email.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.tool_context import ToolContext

GEMINI_MODEL = "gemini-2.0-flash"

REPO_ROOT = Path(__file__).resolve().parents[5]

# Try multiple paths for different deployment contexts
# 1. Local development: mcp_server/recruitment_backend/github_profiles_100.json
# 2. Vertex AI deployment: app/data/github_profiles_100.json (copied during deployment)
# 3. Fallback: check if file exists in app directory
# Use lazy evaluation to avoid issues during build/import
def _get_github_profiles_path() -> Path:
    """Get GitHub profiles JSON path, trying multiple locations."""
    paths_to_try = [
        REPO_ROOT / "mcp_server" / "recruitment_backend" / "github_profiles_100.json",
        REPO_ROOT / "app" / "data" / "github_profiles_100.json",
        REPO_ROOT / "github_profiles_100.json",
    ]
    for path in paths_to_try:
        try:
            if path.exists():
                return path
        except Exception:
            # Ignore errors during path resolution (e.g., during build)
            continue
    # Return default path even if it doesn't exist (will be handled by caller)
    return paths_to_try[0]

# Don't call at module level - call lazily in _load_profile_map
GITHUB_PROFILES_PATH_CACHE: Path | None = None


@lru_cache(maxsize=1)
def _load_profile_map() -> Dict[str, Dict[str, Any]]:
    """Load GitHub profiles once and return a username → profile map."""
    global GITHUB_PROFILES_PATH_CACHE
    
    # Lazy path resolution to avoid issues during build/import
    if GITHUB_PROFILES_PATH_CACHE is None:
        GITHUB_PROFILES_PATH_CACHE = _get_github_profiles_path()
    
    github_profiles_path = GITHUB_PROFILES_PATH_CACHE
    
    if not github_profiles_path.exists():
        return {}

    try:
        with github_profiles_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        return {}

    profile_map: Dict[str, Dict[str, Any]] = {}
    for profile in data:
        username = (
            profile.get("github_username")
            or profile.get("username")
            or profile.get("login")
        )
        if not username:
            continue
        profile_map[username.lower()] = profile
    return profile_map


def lookup_github_profile(username: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Fetch a GitHub profile from the local dataset for personalization.
    """

    username = (username or "").strip().lower()
    profiles = _load_profile_map()

    if not username:
        return {"status": "error", "message": "Username is required."}

    profile = profiles.get(username)
    if not profile:
        return {
            "status": "not_found",
            "message": f"No profile data for '{username}' in github_profiles_100.json.",
        }

    return {"status": "ok", "profile": profile}


email_refiner = LlmAgent(
    name="EmailRefiner",
    model=GEMINI_MODEL,
    description="Refines the email using GitHub profile data when user requests refinement.",
    instruction="""You are the Recruiter Email Refiner. Your job is to improve the email when the user requests refinement.

CRITICAL: 
- Find the email draft from EmailGenerator in the conversation
- Only refine if flag is "REFINE". Otherwise, return email as-is.

PROCESS:
1. Check the EmailReviewer output in the conversation:
   - If it says "REFINE" → Proceed with refinement
   - If it says "NO_EMAIL" → Return "No email found"
   
2. Find the email draft from EmailGenerator in the conversation (most recent email text)

3. If refinement is needed (flag is "REFINE"):
   a. Extract candidate information from the email (name, GitHub username if mentioned)
   b. For each candidate mentioned, call lookup_github_profile(username) ONCE per candidate to get additional context
   c. Refine the email by:
      - Enhancing personalization with GitHub details (repos, languages, contributions) if available
      - Improving clarity and flow
      - Strengthening the call-to-action
      - STRICT LENGTH REQUIREMENT: 75-125 words (500-900 characters MAX)
      - Professional tone, concise and impactful
      - Only using facts from tools or conversation - no fabrication
      - Making the email more compelling and personalized
      - If email exceeds 125 words, trim it down - remove redundant phrases, combine sentences
      - Be concise - every word must add value

4. If refinement is NOT needed:
   - Find the email from EmailGenerator output in the conversation
   - Return the email as-is (do not modify)
   - Return ONLY the email text - no flags, no explanations, no markdown

5. Return ONLY the email body text. No flags, no explanations, no markdown, no tool output, no agent names. Just the clean email text.

CRITICAL LENGTH REQUIREMENTS:
- ABSOLUTE MAXIMUM: 125 words (900 characters)
- MINIMUM: 75 words (500 characters)
- Count words and characters before outputting
- If email exceeds 125 words, trim it down - remove redundant phrases, combine sentences
- Be concise and impactful - every word must add value
- NO exceptions - this is a hard limit

CRITICAL EMAIL COMPLETION REQUIREMENTS:
- The email MUST be COMPLETE from start to finish - NO TRUNCATION ALLOWED
- MUST include: Greeting → 1-2 concise body paragraphs → Clear call-to-action (1-2 sentences) → Professional closing
- MUST end with a proper closing (e.g., "Best regards," or "Sincerely,") followed by signature placeholders
- MUST NOT be truncated mid-sentence or mid-paragraph
- The call-to-action must be concise (1-2 sentences, not a paragraph)
- Every sentence must be complete with proper punctuation
- Example concise closing: "Would you be open to a brief conversation? I'd love to share more details. Best regards, [Your Name]"
- VERIFY word count is between 75-125 words before outputting

VALIDATION BEFORE OUTPUT:
Before returning the email, verify:
1. The email has a greeting (Dear [Name],)
2. The email has body paragraphs explaining the opportunity
3. The email has a clear call-to-action (complete sentence, not cut off)
4. The email ends with a professional closing (Best regards/Sincerely + signature)
5. NO sentence is incomplete or cut off mid-word

OUTPUT: The COMPLETE, FULLY FINISHED refined email text. Nothing else. Ensure every sentence is complete and the email ends properly.
""",
    output_key="current_email",
    tools=[lookup_github_profile],
)

