"""
Recruiter Orchestrator Agent for ADK integration.
Export the agent for use in the root agent.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
from google.adk.agents import LlmAgent

# ---------------------------------------------------------------------------
# Default profile overrides (used by UI mock data & email lookup prompt)
# ---------------------------------------------------------------------------
DEFAULT_PROFILE_OVERRIDES: Dict[str, Dict[str, Any]] = {
    "awesomething": {
        "id": "CAND-001",
        "name": "awesomething",
        "github_username": "awesomething",
        "github_profile_url": "https://github.com/awesomething",
        "role": "Senior Software Engineer",
        "experience_level": "8 years exp",
        "experience_years": 8,
        "location": "Remote - US",
        "primary_language": "Python",
        "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "MCP"],
        "github_stats": {"repos": 342, "stars": 285, "followers": 27, "commits": 3421},
        "email": "awesomething@github.com",
        "match_score": 92,
    },
    "mithonmasud": {
        "id": "CAND-002",
        "name": "Mithonmasud",
        "github_username": "Mithonmasud",
        "github_profile_url": "https://github.com/Mithonmasud",
        "role": "Full Stack Engineer",
        "experience_level": "6 years exp",
        "experience_years": 6,
        "location": "San Francisco, CA",
        "primary_language": "TypeScript",
        "skills": ["TypeScript", "React", "Node.js", "GraphQL", "PostgreSQL"],
        "github_stats": {"repos": 38, "stars": 156, "followers": 892},
        "email": "mithonmasud@github.com",
        "match_score": 88,
    },
    "marquish": {
        "id": "CAND-003",
        "name": "Marquish",
        "github_username": "Marquish",
        "github_profile_url": "https://github.com/Marquish",
        "role": "Backend Engineer",
        "experience_level": "7 years exp",
        "experience_years": 7,
        "location": "Austin, TX",
        "primary_language": "Go",
        "skills": ["Go", "Rust", "Kubernetes", "Docker", "Microservices"],
        "github_stats": {"repos": 29, "stars": 412, "followers": 1589, "commits": 4123},
        "email": "marquish@github.com",
        "match_score": 95,
    },
    "ekeneakubue": {
        "id": "CAND-004",
        "name": "Ekeneakubue",
        "github_username": "Ekeneakubue",
        "github_profile_url": "https://github.com/Ekeneakubue",
        "role": "DevOps Engineer",
        "experience_level": "5 years exp",
        "experience_years": 5,
        "location": "Remote - Global",
        "primary_language": "AWS",
        "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "Python"],
        "github_stats": {"repos": 31, "stars": 198, "followers": 743, "commits": 1876},
        "email": "ekeneakubue@github.com",
        "match_score": 86,
    },
    "sarahchen": {
        "id": "CAND-005",
        "name": "Sarah Chen",
        "github_username": "sarahchen",
        "github_profile_url": "https://github.com/sarahchen",
        "role": "Frontend Engineer",
        "experience_level": "4 years exp",
        "experience_years": 4,
        "location": "Seattle, WA",
        "primary_language": "JavaScript",
        "skills": ["React", "Vue.js", "TypeScript", "CSS", "Webpack"],
        "github_stats": {"repos": 52, "stars": 324, "followers": 567, "commits": 2890},
        "email": "sarahchen@github.com",
        "match_score": 84,
    },
    "olafaloofian": {
        "id": "CAND-006",
        "name": "Michael Kerr",
        "github_username": "Olafaloofian",
        "github_profile_url": "https://github.com/Olafaloofian",
        "role": "Senior Full Stack Engineer",
        "experience_level": "10 years exp",
        "experience_years": 10,
        "location": "Remote - US",
        "primary_language": "Python",
        "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes"],
        "github_stats": {"repos": 106, "stars": 285, "followers": 58, "commits": 3421},
        "email": "olafaloofian@github.com",
        "match_score": 87,
    },
    "xiiiiiiiiii": {
        "id": "CAND-007",
        "name": "xiiiiiiiiii",
        "github_username": "xiiiiiiiiii",
        "github_profile_url": "https://github.com/xiiiiiiiiii",
        "role": "Data Engineer",
        "experience_level": "10 years exp",
        "experience_years": 10,
        "location": "San Francisco, CA",
        "primary_language": "Python",
        "skills": ["Python", "Spark", "Airflow", "SQL", "Data Pipelines", "MCP"],
        "github_stats": {"repos": 27, "stars": 178, "followers": 312, "commits": 1654},
        "email": "xiiiiiiiiii@github.com",
        "match_score": 81,
    },
    "rowens72": {
        "id": "CAND-008",
        "name": "Rowens72",
        "github_username": "Rowens72",
        "github_profile_url": "https://github.com/Rowens72",
        "role": "Security Engineer",
        "experience_level": "8 years exp",
        "experience_years": 8,
        "location": "London, UK",
        "primary_language": "Rust",
        "skills": ["Rust", "Security", "Dotnet", "C#", "Network Security", "Penetration Testing"],
        "github_stats": {"repos": 19, "stars": 456, "followers": 892, "commits": 1432},
        "email": "rowens72@github.com",
        "match_score": 93,
    },
}

# ---------------------------------------------------------------------------
# Recruitment backend access (for candidate search)
# ---------------------------------------------------------------------------

# Add MCP server path so we can import the in-process recruitment backend
mcp_server_path = Path(__file__).parent.parent.parent.parent / "mcp_server" / "recruitment_backend"
if mcp_server_path.exists():
    sys.path.insert(0, str(mcp_server_path))
    print(f"[INFO] Added MCP server path: {mcp_server_path}")
else:
    print(f"[WARN] MCP server path does not exist: {mcp_server_path}")

# Import recruitment backend services (for search_candidates_tool only)
try:
    from recruitment_service import recruitment_service
except ImportError:
    recruitment_service = None
    print("[WARN] recruitment_service not available - candidate search will be limited")

# Email lookup will be implemented locally in this file so it does NOT depend
# on importing anything from the recruitment backend. This avoids import-path
# issues when running in different environments (Vertex, local CLI, etc.).

# ============================================================================
# MCP Tool: Search Candidates
# ============================================================================
def search_candidates_tool(
    job_description: str,
    job_title: str = "",
    limit: int = 8
) -> str:
    """
    Search for candidates matching job requirements using the recruitment backend data.
    """
    if recruitment_service is None:
        return json.dumps({
            "error": "Recruitment backend not available - ensure mcp_server/recruitment_backend is accessible",
            "status": "failed"
        })

    try:
        candidates = recruitment_service.candidates
        matcher = getattr(recruitment_service, "matcher", None)

        if not matcher:
            return json.dumps({
                "error": "Candidate matcher not available",
                "status": "failed"
            })

        results = matcher.match_candidates(
            candidates=candidates,
            job_description=job_description,
            job_title=job_title,
            limit=limit
        )

        response = {
            "query": job_description,
            "job_title": job_title,
            "total_matches": results.get("total_matches"),
            "showing_top": results.get("showing"),
            "requirements_detected": results.get("requirements"),
            "top_candidates": []
        }

        for match in results.get("top_candidates", []):
            candidate = match.get("candidate", {})
            likely_roles = candidate.get("likely_roles") or []
            role = likely_roles[0] if likely_roles else "Software Engineer"
            candidate_id = candidate.get("id") or candidate.get("github_username") or "unknown"

            response["top_candidates"].append({
                "id": candidate_id,
                "name": candidate.get("name") or candidate.get("github_username", "Unknown"),
                "github_username": candidate.get("github_username", ""),
                "github_profile_url": candidate.get("github_profile_url", ""),
                "role": role,
                "experience_level": candidate.get("estimated_experience_level", "Mid"),
                "location": candidate.get("location", ""),
                "primary_language": candidate.get("primary_language", ""),
                "skills": (candidate.get("skills") or [])[:8],
                "github_stats": {
                    "repos": candidate.get("public_repos", 0),
                    "stars": candidate.get("total_stars", 0),
                    "followers": candidate.get("followers", 0),
                },
                "match_score": match.get("match_score", 0),
                "match_reasons": match.get("match_reasons", []),
                "matched_skills": match.get("matched_skills", []),
            })

        return json.dumps(response, indent=2)
    except Exception as error:
        return json.dumps({
            "error": f"Recruitment backend tool error: {error}",
            "status": "failed"
        })

# ---------------------------------------------------------------------------
# Local email lookup tools (Hunter API) - NO backend imports required
# ---------------------------------------------------------------------------

def _parse_candidates_payload(candidates_json: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Parse candidate payloads coming from either:
    - The raw list of candidates
    - The full search JSON with `top_candidates`
    Returns (is_nested, candidate_list).
    """
    data: Any = candidates_json
    if isinstance(candidates_json, str):
        data = json.loads(candidates_json)

    # Nested structure from search_candidates_tool
    if isinstance(data, dict) and "top_candidates" in data:
        candidates = data.get("top_candidates") or []
        if not isinstance(candidates, list):
            raise ValueError("top_candidates must be a list")
        return True, candidates

    # Direct list of candidates
    if isinstance(data, list):
        return False, data

    raise ValueError("Invalid candidates format - expected list or dict with 'top_candidates' key")


