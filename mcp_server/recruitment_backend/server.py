import os
import sys
import logging
from typing import Any, AsyncIterator, List, Dict
import uvicorn
import json
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from a2a.server.apps import A2AStarletteApplication
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from recruitment_service import recruitment_service
from candidate_matcher import CandidateMatcher
from github_scraper import GitHubProfileScraper

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize recruitment tools
matcher = CandidateMatcher()
github_token = os.getenv('GITHUB_TOKEN', '')
hunter_api_key = os.getenv('HUNTER_API_KEY', '')

# ============================================================================
# MCP TOOLS for Recruitment Agents
# ============================================================================

def search_candidates_tool(
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
            # Safely get role
            likely_roles = candidate.get('likely_roles') or []
            role = likely_roles[0] if likely_roles else 'Software Engineer'
            
            # Safely get id
            candidate_id = candidate.get('id') or candidate.get('github_username') or 'unknown'
            
            response['top_candidates'].append({
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
            })
        
        return json.dumps(response, indent=2)
    except Exception as e:
        logger.error(f"Error in search_candidates_tool: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


def scrape_github_profiles_tool(
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


def get_compensation_data_tool(role: str, location: str = "Remote") -> str:
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


def get_pipeline_metrics_tool() -> str:
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


def analyze_portfolio_tool(github_username: str) -> str:
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


def get_time_tracking_tool(recruiter_id: str = "REC-001") -> str:
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


def generate_recruitment_report_tool(
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


def send_recruitment_email_tool(
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


def find_emails_by_github_usernames_tool(github_usernames: str) -> str:
    """
    Find email addresses for GitHub usernames directly using Hunter API.
    This is a simplified tool for testing/default candidates.
    
    Args:
        github_usernames: Comma-separated list of GitHub usernames (e.g., "Rowens72, Mithonmasud, Marquish")
    
    Returns:
        JSON string with candidates including email and email_confidence fields
    """
    import requests
    import time
    import re
    
    try:
        # Re-read API key in case environment wasn't loaded at import time
        api_key = os.getenv('HUNTER_API_KEY', '') or hunter_api_key
        if not api_key:
            logger.error("HUNTER_API_KEY not found in environment or module variable")
            return json.dumps({
                "status": "error",
                "message": "HUNTER_API_KEY not configured. Please set HUNTER_API_KEY environment variable to use email lookup.",
                "top_candidates": []
            })
        logger.info(f"Using Hunter API for email lookup (key length: {len(api_key)})")
        
        # Parse usernames
        usernames = [u.strip() for u in github_usernames.split(',') if u.strip()]
        
        if not usernames:
            return json.dumps({
                "status": "error",
                "message": "No GitHub usernames provided",
                "candidates": []
            })
        
        results = {
            "query": f"Email lookup for GitHub users: {github_usernames}",
            "total_matches": len(usernames),
            "showing_top": len(usernames),
            "top_candidates": []
        }
        
        hunter_api_url = "https://api.hunter.io/v2/email-finder"
        
        for username in usernames:
            email = None
            email_confidence = None
            email_source = None
            candidate_name = username  # Default to username if name not found
            
            # Step 1: Check if candidate exists in database (if available)
            try:
                if recruitment_service and hasattr(recruitment_service, 'candidates'):
                    candidates_db = recruitment_service.candidates
                    username_lower = username.lower()
                    db_candidate = next(
                        (c for c in candidates_db if c.get('github_username', '').lower() == username_lower),
                        None
                    )
                    if db_candidate:
                        candidate_name = db_candidate.get('name') or username
                        if db_candidate.get('email'):
                            email = db_candidate.get('email')
                            email_confidence = 100
                            email_source = "github_profile"
            except Exception as e:
                logger.debug(f"Error checking database for {username}: {e}")
                # Continue to Hunter API if database check fails
            
            # Step 2: If not found, try Hunter API
            if not email and api_key:
                try:
                    # Try to get name from database or use username
                    name_parts = candidate_name.split()
                    first_name = name_parts[0] if name_parts else username
                    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                    
                    # Call Hunter API
                    params = {
                        'api_key': api_key,
                        'first_name': first_name,
                    }
                    if last_name:
                        params['last_name'] = last_name
                    
                    response = requests.get(hunter_api_url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        hunter_data = response.json()
                        if hunter_data.get('data') and hunter_data['data'].get('email'):
                            email = hunter_data['data']['email']
                            email_confidence = hunter_data['data'].get('score', 0)
                            email_source = "hunter_api"
                    elif response.status_code == 429:
                        logger.warning(f"Hunter API rate limit reached for {username}")
                    else:
                        logger.debug(f"Hunter API error for {username}: {response.status_code}")
                    
                    # Be respectful of rate limits
                    time.sleep(0.5)
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error calling Hunter API for {username}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error in email lookup for {username}: {e}")
            
            # Build candidate object
            candidate = {
                "id": username,
                "name": candidate_name,
                "github_username": username,
                "github_profile_url": f"https://github.com/{username}",
                "role": "Software Engineer",  # Default
                "experience_level": "Mid",  # Default
                "location": "",
                "primary_language": "",
                "skills": [],
                "github_stats": {
                    "repos": 0,
                    "stars": 0,
                    "followers": 0,
                },
                "match_score": 0,
                "email": email,
                "email_confidence": email_confidence,
                "email_source": email_source,
            }
            
            results["top_candidates"].append(candidate)
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        logger.error(f"Error in find_emails_by_github_usernames_tool: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e),
            "candidates": []
        })


def find_candidate_emails_tool(candidates_json: str) -> str:
    """
    Find email addresses for candidates using GitHub profiles and Hunter API.
    
    Args:
        candidates_json: JSON string containing list of candidate objects with:
            - id, name, github_username, location (optional)
    
    Returns:
        JSON string with updated candidates including email and email_confidence fields
    """
    import requests
    import time
    import re
    
    try:
        # Re-read API key in case environment wasn't loaded at import time
        api_key = os.getenv('HUNTER_API_KEY', '') or hunter_api_key
        if not api_key:
            logger.error("HUNTER_API_KEY not found in environment or module variable")
            return json.dumps({
                "status": "error",
                "message": "HUNTER_API_KEY not configured. Please set HUNTER_API_KEY environment variable.",
                "candidates": json.loads(candidates_json) if isinstance(candidates_json, str) else candidates_json
            })
        logger.info(f"Using Hunter API for email lookup (key length: {len(api_key)})")
        
        # Parse candidates
        if isinstance(candidates_json, str):
            candidates_data = json.loads(candidates_json)
        else:
            candidates_data = candidates_json
        
        # Handle both direct candidate list and nested structure
        if isinstance(candidates_data, dict) and 'top_candidates' in candidates_data:
            candidates_list = candidates_data['top_candidates']
            is_nested = True
        elif isinstance(candidates_data, list):
            candidates_list = candidates_data
            is_nested = False
        else:
            return json.dumps({
                "status": "error",
                "message": "Invalid candidates format. Expected list or dict with 'top_candidates' key."
            })
        
        updated_candidates = []
        hunter_api_url = "https://api.hunter.io/v2/email-finder"
        
        for candidate in candidates_list:
            email = None
            email_confidence = None
            email_source = None
            
            # Step 1: Check if email exists in GitHub profile data
            # Check recruitment_service candidates for email
            github_username = candidate.get('github_username', '')
            if github_username:
                try:
                    candidates_db = recruitment_service.candidates
                    github_username_lower = github_username.lower()
                    db_candidate = next(
                        (c for c in candidates_db if c.get('github_username', '').lower() == github_username_lower),
                        None
                    )
                    if db_candidate and db_candidate.get('email'):
                        email = db_candidate.get('email')
                        email_confidence = 100
                        email_source = "github_profile"
                except Exception as e:
                    logger.debug(f"Error checking GitHub profile for {github_username}: {e}")
            
            # Step 2: If not found, try Hunter API
            if not email and api_key:
                try:
                    # Extract name components
                    full_name = candidate.get('name', '').strip()
                    if not full_name:
                        full_name = candidate.get('github_username', '')
                    
                    # Split name into first and last
                    name_parts = full_name.split()
                    first_name = name_parts[0] if name_parts else ''
                    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                    
                    # Try to infer domain from location or use common providers
                    location = candidate.get('location', '')
                    domain = None
                    
                    # Try to extract domain from location (e.g., "San Francisco, CA" -> None, but "company.com" -> domain)
                    if location:
                        # Check if location contains a domain-like string
                        domain_match = re.search(r'([a-zA-Z0-9-]+\.(com|org|net|io|co|dev))', location, re.IGNORECASE)
                        if domain_match:
                            domain = domain_match.group(1)
                    
                    # If no domain found, try to infer from GitHub username or use common providers
                    if not domain:
                        # Common email providers as fallback
                        common_domains = ['gmail.com', 'outlook.com', 'yahoo.com']
                        # For now, we'll try without domain (Hunter can work with just name)
                        domain = None
                    
                    # Call Hunter API
                    if first_name:
                        params = {
                            'api_key': api_key,
                            'first_name': first_name,
                        }
                        if last_name:
                            params['last_name'] = last_name
                        if domain:
                            params['domain'] = domain
                        
                        response = requests.get(hunter_api_url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            hunter_data = response.json()
                            if hunter_data.get('data') and hunter_data['data'].get('email'):
                                email = hunter_data['data']['email']
                                email_confidence = hunter_data['data'].get('score', 0)
                                email_source = "hunter_api"
                        elif response.status_code == 429:
                            # Rate limit - skip this candidate
                            logger.warning(f"Hunter API rate limit reached for {github_username}")
                        else:
                            logger.debug(f"Hunter API error for {github_username}: {response.status_code}")
                        
                        # Be respectful of rate limits - add small delay
                        time.sleep(0.5)
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error calling Hunter API for {github_username}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error in email lookup for {github_username}: {e}")
            
            # Update candidate with email data
            updated_candidate = candidate.copy()
            if email:
                updated_candidate['email'] = email
                updated_candidate['email_confidence'] = email_confidence
                updated_candidate['email_source'] = email_source
            else:
                updated_candidate['email'] = None
                updated_candidate['email_confidence'] = None
                updated_candidate['email_source'] = None
            
            updated_candidates.append(updated_candidate)
        
        # Return in same format as input
        if is_nested:
            result = candidates_data.copy()
            result['top_candidates'] = updated_candidates
        else:
            result = updated_candidates
        
        return json.dumps(result, indent=2)
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing candidates JSON: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Invalid JSON format: {str(e)}"
        })
    except Exception as e:
        logger.error(f"Error in find_candidate_emails_tool: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e),
            "candidates": json.loads(candidates_json) if isinstance(candidates_json, str) else candidates_json
        })


# ============================================================================
# Create ADK Agent with All Tools
# ============================================================================

# Create the recruitment agent
def create_recruitment_agent() -> LlmAgent:
    """Creates an LLM agent that handles recruitment queries with all MCP tools"""
    
    def recruitment_tool(query: str) -> str:
        """Tool that queries the recruitment system"""
        return recruitment_service.handle_query(query)
    
    return LlmAgent(
        model="gemini-2.0-flash-exp",
        name="recruitment_data_agent",
        description="Provides recruitment data including candidates, jobs, compensation, and market insights",
        instruction="""
        You are a recruitment data assistant for tech recruiting with access to powerful MCP tools.
        
        **Available Tools:**
        - recruitment_tool: General recruitment queries
        - search_candidates_tool: Intelligent AI-powered candidate search with matching
        - scrape_github_profiles_tool: Scrape new GitHub profiles for sourcing
        - get_compensation_data_tool: Salary benchmarks and compensation data
        - get_pipeline_metrics_tool: Recruitment pipeline analytics
        - analyze_portfolio_tool: Deep GitHub portfolio analysis
        - get_time_tracking_tool: Recruiter productivity and time tracking
        - generate_recruitment_report_tool: Generate candidate reports
        - send_recruitment_email_tool: Email reports to recruiters
        - find_candidate_emails_tool: Find email addresses for candidates using GitHub profiles and Hunter API
        - find_emails_by_github_usernames_tool: Direct email lookup for GitHub usernames (comma-separated list)
        
        **When to Use Each Tool:**
        - For candidate search: Use search_candidates_tool with job description
        - For new sourcing: Use scrape_github_profiles_tool
        - For salary questions: Use get_compensation_data_tool
        - For pipeline data: Use get_pipeline_metrics_tool
        - For portfolio review: Use analyze_portfolio_tool with GitHub username
        - For productivity: Use get_time_tracking_tool
        - For reporting: Use generate_recruitment_report_tool and send_recruitment_email_tool
        
        Always provide clear, structured responses focused on tech talent acquisition.
        Include specific metrics, match scores, and actionable insights.
        """,
        tools=[
            recruitment_tool,
            search_candidates_tool,
            scrape_github_profiles_tool,
            get_compensation_data_tool,
            get_pipeline_metrics_tool,
            analyze_portfolio_tool,
            get_time_tracking_tool,
            generate_recruitment_report_tool,
            send_recruitment_email_tool,
            find_candidate_emails_tool,
            find_emails_by_github_usernames_tool,
        ],
    )

def main():
    """Start the recruitment backend A2A server"""
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8100))
    
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Define agent capabilities
        capabilities = AgentCapabilities(streaming=True)
        
        # Define skills the agent provides (Tech Recruiting Focus)
        skills = [
            AgentSkill(
                id="candidate_sourcing",
                name="Tech Candidate Sourcing (GitHub)",
                description="Analyzes tech candidate pipelines, GitHub profiles, open-source contributions, and sourcing channel effectiveness",
                tags=["sourcing", "pipeline", "github", "tech-talent", "open-source"],
                examples=["Find senior engineers on GitHub", "Show me GitHub sourcing metrics", "Which channel brings best tech talent?"]
            ),
            AgentSkill(
                id="compensation",
                name="Tech Compensation Benchmarking",
                description="Provides salary benchmarks for engineering roles, equity packages, and competitive offer recommendations",
                tags=["compensation", "salary", "equity", "tech-offers"],
                examples=["What's the market rate for a Staff Engineer?", "Compare equity packages for ML roles"]
            ),
            AgentSkill(
                id="candidate_review",
                name="Technical Candidate Portfolio Review",
                description="Reviews GitHub repositories, coding assessments, technical skills, and open-source contributions",
                tags=["candidates", "screening", "github", "coding", "tech-skills"],
                examples=["Analyze this candidate's GitHub profile", "Show top candidates for backend role"]
            ),
            AgentSkill(
                id="hiring_goals",
                name="Tech Hiring Goals Tracking",
                description="Tracks engineering hiring targets, technical pipeline health, and recruitment OKRs",
                tags=["goals", "targets", "metrics", "tech-hiring"],
                examples=["How are we tracking against engineering hiring goals?", "Show me technical pipeline bottlenecks"]
            ),
            AgentSkill(
                id="time_tracking",
                name="Recruiter Time Tracking & Productivity",
                description="Tracks recruiter time allocation across activities, identifies productivity bottlenecks, and provides optimization recommendations",
                tags=["productivity", "time-tracking", "analytics", "efficiency"],
                examples=["Show my time breakdown this week", "Where am I spending too much time?", "Compare my productivity to team average"]
            ),
            AgentSkill(
                id="market_insights",
                name="Tech Talent Market Intelligence",
                description="Provides tech talent market trends, competitive intelligence, and strategic recruitment recommendations",
                tags=["market", "trends", "intelligence", "tech-talent"],
                examples=["What are current tech hiring trends?", "Show me salary trends for ML engineers"]
            ),
        ]
        
        # Create agent card
        agent_card = AgentCard(
            name="Recruitment Data Agent",
            description="Provides comprehensive recruitment data and insights for talent acquisition teams",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=["text/plain"],
            defaultOutputModes=["text/plain"],
            capabilities=capabilities,
            skills=skills,
        )
        
        # Create ADK agent
        adk_agent = create_recruitment_agent()
        runner = Runner(
            app_name=agent_card.name,
            agent=adk_agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        
        # Create A2A server
        request_handler = DefaultRequestHandler(
            agent_executor=runner,
            task_store=InMemoryTaskStore(),
        )
        
        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )
        
        print(f"\n🚀 Recruitment Backend Server Starting...")
        print(f"📍 URL: http://{host}:{port}")
        print(f"🎴 Agent Card: http://{host}:{port}/.well-known/agent-card.json")
        print(f"✅ Ready to serve recruitment data!")
        print(f"💼 Focus: GitHub-based tech talent sourcing\n")
        
        # Start server
        uvicorn.run(server.build(), host=host, port=port)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

