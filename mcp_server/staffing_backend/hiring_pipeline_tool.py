"""
Hiring Pipeline Tool - Manage candidate interview pipeline.
Equivalent to production queue in supply chain.
"""
from supabase import create_client, Client
import json
import base64
import io
from PyPDF2 import PdfReader
import os

class HiringPipelineTool:
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
    
    def get_pipeline_status(self, job_opening_id: int = None) -> str:
        """
        Get hiring pipeline status for a job or all jobs.
        
        Returns pipeline entries with resume data for submitted candidates.
        Access is controlled through hiring_pipeline relationship - employers only see
        resumes for candidates that have been submitted to them.
        """
        try:
            # Get pipeline entries with resume submission details
            # Using !inner ensures only resumes with pipeline entries are returned
            # This enforces relationship-based access (employers only see submitted candidates)
            query = self.supabase.table("hiring_pipeline")\
                .select("*, resume_submissions!inner(*)")
            
            result = query.execute()
            
            # Filter by job_opening_id if provided
            if job_opening_id:
                filtered_data = [
                    entry for entry in result.data 
                    if entry.get("resume_submissions", {}).get("job_opening_id") == job_opening_id
                ]
                result.data = filtered_data
            
            # Group by stage
            pipeline_by_stage = {}
            for entry in result.data:
                stage = entry["stage"]
                if stage not in pipeline_by_stage:
                    pipeline_by_stage[stage] = []
                pipeline_by_stage[stage].append(entry)
            
            return json.dumps({
                "status": "success",
                "total_candidates": len(result.data),
                "pipeline_by_stage": pipeline_by_stage
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Pipeline query failed: {str(e)}"
            })
    
    def update_pipeline_stage(
        self,
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
        """
        try:
            # Insert new pipeline stage
            pipeline_data = {
                "submission_id": submission_id,
                "stage": new_stage,
                "stage_status": stage_status,
                "feedback": feedback
            }
            
            result = self.supabase.table("hiring_pipeline").insert(pipeline_data).execute()
            
            # Update submission status
            submission_status_map = {
                "screening": "reviewing",
                "technical-interview": "interviewing",
                "cultural-fit": "interviewing",
                "offer": "offered",
                "hired": "hired"
            }
            
            self.supabase.table("resume_submissions")\
                .update({"status": submission_status_map.get(new_stage, "submitted")})\
                .eq("id", submission_id)\
                .execute()
            
            return json.dumps({
                "status": "success",
                "message": f"Pipeline updated to {new_stage}",
                "pipeline_entry": result.data[0]
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Pipeline update failed: {str(e)}"
            })
    
    def get_candidate_resume(
        self, 
        submission_id: int = None,
        candidate_name: str = None,
        candidate_email: str = None
    ) -> str:
        """
        Get full resume details for a candidate submission.
        
        Can search by either submission_id OR by candidate name and email.
        If searching by name/email, finds the most recent submission matching those criteria.
        
        Security: When using submission_id, only returns resume if submission_id exists in hiring_pipeline
        (ensures employer has legitimate access through submission relationship).
        When searching by name/email, returns the resume directly (no pipeline check needed for review purposes).
        
        Args:
            submission_id: Optional ID of the candidate submission (if provided, uses this)
            candidate_name: Optional candidate's full name (required if submission_id not provided)
            candidate_email: Optional candidate's email (required if submission_id not provided)
        
        Returns:
            JSON string with full resume data including submission_id
        """
        try:
            # Validate parameters
            if not submission_id and (not candidate_name or not candidate_email):
                return json.dumps({
                    "status": "error",
                    "message": "Either submission_id OR both candidate_name and candidate_email must be provided."
                })
            
            resume_data = None
            found_submission_id = None
            
            if submission_id:
                # Method 1: Search by submission_id (with pipeline security check)
                pipeline_check = self.supabase.table("hiring_pipeline")\
                    .select("submission_id")\
                    .eq("submission_id", submission_id)\
                    .limit(1)\
                    .execute()
                
                if not pipeline_check.data or len(pipeline_check.data) == 0:
                    return json.dumps({
                        "status": "error",
                        "message": f"Submission ID {submission_id} not found in hiring pipeline. Access denied - only submitted candidates are accessible."
                    })
                
                # Get full resume data
                resume_query = self.supabase.table("resume_submissions")\
                    .select("*")\
                    .eq("id", submission_id)\
                    .single()\
                    .execute()
                
                if not resume_query.data:
                    return json.dumps({
                        "status": "error",
                        "message": f"Resume not found for submission ID {submission_id}"
                    })
                
                resume_data = resume_query.data
                found_submission_id = submission_id
                decoded_text = self._extract_text_from_resume(resume_data)
                if decoded_text:
                    resume_data["decoded_text"] = decoded_text
            else:
                # Method 2: Search by name and email
                resume_query = self.supabase.table("resume_submissions")\
                    .select("*")\
                    .eq("name", candidate_name)\
                    .eq("email", candidate_email)\
                    .order("id", desc=True)\
                    .limit(1)\
                    .execute()
                
                if not resume_query.data or len(resume_query.data) == 0:
                    return json.dumps({
                        "status": "error",
                        "message": f"Resume not found for candidate {candidate_name} ({candidate_email}). The candidate may not exist in the database yet."
                    })
                
                resume_data = resume_query.data[0]
                found_submission_id = resume_data.get("id")
                decoded_text = self._extract_text_from_resume(resume_data)
                if decoded_text:
                    resume_data["decoded_text"] = decoded_text
            
            return json.dumps({
                "status": "success",
                "submission_id": found_submission_id,
                "resume": resume_data
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Failed to retrieve resume: {str(e)}"
            })

    def _extract_text_from_resume(self, resume_data: dict) -> str:
        """
        Attempt to decode resume_data (base64 PDF/text) into readable text for analysis.
        Returns decoded text or None if extraction fails.
        """
        if not resume_data or not isinstance(resume_data, dict):
            return None

        encoded_data = resume_data.get("resume_data")
        if not encoded_data or not isinstance(encoded_data, str):
            return None

        file_type = (resume_data.get("file_type") or "").lower()

        try:
            raw_bytes = base64.b64decode(encoded_data, validate=True)
        except Exception:
            return None

        # If PDF, try to extract text using PyPDF2
        if "pdf" in file_type or raw_bytes.startswith(b"%PDF"):
            try:
                reader = PdfReader(io.BytesIO(raw_bytes))
                text_chunks = []
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    if page_text:
                        text_chunks.append(page_text)
                combined = "\n\n".join(text_chunks).strip()
                if combined:
                    return combined
            except Exception:
                pass

        # Fallback: attempt to decode raw bytes as UTF-8 text
        try:
            decoded = raw_bytes.decode("utf-8", errors="ignore").strip()
            return decoded or None
        except Exception:
            return None

