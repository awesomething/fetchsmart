"""
Recruitment Backend MCP Server
Migrated from A2A to FastMCP for compatibility with MCPToolset

This server exposes recruitment tools via the Model Context Protocol (MCP).
Compatible with Google ADK's MCPToolset and standard MCP clients.
"""
import os
import sys
import logging
import json
from typing import List, Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from recruitment_service import recruitment_service
from candidate_matcher import CandidateMatcher
from github_scraper import GitHubProfileScraper

load_dotenv()
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%m/%d/%y %H:%M:%S'
)

# Initialize recruitment tools
matcher = CandidateMatcher()
github_token = os.getenv('GITHUB_TOKEN', '')
hunter_api_key = os.getenv('HUNTER_API_KEY', '')

# Initialize FastMCP server
# IMPORTANT: Use port 8200 to avoid conflict with staffing_backend (port 8100)
PORT = int(os.environ.get("PORT", 8200))
HOST = os.environ.get("HOST", "0.0.0.0")

# FastMCP automatically handles MCP protocol initialization
# The 'streamable-http' transport is compatible with ADK's MCPToolset
mcp = FastMCP("recruitment-agent", host=HOST, port=PORT)

logger.info("=" * 60)
logger.info("🚀 Recruitment Backend MCP Server Initializing...")
logger.info(f"📍 Server will start on: http://{HOST}:{PORT}")
logger.info(f"🔧 MCP Endpoint: http://{HOST}:{PORT}/mcp")
logger.info("=" * 60)

# ============================================================================
# MCP TOOLS for Recruitment Agents
# ============================================================================