def _apply_candidates_back(
    original_json: str, is_nested: bool, updated_candidates: List[Dict[str, Any]]
) -> str:
    """Re-attach updated candidates into the original JSON structure."""
    data = json.loads(original_json)
    if is_nested:
        data["top_candidates"] = updated_candidates
        return json.dumps(data, indent=2)
    return json.dumps(updated_candidates, indent=2)


def _normalized_name_and_username(candidate: Dict[str, Any]) -> Tuple[str, str]:
    """Return (full_name, github_username) with safe defaults."""
    username = (candidate.get("github_username") or "").strip()
    full_name = (candidate.get("name") or "").strip()
    if not full_name:
        full_name = username
    return full_name, username


def _lookup_dataset_candidate(github_username: str | None, name: str | None) -> Dict[str, Any] | None:
    """Look up candidate information in overrides or recruitment_service dataset."""
    username_key = (github_username or "").lower()
    name_key = (name or "").lower()

    # Check overrides first (ensures mock/default profiles have data)
    if username_key in DEFAULT_PROFILE_OVERRIDES:
        return DEFAULT_PROFILE_OVERRIDES[username_key]
    if name_key in DEFAULT_PROFILE_OVERRIDES:
        return DEFAULT_PROFILE_OVERRIDES[name_key]

    if not recruitment_service or not hasattr(recruitment_service, "candidates"):
        return None

    try:
        for cand in getattr(recruitment_service, "candidates", []):
            cand_username = (cand.get("github_username") or "").lower()
            cand_name = (cand.get("name") or "").lower()
            if username_key and cand_username == username_key:
                return cand
            if name_key and cand_name == name_key:
                return cand
    except Exception:
        return None
    return None


