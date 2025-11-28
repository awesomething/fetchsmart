"""
MCP Staffing Agent Server
Main server file that registers all staffing MCP tools.
"""
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from job_search_tool import JobSearchTool
from candidate_submission_tool import CandidateSubmissionTool
from hiring_pipeline_tool import HiringPipelineTool
import json

# Load environment variables
# Try loading from both current directory and parent directory
load_dotenv()  # Current directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))  # Explicit path
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))  # Parent directory

# Initialize FastMCP server
PORT = int(os.environ.get("PORT", 8100))
# FastMCP automatically handles MCP protocol initialization
# The 'streamable-http' transport is compatible with ADK's MCPToolset
mcp = FastMCP("staffing-agent", host="0.0.0.0", port=PORT)

# Initialize tools with error handling
try:
    job_search_tool = JobSearchTool()
    print("[OK] JobSearchTool initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize JobSearchTool: {e}")
    import traceback
    traceback.print_exc()
    job_search_tool = None

try:
    candidate_submission_tool = CandidateSubmissionTool()
    print("[OK] CandidateSubmissionTool initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize CandidateSubmissionTool: {e}")
    import traceback
    traceback.print_exc()
    candidate_submission_tool = None

try:
    hiring_pipeline_tool = HiringPipelineTool()
    print("[OK] HiringPipelineTool initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize HiringPipelineTool: {e}")
    import traceback
    traceback.print_exc()
    hiring_pipeline_tool = None

if job_search_tool and candidate_submission_tool and hiring_pipeline_tool:
    print("[OK] All staffing MCP tools initialized successfully.")
else:
    print("[WARNING] Some tools failed to initialize. MCP server will continue but some tools may not work.")

# ============================================================================
# MCP Tool Registrations
# ============================================================================

@mcp.tool()
async def search_jobs(
    job_title: str = None,
    location: str = "",
    min_salary: float = None,
    max_salary: float = None,
    remote_only: bool = False,
    limit: int = 10
) -> str:
    """
    Search job openings from Supabase with JSearch API fallback.
    
    Args:
        job_title: Search term in job title (partial match)
        location: Job location (partial match). Use empty string for no location filter, or set remote_only=True for remote jobs
        min_salary: Minimum salary filter (numeric). Jobs with max_salary < min_salary are excluded.
        max_salary: Maximum salary filter (numeric). Jobs with min_salary > max_salary are excluded.
        remote_only: If True, only return jobs where job_location IS NULL (overrides location parameter)
        limit: Max number of results
    
    Returns:
        JSON string with matching job openings
    """
    try:
        if job_search_tool is None:
            error_response = {
                "status": "error",
                "message": "JobSearchTool not initialized. Check server logs.",
                "total_jobs": 0,
                "jobs": [],
                "error_type": "InitializationError"
            }
            return json.dumps(error_response)
        
        result = job_search_tool.search_jobs(
            job_title=job_title,
            location=location,
            min_salary=min_salary,
            max_salary=max_salary,
            remote_only=remote_only,
            limit=limit
        )
        return result
    except Exception as e:
        # Always return a valid JSON string, even on error
        error_response = {
            "status": "error",
            "message": f"Job search failed: {str(e)}",
            "total_jobs": 0,
            "jobs": [],
            "error_type": type(e).__name__
        }
        return json.dumps(error_response)

@mcp.tool()
async def create_candidate_submission(
    candidate_name: str,
    candidate_email: str,
    job_description_summary: str = None,
    job_opening_id: int = None,
    candidate_github: str = None,
    candidate_linkedin: str = None,
    recruiter_id: str = None,
    match_score: float = 0.0,
    notes: str = ""
) -> str:
    """
    Create a candidate submission for a job opening.
    
    **REQUIRED ARGUMENTS (only these are needed):**
    - candidate_name: Candidate's full name
    - candidate_email: Candidate's email address
    
    **OPTIONAL ARGUMENTS (do not request these from users):**
    - job_description_summary: Job description summary (max 1028 characters). If provided, will be stored in notes field.
    - job_opening_id: Optional integer ID of the job opening (not required - JD summary is sufficient)
    - candidate_github: GitHub profile URL (optional)
    - candidate_linkedin: LinkedIn profile URL (optional)
    - recruiter_id: UUID of the recruiter (optional, not required)
    - match_score: Automated match score (0.00-1.00, defaults to 0.0)
    - notes: Additional notes about the candidate (optional)
    
    **IMPORTANT:** Only candidate_name and candidate_email are required. 
    The job_description_summary should be provided if available (max 1028 characters).
    All other fields are optional and should NOT be requested from users.
    
    Returns:
        JSON string with submission details
    """
    try:
        if candidate_submission_tool is None:
            error_response = {
                "status": "error",
                "message": "CandidateSubmissionTool not initialized. Check server logs.",
                "error_type": "InitializationError"
            }
            return json.dumps(error_response)
        
        # Validate: Either job_opening_id OR job_description_summary should be provided
        # But this is optional - the tool can work with just name and email
        # However, if job_description_summary is provided, enforce character limit
        if job_description_summary and len(job_description_summary) > 1028:
            return json.dumps({
                "status": "error",
                "message": "Job description summary exceeds 1028 character limit.",
                "error_type": "ValidationError"
            })
        
        result = candidate_submission_tool.create_submission(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            job_opening_id=job_opening_id,
            job_description_summary=job_description_summary,
            candidate_github=candidate_github,
            candidate_linkedin=candidate_linkedin,
            recruiter_id=recruiter_id,
            match_score=match_score,
            notes=notes
        )
        return result
    except Exception as e:
        # Always return a valid JSON string, even on error
        error_msg = str(e)
        # Clean error message to prevent JSON encoding issues
        error_msg = error_msg.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        error_msg = error_msg[:500]  # Truncate very long error messages
        
        error_response = {
            "status": "error",
            "message": f"Candidate submission failed: {error_msg}",
            "error_type": type(e).__name__
        }
        
        # Ensure JSON is always valid
        try:
            return json.dumps(error_response, ensure_ascii=False)
        except (TypeError, ValueError) as json_error:
            # Fallback if JSON encoding fails
            return json.dumps({
                "status": "error",
                "message": "Candidate submission failed. Error details could not be serialized.",
                "error_type": "SerializationError"
            })