@mcp.tool()
async def search_candidates_tool(
    job_description: str,
    job_title: str = "",
    limit: int = 8
) -> str:
    """
    Intelligent candidate search using AI-powered matching.

    Args:
        job_description: Natural language job description or requirements
        job_title: Optional job title for better matching
        limit: Number of top candidates to return (default: 8)

    Returns:
        JSON string with matched candidates, scores, and reasons
    """
    logger.info(f"[REQUEST] search_candidates_tool called: job_title={job_title}, limit={limit}")
    try:
        candidates = recruitment_service.candidates
        results = matcher.match_candidates(
            candidates=candidates,
            job_description=job_description,
            job_title=job_title,
            limit=limit
        )

        # Format for agent consumption
        response = {
            "query": job_description,
            "total_matches": results['total_matches'],
            "showing_top": results['showing'],
            "requirements_detected": results['requirements'],
            "top_candidates": []
        }

        for match in results['top_candidates']:
            candidate = match['candidate']
            likely_roles = candidate.get('likely_roles') or []
            role = likely_roles[0] if likely_roles else 'Software Engineer'
            candidate_id = candidate.get('id') or candidate.get('github_username') or 'unknown'

            # CRITICAL: Include email field from github_profiles_100.json if available
            # This allows find_candidate_emails_tool to preserve existing emails
            candidate_data = {
                "id": candidate_id,
                "name": candidate.get('name') or candidate.get('github_username', 'Unknown'),
                "github_username": candidate.get('github_username', ''),
                "github_profile_url": candidate.get('github_profile_url', ''),
                "role": role,
                "experience_level": candidate.get('estimated_experience_level', 'Mid'),
                "location": candidate.get('location', ''),
                "primary_language": candidate.get('primary_language', ''),
                "skills": candidate.get('skills', [])[:8],
                "github_stats": {
                    "repos": candidate.get('public_repos', 0),
                    "stars": candidate.get('total_stars', 0),
                    "followers": candidate.get('followers', 0),
                },
                "match_score": match.get('match_score', 0),
                "match_reasons": match.get('match_reasons', []),
                "matched_skills": match.get('matched_skills', []),
            }

            # Preserve email from github_profiles_100.json if available
            if candidate.get('email'):
                candidate_data['email'] = candidate.get('email')
                candidate_data['email_confidence'] = 100
                candidate_data['email_source'] = 'github_profile'

            response['top_candidates'].append(candidate_data)

        result = json.dumps(response, indent=2)
        logger.info(f"[SUCCESS] search_candidates_tool completed: {response.get('showing_top', 0)} candidates found")
        return result
    except Exception as e:
        logger.error(f"[ERROR] search_candidates_tool failed: {e}", exc_info=True)
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def scrape_github_profiles_tool(
    target_count: int = 20,
    tech_stack: str = ""
) -> str:
    """
    Scrape GitHub profiles for recruitment sourcing.

    Args:
        target_count: Number of profiles to scrape
        tech_stack: Optional tech stack to focus on (e.g., "python", "react", "golang")

    Returns:
        JSON string with scraped profiles and statistics
    """
    try:
        if not github_token:
            return json.dumps({
                "status": "error",
                "message": "GITHUB_TOKEN not configured. Please set environment variable."
            })

        scraper = GitHubProfileScraper(github_token)
        profiles = scraper.scrape_diverse_profiles(target_count=target_count)

        return json.dumps({
            "status": "success",
            "profiles_scraped": len(profiles),
            "profiles": profiles[:10],  # Return first 10 for preview
            "message": f"Successfully scraped {len(profiles)} GitHub profiles"
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in scrape_github_profiles_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def get_compensation_data_tool(role: str, location: str = "Remote") -> str:
    """
    Get compensation benchmarks for tech roles.

    Args:
        role: Job role (e.g., "Senior Software Engineer", "Staff Engineer")
        location: Location for geo-adjusted compensation

    Returns:
        JSON string with compensation data
    """
    try:
        return recruitment_service._get_compensation_data()
    except Exception as e:
        logger.error(f"Error in get_compensation_data_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def get_pipeline_metrics_tool() -> str:
    """
    Get recruitment pipeline metrics and analytics.

    Returns:
        JSON string with pipeline data
    """
    try:
        return recruitment_service._get_candidate_pipeline()
    except Exception as e:
        logger.error(f"Error in get_pipeline_metrics_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def analyze_portfolio_tool(github_username: str) -> str:
    """
    Analyze a candidate's GitHub portfolio.

    Args:
        github_username: GitHub username to analyze

    Returns:
        JSON string with portfolio analysis
    """
    try:
        # Find candidate in dataset (case-insensitive search)
        candidates = recruitment_service.candidates
        github_username_lower = github_username.lower()
        candidate = next(
            (c for c in candidates if c.get('github_username', '').lower() == github_username_lower),
            None
        )

        if not candidate:
            # Return list of available usernames for debugging
            available_usernames = [c.get('github_username', 'N/A') for c in candidates[:10]]
            return json.dumps({
                "status": "not_found",
                "message": f"Candidate {github_username} not found in database",
                "available_samples": available_usernames,
                "total_candidates": len(candidates)
            }, indent=2)

        # Analyze portfolio
        analysis = {
            "github_username": github_username,
            "name": candidate.get('name'),
            "primary_language": candidate.get('primary_language'),
            "languages": candidate.get('languages', []),
            "skills": candidate.get('skills', []),
            "github_stats": {
                "repos": candidate.get('public_repos'),
                "stars": candidate.get('total_stars'),
                "followers": candidate.get('followers'),
            },
            "notable_repos": candidate.get('notable_repos', [])[:5],
            "experience_level": candidate.get('estimated_experience_level'),
            "open_source_contributor": candidate.get('open_source_contributor'),
            "tech_stack_summary": candidate.get('tech_stack_summary', ''),
            "assessment": {
                "code_quality": "Strong" if candidate.get('total_stars', 0) > 200 else "Good",
                "activity_level": "High" if candidate.get('public_repos', 0) > 30 else "Moderate",
                "community_engagement": "Active" if candidate.get('open_source_contributor') else "Limited"
            }
        }

        return json.dumps(analysis, indent=2)
    except Exception as e:
        logger.error(f"Error in analyze_portfolio_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def get_time_tracking_tool(recruiter_id: str = "REC-001") -> str:
    """
    Get recruiter productivity and time tracking data.

    Args:
        recruiter_id: Recruiter ID to analyze

    Returns:
        JSON string with time tracking data
    """
    try:
        return recruitment_service._get_time_tracking_data()
    except Exception as e:
        logger.error(f"Error in get_time_tracking_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def generate_recruitment_report_tool(
    candidates: List[Dict],
    job_title: str,
    format: str = "json"
) -> str:
    """
    Generate a recruitment report with candidate recommendations.

    Args:
        candidates: List of candidate dictionaries
        job_title: Job title for the role
        format: Output format ("json", "html", "pdf")

    Returns:
        JSON string with report data or file path
    """
    try:
        report = {
            "report_id": f"REPORT-{hash(job_title) % 10000:04d}",
            "job_title": job_title,
            "generated_at": str(json.dumps({"iso": "2024-01-15T10:30:00Z"})),
            "summary": {
                "total_candidates": len(candidates),
                "recommended_count": len([c for c in candidates if c.get('match_score', 0) > 70]),
                "avg_match_score": sum(c.get('match_score', 0) for c in candidates) / len(candidates) if candidates else 0
            },
            "candidates": candidates,
            "recommendations": [
                "Schedule technical interviews with top 3 candidates",
                "Prioritize candidates with open-source contributions",
                "Consider remote candidates to expand talent pool"
            ]
        }

        return json.dumps(report, indent=2)
    except Exception as e:
        logger.error(f"Error in generate_recruitment_report_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def send_recruitment_email_tool(
    recruiter_email: str,
    report_data: str,
    subject: str = "Candidate Recommendations Report"
) -> str:
    """
    Send recruitment report via email to recruiter.

    Args:
        recruiter_email: Email address of recruiter
        report_data: JSON report data to send
        subject: Email subject line

    Returns:
        JSON string with email status
    """
    try:
        # Placeholder for actual email sending
        # In production, integrate with email service (SendGrid, Gmail API, etc.)
        result = {
            "status": "success",
            "message": f"Report sent to {recruiter_email}",
            "subject": subject,
            "timestamp": "2024-01-15T10:30:00Z",
            "note": "Email simulation - integrate with actual email service in production"
        }

        logger.info(f"Would send recruitment report to {recruiter_email}")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in send_recruitment_email_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def find_emails_by_github_usernames_tool(github_usernames: str) -> str:
    """
    Find email addresses for GitHub usernames from database or Hunter API.
    Priority: DEFAULT_PROFILE_OVERRIDES > github_profiles_100.json > Hunter API

    Args:
        github_usernames: Comma-separated list of GitHub usernames

    Returns:
        JSON string with candidates and their email addresses
    """
    try:
        import requests

        usernames = [u.strip() for u in github_usernames.split(',') if u.strip()]
        if not usernames:
            return json.dumps({
                "status": "error",
                "message": "No GitHub usernames provided",
                "top_candidates": []
            })

        # Default profile overrides (for testing - moved from adk_agent.py)
        DEFAULT_PROFILE_OVERRIDES = {
            "awesomething": {"id": "CAND-001", "name": "awesomething", "github_username": "awesomething", "email": "awesomething@github.com"},
            "mithonmasud": {"id": "CAND-002", "name": "Mithonmasud", "github_username": "Mithonmasud", "email": "mithonmasud@github.com"},
            "marquish": {"id": "CAND-003", "name": "Marquish", "github_username": "Marquish", "email": "marquish@github.com"},
            "ekeneakubue": {"id": "CAND-004", "name": "Ekeneakubue", "github_username": "Ekeneakubue", "email": "ekeneakubue@github.com"},
            "sarahchen": {"id": "CAND-005", "name": "Sarah Chen", "github_username": "sarahchen", "email": "sarahchen@github.com"},
            "olafaloofian": {"id": "CAND-006", "name": "Michael Kerr", "github_username": "Olafaloofian", "email": "olafaloofian@github.com"},
            "xiiiiiiiiii": {"id": "CAND-007", "name": "xiiiiiiiiii", "github_username": "xiiiiiiiiii", "email": "xiiiiiiiiii@github.com"},
            "rowens72": {"id": "CAND-008", "name": "Rowens72", "github_username": "Rowens72", "email": "rowens72@github.com"},
        }

        results = []
        for username in usernames:
            username_lower = username.lower()

            # Check default profiles first
            if username_lower in DEFAULT_PROFILE_OVERRIDES:
                profile = DEFAULT_PROFILE_OVERRIDES[username_lower]
                candidate = {
                    "id": profile.get("id", username),
                    "name": profile.get("name", username),
                    "github_username": profile.get("github_username", username),
                    "github_profile_url": f"https://github.com/{username}",
                    "email": profile.get("email"),
                    "email_confidence": 100,
                    "email_source": "recruitment_database"
                }
                results.append(candidate)
                continue

            # Check recruitment service database
            candidates = recruitment_service.candidates
            dataset_cand = next(
                (c for c in candidates if c.get('github_username', '').lower() == username_lower),
                None
            )

            if dataset_cand and dataset_cand.get('email'):
                candidate = {
                    "id": dataset_cand.get('id', username),
                    "name": dataset_cand.get('name', username),
                    "github_username": dataset_cand.get('github_username', username),
                    "github_profile_url": dataset_cand.get('github_profile_url', f"https://github.com/{username}"),
                    "email": dataset_cand.get('email'),
                    "email_confidence": 100,
                    "email_source": "recruitment_database"
                }
                results.append(candidate)
                continue

            # Fallback to Hunter API (if configured)
            if not hunter_api_key:
                # No Hunter API key - return candidate without email
                logger.warning(f"No email found for {username} and HUNTER_API_KEY not configured")
                candidate = {
                    "id": username,
                    "name": username,
                    "github_username": username,
                    "github_profile_url": f"https://github.com/{username}",
                    "email": None,
                    "email_confidence": None,
                    "email_source": None
                }
                results.append(candidate)
                continue

            parts = username.split()
            first_name = parts[0] if parts else username
            last_name = " ".join(parts[1:]) if len(parts) > 1 else None

            try:
                params = {"api_key": hunter_api_key, "first_name": first_name}
                if last_name:
                    params["last_name"] = last_name

                resp = requests.get("https://api.hunter.io/v2/email-finder", params=params, timeout=10)
                if resp.status_code == 200:
                    payload = resp.json() or {}
                    data = payload.get("data") or {}
                    email = data.get("email")
                    score = data.get("score")

                    candidate = {
                        "id": username,
                        "name": username,
                        "github_username": username,
                        "github_profile_url": f"https://github.com/{username}",
                        "email": email,
                        "email_confidence": score,
                        "email_source": "hunter_api" if email else None
                    }
                else:
                    candidate = {
                        "id": username,
                        "name": username,
                        "github_username": username,
                        "github_profile_url": f"https://github.com/{username}",
                        "email": None,
                        "email_confidence": None,
                        "email_source": None
                    }
            except Exception as e:
                logger.warning(f"Hunter API error for {username}: {e}")
                candidate = {
                    "id": username,
                    "name": username,
                    "github_username": username,
                    "github_profile_url": f"https://github.com/{username}",
                    "email": None,
                    "email_confidence": None,
                    "email_source": None
                }

            results.append(candidate)

        response = {
            "query": f"Email lookup for GitHub users: {github_usernames}",
            "total_matches": len(results),
            "showing_top": len(results),
            "top_candidates": results
        }
        return json.dumps(response, indent=2)
    except Exception as e:
        logger.error(f"Error in find_emails_by_github_usernames_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@mcp.tool()
async def find_candidate_emails_tool(candidates_json: str) -> str:
    """
    Find email addresses for candidates from database or Hunter API.
    Priority: Existing email > DEFAULT_PROFILE_OVERRIDES > github_profiles_100.json > Hunter API

    Args:
        candidates_json: JSON string with candidate data (from search_candidates_tool)

    Returns:
        JSON string with updated candidate data including emails
    """
    try:
        import requests

        logger.info(f"[find_candidate_emails_tool] Received request with {len(candidates_json)} characters")
        
        # Parse input JSON
        data = json.loads(candidates_json)
        is_nested = isinstance(data, dict) and "top_candidates" in data
        candidates = data.get("top_candidates", []) if is_nested else data

        if not isinstance(candidates, list):
            logger.error(f"[find_candidate_emails_tool] Invalid format: candidates is not a list")
            return json.dumps({"status": "error", "message": "Invalid candidates format"})
        
        logger.info(f"[find_candidate_emails_tool] Processing {len(candidates)} candidates")
        logger.info(f"[find_candidate_emails_tool] HUNTER_API_KEY configured: {bool(hunter_api_key)}")

        # Default profile overrides (for testing)
        DEFAULT_PROFILE_OVERRIDES = {
            "awesomething": {"email": "awesomething@github.com"},
            "mithonmasud": {"email": "mithonmasud@github.com"},
            "marquish": {"email": "marquish@github.com"},
            "ekeneakubue": {"email": "ekeneakubue@github.com"},
            "sarahchen": {"email": "sarahchen@github.com"},
            "olafaloofian": {"email": "olafaloofian@github.com"},
            "xiiiiiiiiii": {"email": "xiiiiiiiiii@github.com"},
            "rowens72": {"email": "rowens72@github.com"},
        }

        # Load github_profiles_100.json data (contains 100 real GitHub profiles with emails)
        github_profiles = recruitment_service.candidates
        logger.info(f"[find_candidate_emails_tool] Loaded {len(github_profiles)} profiles from github_profiles_100.json")

        updated = []
        emails_found = 0
        emails_from_database = 0
        emails_from_github_json = 0
        emails_from_hunter = 0
        
        for cand in candidates:
            cand = dict(cand)  # shallow copy
            username = cand.get('github_username', 'unknown')
            username_lower = username.lower()

            # Skip if already has email
            if cand.get('email'):
                emails_found += 1
                logger.info(f"[find_candidate_emails_tool] Candidate {username} already has email: {cand.get('email')}")
                updated.append(cand)
                continue

            # PRIORITY 1: Check DEFAULT_PROFILE_OVERRIDES (hardcoded test data)
            if username_lower in DEFAULT_PROFILE_OVERRIDES:
                cand['email'] = DEFAULT_PROFILE_OVERRIDES[username_lower]['email']
                cand['email_confidence'] = 100
                cand['email_source'] = 'recruitment_database'
                emails_found += 1
                emails_from_database += 1
                logger.info(f"[find_candidate_emails_tool] Found email for {username} from database override")
                updated.append(cand)
                continue

            # PRIORITY 2: Check github_profiles_100.json (100 real GitHub profiles)
            dataset_cand = next(
                (c for c in github_profiles if c.get('github_username', '').lower() == username_lower),
                None
            )
            if dataset_cand and dataset_cand.get('email'):
                cand['email'] = dataset_cand.get('email')
                cand['email_confidence'] = 100
                cand['email_source'] = 'github_profiles_100_json'
                emails_found += 1
                emails_from_github_json += 1
                logger.info(f"[find_candidate_emails_tool] Found email for {username} from github_profiles_100.json: {cand['email']}")
                updated.append(cand)
                continue

            # PRIORITY 3: Use Hunter API (if configured)
            if not hunter_api_key:
                # No Hunter API key - keep candidate without email
                logger.warning(f"[find_candidate_emails_tool] No email found for {username} in database/JSON and HUNTER_API_KEY not configured")
                cand.setdefault('email', None)
                cand.setdefault('email_confidence', None)
                cand.setdefault('email_source', None)
                updated.append(cand)
                continue

            full_name = cand.get('name', '')
            parts = full_name.split()
            first_name = parts[0] if parts else ''
            last_name = " ".join(parts[1:]) if len(parts) > 1 else None

            if not first_name:
                cand['email'] = None
                cand['email_confidence'] = None
                cand['email_source'] = None
                updated.append(cand)
                continue

            try:
                params = {"api_key": hunter_api_key, "first_name": first_name}
                if last_name:
                    params["last_name"] = last_name

                logger.info(f"[find_candidate_emails_tool] Calling Hunter API for {username} (name: {first_name} {last_name or ''})")
                resp = requests.get("https://api.hunter.io/v2/email-finder", params=params, timeout=10)
                if resp.status_code == 200:
                    payload = resp.json() or {}
                    data_inner = payload.get("data") or {}
                    email = data_inner.get("email")
                    score = data_inner.get("score")

                    cand['email'] = email
                    cand['email_confidence'] = score
                    cand['email_source'] = 'hunter_api' if email else None
                    
                    if email:
                        emails_found += 1
                        emails_from_hunter += 1
                        logger.info(f"[find_candidate_emails_tool] Found email for {username} from Hunter API: {email} (score: {score})")
                    else:
                        logger.warning(f"[find_candidate_emails_tool] Hunter API returned no email for {username}")
                else:
                    logger.warning(f"[find_candidate_emails_tool] Hunter API returned status {resp.status_code} for {username}")
                    cand['email'] = None
                    cand['email_confidence'] = None
                    cand['email_source'] = None
            except Exception as e:
                logger.warning(f"[find_candidate_emails_tool] Hunter API error for {username}: {e}")
                cand['email'] = None
                cand['email_confidence'] = None
                cand['email_source'] = None

            updated.append(cand)
        
        logger.info(f"[find_candidate_emails_tool] Summary: Found {emails_found} emails total ({emails_from_database} from overrides, {emails_from_github_json} from github_profiles_100.json, {emails_from_hunter} from Hunter API) out of {len(candidates)} candidates")

        # Return in original format
        if is_nested:
            data['top_candidates'] = updated
            result = json.dumps(data, indent=2)
        else:
            result = json.dumps(updated, indent=2)
        
        logger.info(f"[find_candidate_emails_tool] Returning result with {len(updated)} candidates")
        return result
    except Exception as e:
        logger.error(f"[find_candidate_emails_tool] Error: {e}", exc_info=True)
        return json.dumps({"error": str(e), "status": "failed"})


# ============================================================================
# Server Startup
# ============================================================================

def main():
    """Start the FastMCP server."""
    try:
        logger.info("=" * 60)
        logger.info("🚀 Recruitment Backend MCP Server Starting...")
        logger.info("=" * 60)
        logger.info(f"📍 Server: http://{HOST}:{PORT}")
        logger.info(f"🔧 Transport: streamable-http")
        logger.info(f"📦 Tools Registered:")
        logger.info("   - search_candidates_tool")
        logger.info("   - scrape_github_profiles_tool")
        logger.info("   - get_compensation_data_tool")
        logger.info("   - get_pipeline_metrics_tool")
        logger.info("   - analyze_portfolio_tool")
        logger.info("   - get_time_tracking_tool")
        logger.info("   - generate_recruitment_report_tool")
        logger.info("   - send_recruitment_email_tool")
        logger.info("   - find_emails_by_github_usernames_tool")
        logger.info("   - find_candidate_emails_tool")
        logger.info(f"💡 Test with: npx @modelcontextprotocol/inspector python server.py")
        logger.info("=" * 60)
        logger.info(f"[INFO] MCP endpoint will be available at: http://{HOST}:{PORT}/mcp")
        logger.info(f"[INFO] ADK agents should connect to: http://{HOST}:{PORT}/mcp")
        logger.info("=" * 60)
        logger.info(f"[INFO] Environment: PORT={PORT}, HOST={HOST}")
        logger.info(f"[INFO] Cloud Run will map this to the service URL")
        logger.info("=" * 60)

        # Start FastMCP server
        logger.info(f"[INFO] Starting FastMCP server on port {PORT}...")
        mcp.run(transport='streamable-http')

    except KeyboardInterrupt:
        logger.info("\n[INFO] Server stopped by user")
    except Exception as e:
        logger.error(f"\n[ERROR] Server crashed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