def _call_hunter_api(first_name: str, last_name: str | None, api_key: str) -> Tuple[str | None, int | None]:
    """
    Minimal Hunter API wrapper using only name-based lookup.
    Domain is intentionally omitted so we don't rely on company data.
    """
    if not first_name:
        return None, None

    params: Dict[str, Any] = {
        "api_key": api_key,
        "first_name": first_name,
    }
    if last_name:
        params["last_name"] = last_name

    try:
        resp = requests.get("https://api.hunter.io/v2/email-finder", params=params, timeout=10)
    except requests.RequestException:
        return None, None

    if resp.status_code != 200:
        return None, None

    payload = resp.json() or {}
    data = payload.get("data") or {}
    email = data.get("email")
    score = data.get("score")
    return email, score


def find_candidate_emails_tool(candidates_json: str) -> str:
    """
    Find email addresses for candidates using Hunter API.

    This version is self-contained and does NOT rely on importing any backend
    modules, so it works consistently in Vertex / CLI / local environments.
    """
    api_key = os.getenv("HUNTER_API_KEY", "")
    if not api_key:
        return json.dumps(
            {
                "status": "error",
                "message": "HUNTER_API_KEY not configured. Please set HUNTER_API_KEY in the environment.",
                "candidates": json.loads(candidates_json),
            }
        )

    try:
        is_nested, candidates = _parse_candidates_payload(candidates_json)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Invalid candidates payload: {e}"})

    updated: List[Dict[str, Any]] = []

    for cand in candidates:
        cand = dict(cand)  # shallow copy to avoid mutating original

        # Look up dataset information first (covers our curated GitHub profiles)
        dataset_cand = _lookup_dataset_candidate(cand.get("github_username"), cand.get("name"))
        dataset_email = dataset_cand.get("email") if dataset_cand else None
        if dataset_email:
            cand["email"] = dataset_email
            cand["email_confidence"] = 100
            cand["email_source"] = "recruitment_database"
            updated.append(cand)
            continue

        # If email already present we keep it
        if cand.get("email"):
            updated.append(cand)
            continue

        full_name, username = _normalized_name_and_username(cand)
        parts = full_name.split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else None

        email, score = _call_hunter_api(first_name, last_name, api_key)
        if email:
            cand["email"] = email
            cand["email_confidence"] = score
            cand["email_source"] = "hunter_api"
        else:
            cand.setdefault("email", None)
            cand.setdefault("email_confidence", None)
            cand.setdefault("email_source", None)

        updated.append(cand)

    return _apply_candidates_back(candidates_json, is_nested, updated)