@mcp.tool()
async def get_pipeline_status(job_opening_id: int = None) -> str:
    """
    Get hiring pipeline status for a job or all jobs.
    
    Args:
        job_opening_id: Optional job opening ID to filter by
    
    Returns:
        JSON string with pipeline status grouped by stage
    """
    try:
        if hiring_pipeline_tool is None:
            error_response = {
                "status": "error",
                "message": "HiringPipelineTool not initialized. Check server logs.",
                "error_type": "InitializationError"
            }
            return json.dumps(error_response)
        
        return hiring_pipeline_tool.get_pipeline_status(job_opening_id=job_opening_id)
    except Exception as e:
        error_response = {
            "status": "error",
            "message": f"Pipeline status retrieval failed: {str(e)}",
            "error_type": type(e).__name__
        }
        return json.dumps(error_response)

@mcp.tool()
async def get_candidate_resume(
    submission_id: int = None,
    candidate_name: str = None,
    candidate_email: str = None
) -> str:
    """
    Get full resume details for a candidate submission.
    
    Can search by either submission_id OR by candidate name and email.
    If searching by name/email, finds the most recent submission matching those criteria.
    
    **Search Methods:**
    - Method 1: Provide submission_id (integer) - requires candidate to exist in hiring_pipeline
    - Method 2: Provide candidate_name and candidate_email - searches directly in resume_submissions table
    
    **IMPORTANT:** For employer review workflow, use Method 2 (name/email) to retrieve existing resumes
    without needing to create a submission first.
    
    Args:
        submission_id: Optional integer ID of candidate submission (if provided, uses this)
        candidate_name: Optional candidate's full name (required if submission_id not provided)
        candidate_email: Optional candidate's email (required if submission_id not provided)
    
    Returns:
        JSON string with full resume data including submission_id, resume_data, skills, extracted_text, etc.
    """
    try:
        if hiring_pipeline_tool is None:
            error_response = {
                "status": "error",
                "message": "HiringPipelineTool not initialized. Check server logs.",
                "error_type": "InitializationError"
            }
            return json.dumps(error_response)
        
        return hiring_pipeline_tool.get_candidate_resume(
            submission_id=submission_id,
            candidate_name=candidate_name,
            candidate_email=candidate_email
        )
    except Exception as e:
        error_response = {
            "status": "error",
            "message": f"Resume retrieval failed: {str(e)}",
            "error_type": type(e).__name__
        }
        return json.dumps(error_response)

@mcp.tool()
async def update_pipeline_stage(
    submission_id: int,
    new_stage: str,
    stage_status: str = "in-progress",
    feedback: str = ""
) -> str:
    """
    Update candidate's pipeline stage.
    
    Args:
        submission_id: Integer ID of candidate submission (matches resume_submissions.id)
        new_stage: screening, technical-interview, cultural-fit, offer, hired
        stage_status: pending, in-progress, completed, rejected
        feedback: Interview feedback or notes
    
    Returns:
        JSON string with updated pipeline entry
    """
    try:
        if hiring_pipeline_tool is None:
            error_response = {
                "status": "error",
                "message": "HiringPipelineTool not initialized. Check server logs.",
                "error_type": "InitializationError"
            }
            return json.dumps(error_response)
        
        return hiring_pipeline_tool.update_pipeline_stage(
            submission_id=submission_id,
            new_stage=new_stage,
            stage_status=stage_status,
            feedback=feedback
        )
    except Exception as e:
        error_response = {
            "status": "error",
            "message": f"Pipeline update failed: {str(e)}",
            "error_type": type(e).__name__
        }
        return json.dumps(error_response)

@mcp.tool()
async def health_check() -> str:
    """Health check endpoint for the MCP server"""
    return json.dumps({
        "status": "healthy",
        "server": "Staffing MCP Agent",
        "tools_count": len(mcp.list_tools()) if hasattr(mcp, 'list_tools') else 5
    })

if __name__ == "__main__":
    # Initialize and run the server
    print("\n" + "=" * 60)
    print("Starting Staffing MCP Agent Server")
    print("=" * 60)
    print(f"📍 Server: http://localhost:{PORT}")
    print(f"🔧 Transport: streamable-http")
    print(f"📦 Tools: 6 available (search_jobs, create_candidate_submission, get_pipeline_status, get_candidate_resume, update_pipeline_stage, health_check)")
    print(f"💡 Test with: npx @modelcontextprotocol/inspector python mcpstaffingagent.py")
    print("=" * 60 + "\n")
    print(f"[INFO] MCP endpoint will be available at: http://localhost:{PORT}/mcp")
    print(f"[INFO] ADK agents should connect to: http://localhost:{PORT}/mcp")
    print("=" * 60 + "\n")
    
    try:
        print(f"[INFO] Starting FastMCP server on port {PORT}...")
        mcp.run(transport='streamable-http')
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Server crashed: {e}")
        import traceback
        traceback.print_exc()
        raise

