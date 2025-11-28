"""
Candidate Submission Tool - Generate candidate submission packages.
Equivalent to purchase order generation in supply chain.
"""
from supabase import create_client, Client
import json
import os
from datetime import datetime
from typing import Optional, Dict, Set

class CandidateSubmissionTool:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set. "
                "Please configure these in your .env file."
            )
        
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Supabase client: {e}") from e
        
        # Cache for column existence checks (performance optimization)
        self._column_cache: Optional[Set[str]] = None
    
    def create_submission(
        self,
        candidate_name: str,
        candidate_email: str,
        job_opening_id: Optional[int] = None,  # Optional to support JD summary workflow
        job_description_summary: Optional[str] = None,  # JD summary (max 1028 chars) - stored in notes if job_opening_id is None
        candidate_github: str = None,
        candidate_linkedin: str = None,
        recruiter_id: str = None,
        match_score: float = 0.0,
        notes: str = ""
    ) -> str:
        """
        Create a candidate submission for a job opening.
        
        **REQUIRED ARGUMENTS:**
        - candidate_name: Candidate's full name (maps to 'name' in resume_submissions)
        - candidate_email: Candidate's email (maps to 'email' in resume_submissions)
        
        **OPTIONAL ARGUMENTS:**
        - job_opening_id: Optional integer ID of the job opening (not required)
        - job_description_summary: Job description summary (max 1028 characters). If job_opening_id is None, this will be stored in notes field.
        - candidate_github: GitHub profile URL (optional - only inserted if column exists)
        - candidate_linkedin: LinkedIn profile URL (optional - only inserted if column exists)
        - recruiter_id: UUID of the recruiter making submission (optional, not required)
        - match_score: Automated match score (0.00-1.00, defaults to 0.0)
        - notes: Additional notes about the candidate (optional)
        
        **IMPORTANT:** Only candidate_name and candidate_email are required.
        If job_opening_id is not provided, job_description_summary will be stored in the notes field.
        
        Returns:
            JSON string with submission details
        """
        try:
            # Generate unique submission number
            submission_number = f"SUB-{datetime.now().strftime('%Y%m%d')}-{self._generate_random_id()}"
            
            # Get available columns first to build submission data dynamically
            available_columns = self._get_available_columns()
            
            # Build base submission data with REQUIRED fields that always exist
            submission_data: Dict = {
                "name": candidate_name,
                "email": candidate_email
            }
            
            # Add extended fields ONLY if columns exist in database
            # This ensures compatibility with both old and new schemas
            
            if job_opening_id is not None and "job_opening_id" in available_columns:
                submission_data["job_opening_id"] = job_opening_id
            
            if "submission_number" in available_columns:
                submission_data["submission_number"] = submission_number
            
            if "status" in available_columns:
                submission_data["status"] = "submitted"
            
            if recruiter_id and "recruiter_id" in available_columns:
                submission_data["recruiter_id"] = recruiter_id
            
            if match_score is not None and match_score > 0 and "match_score" in available_columns:
                submission_data["match_score"] = match_score
            
            # Handle job_description_summary: if job_opening_id is None, store JD summary in notes
            if job_opening_id is None and job_description_summary:
                # Prepend JD summary to notes, ensuring it doesn't exceed total notes length
                combined_notes = f"JD Summary: {job_description_summary}\n\n{notes}".strip()
                if "notes" in available_columns:
                    submission_data["notes"] = combined_notes[:1028]  # Truncate if too long
            elif notes and "notes" in available_columns:
                submission_data["notes"] = notes
            
            # Add optional GitHub/LinkedIn only if columns exist AND values provided
            if candidate_github and "candidate_github" in available_columns:
                submission_data["candidate_github"] = candidate_github
            
            if candidate_linkedin and "candidate_linkedin" in available_columns:
                submission_data["candidate_linkedin"] = candidate_linkedin
            
            # Insert into Supabase
            result = self.supabase.table("resume_submissions").insert(submission_data).execute()
            
            if not result.data or len(result.data) == 0:
                return json.dumps({
                    "status": "error",
                    "message": "Submission created but no data returned from database"
                })
            
            submission_id = result.data[0]["id"]
            
            # Also create initial pipeline stage (only if hiring_pipeline table exists)
            # Check if we can access the hiring_pipeline table
            try:
                pipeline_entry = {
                    "submission_id": submission_id,
                    "stage": "screening",
                    "stage_status": "pending"
                }
                self.supabase.table("hiring_pipeline").insert(pipeline_entry).execute()
            except Exception as pipeline_error:
                # Pipeline table might not exist - that's okay, continue without it
                print(f"[WARNING] Could not create pipeline entry: {pipeline_error}")
                # Don't fail the submission if pipeline creation fails
            
            return json.dumps({
                "status": "success",
                "message": "Candidate submission created successfully",
                "submission_id": submission_id,  # Include submission_id at top level for easy access
                "submission": result.data[0],
                "warnings": self._get_warnings(candidate_github, candidate_linkedin, available_columns)
            })
            
        except Exception as e:
            error_msg = str(e)
            # Clean error message to prevent JSON encoding issues
            # Remove any control characters and ensure proper escaping
            error_msg = error_msg.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            error_msg = error_msg[:500]  # Truncate very long error messages
            
            # Provide more helpful error messages for specific error types
            if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
                error_response = {
                    "status": "error",
                    "message": f"Database schema mismatch: {error_msg}. Please run the schema migration to add optional columns.",
                    "error_type": "SchemaError"
                }
            elif "row-level security" in error_msg.lower() or "policy" in error_msg.lower() or "permission denied" in error_msg.lower():
                error_response = {
                    "status": "error",
                    "message": "Row-level security policy violation. Please ensure SUPABASE_SERVICE_KEY is set correctly and has proper permissions. If using RLS, you may need to disable it for the resume_submissions table or add appropriate policies.",
                    "error_type": "SecurityError",
                    "original_error": error_msg
                }
            else:
                error_response = {
                    "status": "error",
                    "message": f"Submission creation failed: {error_msg}",
                    "error_type": type(e).__name__
                }
            
            # Ensure JSON is always valid by using json.dumps
            try:
                return json.dumps(error_response, ensure_ascii=False)
            except (TypeError, ValueError) as json_error:
                # Fallback if JSON encoding fails
                return json.dumps({
                    "status": "error",
                    "message": f"Submission creation failed. Error details could not be serialized: {str(json_error)}",
                    "error_type": "SerializationError"
                })
    
    def _get_available_columns(self) -> Set[str]:
        """
        Get list of available columns in resume_submissions table.
        Uses caching to avoid repeated queries.
        
        Returns:
            Set of column names that exist in the table
        """
        # Return cached result if available
        if self._column_cache is not None:
            return self._column_cache
        
        try:
            # Query a single row to get column information
            # This is a lightweight way to discover available columns
            test_query = self.supabase.table("resume_submissions").select("*").limit(1).execute()
            
            if test_query.data and len(test_query.data) > 0:
                # Extract column names from the first row's keys
                available_columns = set(test_query.data[0].keys())
            else:
                # If table is empty, try inserting a minimal test record
                # We'll use a try-except approach to discover columns
                available_columns = self._discover_columns_via_insert()
            
            # Cache the result
            self._column_cache = available_columns
            return available_columns
            
        except Exception as e:
            # If query fails, assume only basic columns exist (matching actual Supabase schema)
            # This is a safe fallback that ensures backward compatibility
            print(f"[WARNING] Could not query table schema: {e}. Assuming basic columns only.")
            # Based on actual Supabase table structure:
            basic_columns = {
                "id", "name", "email", "phone", "resume_filename", 
                "resume_data", "file_type"
            }
            self._column_cache = basic_columns
            return basic_columns
    
    def _discover_columns_via_insert(self) -> Set[str]:
        """
        Discover available columns when table is empty.
        Uses a conservative approach: only include columns we're certain exist.
        
        Returns:
            Set of column names that are guaranteed to exist
        """
        # Conservative set: only include columns that match the ACTUAL Supabase schema
        # Based on the actual table structure shown in Supabase UI
        known_columns = {
            "id", "name", "email", "phone", "resume_filename", 
            "resume_data", "file_type"
        }
        
        # Note: Extended columns (job_opening_id, submission_number, status, etc.)
        # will be discovered dynamically when they exist via the schema migration
        # This conservative approach ensures backward compatibility with existing tables
        
        return known_columns
    
    def _get_warnings(
        self, 
        candidate_github: Optional[str], 
        candidate_linkedin: Optional[str], 
        available_columns: Set[str]
    ) -> list:
        """
        Generate warnings if optional fields were provided but columns don't exist.
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        if candidate_github and "candidate_github" not in available_columns:
            warnings.append("candidate_github field provided but column does not exist in database")
        
        if candidate_linkedin and "candidate_linkedin" not in available_columns:
            warnings.append("candidate_linkedin field provided but column does not exist in database")
        
        return warnings
    
    def _generate_random_id(self) -> str:
        """Generate random 6-digit ID."""
        import random
        return str(random.randint(100000, 999999))