def find_emails_by_github_usernames_tool(github_usernames: str) -> str:
    """
    Direct email lookup for GitHub usernames using Hunter API.

    This is primarily for the "default profiles" / testing flow where we only
    have usernames and no prior search result JSON.
    """
    api_key = os.getenv("HUNTER_API_KEY", "")
    if not api_key:
        return json.dumps(
            {
                "status": "error",
                "message": "HUNTER_API_KEY not configured. Please set HUNTER_API_KEY in the environment.",
                "top_candidates": [],
            }
        )

    usernames = [u.strip() for u in github_usernames.split(",") if u.strip()]
    if not usernames:
        return json.dumps(
            {"status": "error", "message": "No GitHub usernames provided", "top_candidates": []}
        )

    results: List[Dict[str, Any]] = []
    for username in usernames:
        dataset_cand = _lookup_dataset_candidate(username, username)
        if dataset_cand:
            stats = dataset_cand.get("github_stats") or {}
            candidate: Dict[str, Any] = {
                "id": dataset_cand.get("id") or username,
                "name": dataset_cand.get("name") or username,
                "github_username": dataset_cand.get("github_username") or username,
                "github_profile_url": dataset_cand.get("github_profile")
                or dataset_cand.get("github_profile_url")
                or f"https://github.com/{username}",
                "role": dataset_cand.get("role") or "Software Engineer",
                "experience_level": dataset_cand.get("experience_level")
                or dataset_cand.get("system_design_level")
                or (f"{dataset_cand.get('experience_years')} years" if dataset_cand.get("experience_years") else "Mid"),
                "location": dataset_cand.get("location") or "",
                "primary_language": dataset_cand.get("primary_language") or "",
                "skills": (dataset_cand.get("skills") or [])[:8],
                "github_stats": {
                    "repos": stats.get("repos")
                    or dataset_cand.get("github_repos")
                    or dataset_cand.get("public_repos")
                    or 0,
                    "stars": stats.get("stars")
                    or dataset_cand.get("github_stars")
                    or dataset_cand.get("total_stars")
                    or 0,
                    "followers": stats.get("followers") or dataset_cand.get("followers") or 0,
                },
                "match_score": dataset_cand.get("match_score")
                or dataset_cand.get("coding_assessment_score")
                or 0,
            }
            email = dataset_cand.get("email")
            if email:
                candidate["email"] = email
                candidate["email_confidence"] = 100
                candidate["email_source"] = "recruitment_database"
                results.append(candidate)
                continue
        else:
            candidate = {
                "id": username,
                "name": username,
                "github_username": username,
                "github_profile_url": f"https://github.com/{username}",
                "role": "Software Engineer",
                "experience_level": "Mid",
                "location": "",
                "primary_language": "",
                "skills": [],
                "github_stats": {"repos": 0, "stars": 0, "followers": 0},
                "match_score": 0,
            }

        # Treat username as both name and GitHub handle for Hunter fallback
        parts = username.split()
        first_name = parts[0] if parts else username
        last_name = " ".join(parts[1:]) if len(parts) > 1 else None

        email, score = _call_hunter_api(first_name, last_name, api_key)
        candidate["email"] = email
        candidate["email_confidence"] = score
        candidate["email_source"] = "hunter_api" if email else None
        results.append(candidate)

    response = {
        "query": f"Email lookup for GitHub users: {github_usernames}",
        "total_matches": len(results),
        "showing_top": len(results),
        "top_candidates": results,
    }
    return json.dumps(response, indent=2)

# Build tools list – all functions are local and always available
tools_list = [search_candidates_tool, find_candidate_emails_tool, find_emails_by_github_usernames_tool]

print("[INFO] ========================================")
print("[INFO] Recruiter Orchestrator Agent Setup")
print("[INFO] ========================================")
print("[INFO] Tools registered:")
print("  - search_candidates_tool: ✅ (local)")
print("  - find_candidate_emails_tool: ✅ (local Hunter API)")
print("  - find_emails_by_github_usernames_tool: ✅ (local Hunter API)")
print(f"[INFO] Total tools in list: {len(tools_list)}")
print(f"[INFO] Tool names: {[tool.__name__ for tool in tools_list]}")
print("[INFO] ========================================")

# Create the agent
recruiter_orchestrator_agent = LlmAgent(
    name="RecruiterOrchestrator",
    model="gemini-2.0-flash",
    description="Tech recruitment and talent acquisition orchestrator managing candidate sourcing, screening, portfolio analysis, compensation, and productivity tracking",
    tools=tools_list,
    instruction="""
    You are the Recruiter Orchestrator for tech recruiting operations.
    
    You have access to the `search_candidates_tool` function that connects to a recruitment database
    with real candidate profiles from GitHub.
    
    **CRITICAL - When to Use search_candidates_tool:**
    
    USE the tool when the user asks to:
    - "Find" or "Search for" candidates (e.g., "Find senior TypeScript engineers")
    - "Show me" candidates for a role
    - "Get" or "List" candidates matching criteria
    - Any request for actual candidate profiles
    
    DO NOT use the tool when the user asks for:
    - General advice about recruiting
    - Compensation information
    - Interview questions or strategies
    - Recruiting process guidance
    
    **How to Use search_candidates_tool:**
    
    1. Extract the key requirements from the user's query:
       - Job description: Main skills, technologies, role requirements
       - Job title: The position (e.g., "Senior Backend Engineer", "React Developer")
       - Limit: Number of candidates (default 8, max 20)
    
    2. Call the tool:
       ```
       search_candidates_tool(
           job_description="Senior engineer with TypeScript, React, and Node.js experience",
           job_title="Senior Full Stack Engineer",
           limit=10
       )
       ```
    
    3. **CRITICAL**: The tool returns JSON with candidate data. You MUST return ONLY the raw JSON 
       response from the tool - DO NOT add any commentary, formatting, or additional text.
       Just return the exact JSON string you receive from the tool.
    
    **Response Format After Using Tool:**
    
    Return ONLY the raw JSON from search_candidates_tool, nothing else.
    The frontend will automatically parse and display the candidates in a beautiful card layout.
    
    Example response (return EXACTLY what the tool gives you):
    ```json
    {
      "query": "React developer",
      "job_title": "React Developer",
      "total_matches": 26,
      "showing_top": 5,
      "requirements_detected": {...},
      "top_candidates": [...]
    }
    ```
    
    DO NOT add:
    - "Here are the results..."
    - "I found X candidates..."
    - Match summaries or explanations
    - Next steps or recommendations
    
    The frontend handles all the presentation. Your job is to:
    1. Call the tool with the right parameters
    2. Return the JSON response immediately
    3. Nothing else!
    
    **Email Lookup - TWO DISTINCT SCENARIOS:**
    
    **PRIORITY: Scenario 1 - After Candidate Search (NORMAL FLOW)**
    
    This is the PRIMARY and MOST COMMON flow:
    
    1. User searches for candidates (e.g., "Find senior engineers")
    2. You call `search_candidates_tool` and return the JSON response
    
    3. **CRITICAL - When User Asks for Emails:**
       If the user asks for emails (says "yes", "please", "sure", "get emails", "find emails", "email addresses", etc.), 
       you MUST:
       
       a. First, call `search_candidates_tool` again with the SAME parameters from the previous search
          (This retrieves the candidate JSON you need)
       
       b. Then IMMEDIATELY call `find_candidate_emails_tool` with the search results JSON
       
       c. Return ONLY the updated JSON from `find_candidate_emails_tool` - this will have email fields added
    
    **Example normal flow:**
    ```
    # Step 1: User asks "Find senior engineers"
    search_results = search_candidates_tool(job_description="senior engineers", limit=8)
    # Return search_results JSON
    
    # Step 2: User says "yes" or "get emails"
    # Re-search to get the JSON (since you don't have memory of previous calls)
    search_results_again = search_candidates_tool(job_description="senior engineers", limit=8)
    # Then immediately call email lookup
    updated_results = find_candidate_emails_tool(search_results_again)
    # Return updated_results JSON with emails - DO NOT return search_results_again!
    ```
    
    **IMPORTANT**: When returning email lookup results, return ONLY the JSON from `find_candidate_emails_tool`.
    Do NOT return the original search results. The email lookup tool returns the same structure with email fields added.
    
    **Scenario 2: Direct Username Email Lookup (TESTING/UTILITY ONLY)**
    
    **CRITICAL**: When user provides a list of GitHub usernames (e.g., "Find email addresses for these GitHub users: Rowens72, Mithonmasud..."), 
    you MUST use `find_emails_by_github_usernames_tool` DIRECTLY - DO NOT search for candidates first!
    
    Steps:
    1. Extract the GitHub usernames from the user's request (comma-separated list)
    2. Call `find_emails_by_github_usernames_tool` immediately with the usernames
       Example: `find_emails_by_github_usernames_tool("Rowens72, Mithonmasud, Marquish, Ekeneakubue")`
    3. Return ONLY the JSON response from the tool - it will include email fields for each candidate
    
    **DO NOT**:
    - Call `search_candidates_tool` first (this tool works independently)
    - Ask for job descriptions
    - Try to search the database first
    - Return multiple JSON responses - return ONLY the email lookup results
    
    **ONLY use `find_emails_by_github_usernames_tool` when:**
    - User explicitly lists GitHub usernames in their request
    - The request contains a comma-separated list of usernames
    - Example: "Find email addresses for these GitHub users: Rowens72, Mithonmasud, Marquish..."
    
    **Do NOT use `find_emails_by_github_usernames_tool` if:**
    - User just searched for candidates and wants emails (use Scenario 1 with `find_candidate_emails_tool`)
    - User says "get emails" or "find emails" without listing specific usernames (use Scenario 1)
    - You have candidate search results available (use Scenario 1)
    
    Both tools return JSON with these email fields:
    - `email`: The found email address (or null if not found)
    - `email_confidence`: Confidence score 0-100 (or null)
    - `email_source`: "github_profile" or "hunter_api" (or null)
    
    Return the updated JSON response with emails included. The frontend will automatically update the candidate cards.
    
    **For General Recruiting Questions (without tool):**
    
    Provide comprehensive guidance on:
    - Recruiting strategies and best practices
    - Compensation benchmarks for tech roles
    - Interview and assessment approaches
    - Pipeline optimization
    - Sourcing strategies
    
    Always be direct, actionable, and data-driven. Focus on helping recruiters find and evaluate top tech talent.
    """,
)

