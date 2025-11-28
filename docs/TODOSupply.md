# Staffing Agency Agent Suite - Implementation Plan

## 🎯 Strategic Vision

Convert the supply chain orchestrator system into a **Staffing Agency Agent Suite** that connects recruiters (buyers) with employer job openings (inventory) using Supabase as the job database.

### Business Model Mapping

| Supply Chain Component | Staffing Agency Equivalent |
|------------------------|---------------------------|
| **Buyer** | **Recruiter/Staffing Agency** |
| **Supplier** | **Employer/Client Company** |
| **Inventory** | **Job Openings Database (Supabase)** |
| **Purchase Order** | **Candidate Submission / Job Offer** |
| **Production Queue** | **Hiring Pipeline / Interview Schedule** |
| **Items** | **Candidates** |
| **Restock Needs** | **Open Positions Needing Candidates** |

---

## 📊 Architecture Overview

```
┌─────────────────┐
│   Next.js UI    │  ← User selects Recruiter or Employer mode
│   (Frontend)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   ADK Agents    │  ← Staffing orchestrators
│  Recruiter/     │
│  Employer Modes │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   MCP Server    │
│  (Cloud Run)    │
│  Staffing Tools │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ↓                 ↓
┌─────────────────┐  ┌──────────────────┐
│    Supabase     │  │  JSearch API     │
│ (Primary Source)│  │  (Fallback)      │
│  Jobs Database  │  │  RapidAPI        │
└─────────────────┘  └──────────────────┘
         │                 │
         └────────┬────────┘
                  │
                  ↓
         Normalized Results
         (Same format)
```

**Fallback Flow:**
1. Try Supabase first (your existing database)
2. If Supabase fails/pauses → Automatically use JSearch API
3. Normalize JSearch results to match Supabase schema
4. Return consistent format to users

---

## 🗂️ Phase 1: Database Schema Alignment

### 1.1 Existing Supabase Schema

**Your existing `job_flow` table structure:**
```sql
-- Existing columns (already in your database):
id (int8)                    -- Primary key
job_title (text)            -- Job title
job_location (text)         -- Location (NULL = remote)
job_apply_link (text)       -- Application URL
job_salary (text)           -- General salary field (mostly NULL)
job_min_salary (text)       -- Minimum salary (can be annual or hourly)
job_max_salary (text)       -- Maximum salary (can be annual or hourly)
```

**Note:** Your existing table uses `int8` for IDs and `text` for salary fields (supports both annual and hourly rates).

### 1.2 Additional Tables to Create

Since your job table already exists, we only need to add supporting tables for the staffing workflow:

#### `employers` (replaces suppliers)
```sql
CREATE TABLE employers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_name VARCHAR(255) NOT NULL,
  industry VARCHAR(100),
  contact_name VARCHAR(255),
  contact_email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  website VARCHAR(255),
  address TEXT,
  company_size VARCHAR(50), -- startup, small, medium, enterprise
  preferred_staffing_types TEXT[], -- contract, contract-to-hire, direct-hire
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### `resume_submissions` (replaces purchase orders - existing table)
```sql
-- Existing columns in your resume_submissions table:
id (int4)                        -- Primary key
name (text)                      -- Candidate name
email (text)                     -- Candidate email
phone (text)                     -- Candidate phone
resume_filename (text)           -- Resume file name
resume_data (text)               -- Resume content/base64
file_type (text)                 -- application/pdf, etc.
created_at (timestamptz)         -- Submission timestamp
timestamp (text)                 -- Additional timestamp field
summary (text)                   -- Resume summary
extracted_text (text)            -- Extracted text from resume
skills (jsonb)                   -- Candidate skills
years_experience (int4)          -- Years of experience
matched_recruiters (jsonb)       -- Matched recruiters
candidate_tier (text)            -- Candidate tier/quality
classification_details (jsonb)   -- Classification metadata

-- Optional: Add missing columns if needed
ALTER TABLE resume_submissions 
ADD COLUMN IF NOT EXISTS job_opening_id INTEGER REFERENCES job_flow(id),
ADD COLUMN IF NOT EXISTS submission_number VARCHAR(50) UNIQUE,
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'submitted',
ADD COLUMN IF NOT EXISTS match_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS recruiter_id UUID REFERENCES recruiters(id);

CREATE INDEX IF NOT EXISTS idx_resume_status ON resume_submissions(status);
CREATE INDEX IF NOT EXISTS idx_resume_job ON resume_submissions(job_opening_id);
```

#### `recruiters` (replaces buyer accounts)
```sql
CREATE TABLE recruiters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(50),
  agency_name VARCHAR(255),
  specializations TEXT[], -- e.g., ['frontend', 'backend', 'devops']
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### `hiring_pipeline` (replaces production queue)
```sql
CREATE TABLE hiring_pipeline (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  submission_id INTEGER REFERENCES resume_submissions(id),
  stage VARCHAR(50) NOT NULL, -- screening, technical-interview, cultural-fit, offer, hired
  stage_status VARCHAR(50) DEFAULT 'pending', -- pending, in-progress, completed, rejected
  scheduled_date TIMESTAMP,
  completed_date TIMESTAMP,
  interviewer VARCHAR(255),
  feedback TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pipeline_stage ON hiring_pipeline(stage, stage_status);
```

### 1.3 Optional: Add Missing Columns to Existing Table

If you want to enhance your existing `job_flow` table with additional fields for better filtering:

```sql
-- Add optional columns to existing table (if needed)
ALTER TABLE job_flow 
ADD COLUMN IF NOT EXISTS job_description TEXT,
ADD COLUMN IF NOT EXISTS tech_stack TEXT[], -- Array of technologies
ADD COLUMN IF NOT EXISTS years_experience INTEGER,
ADD COLUMN IF NOT EXISTS work_type VARCHAR(50), -- contract, contract-to-hire, direct-hire
ADD COLUMN IF NOT EXISTS remote_type VARCHAR(50), -- remote, hybrid, on-site
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'open', -- open, filled, closed
ADD COLUMN IF NOT EXISTS urgency VARCHAR(50) DEFAULT 'medium', -- low, medium, high, critical
ADD COLUMN IF NOT EXISTS posted_date TIMESTAMP DEFAULT NOW();

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_job_location ON job_flow(job_location);
CREATE INDEX IF NOT EXISTS idx_job_status ON job_flow(status) WHERE status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_job_urgency ON job_flow(urgency) WHERE urgency IS NOT NULL;
```

**Note:** These are optional enhancements. The MCP tools will work with your existing schema as-is.

**TODO:**
- [ ] Verify Supabase connection and credentials
- [ ] Test querying existing `job_flow` table
- [ ] Create additional tables (employers, hiring_pipeline, recruiters)
- [ ] Optionally add enhancement columns to existing table
- [ ] Add indexes for performance on existing columns
- [ ] Set up Row-Level Security (RLS) policies if needed

---

## 🛠️ Phase 2: MCP Tools Migration (MongoDB → Supabase)

### 2.0 Fallback Strategy Overview

**Problem:** Supabase free tier pauses databases after inactivity, causing job search to fail.

**Solution:** Implement JSearch API (RapidAPI) as automatic fallback.

**How It Works:**
1. **Primary Path**: Always query Supabase first (your existing database with thousands of jobs)
2. **Fallback Trigger**: If Supabase fails or returns 0 results, automatically switch to JSearch API
3. **Result Normalization**: JSearch results are converted to match your Supabase schema format
4. **Transparent**: Users get the same response format regardless of data source

**Benefits:**
- ✅ No downtime when Supabase pauses
- ✅ Seamless user experience
- ✅ Cost-effective (JSearch only used when needed)
- ✅ Same response format from both sources

### 2.1 New MCP Staffing Tools

**File:** `mcp_server/staffing_backend/job_search_tool.py`

Replaces: `restock_inventory_tool.py` (analyze inventory)

```python
"""
Job Search Tool - Query job openings from Supabase with JSearch API fallback.
Equivalent to inventory analysis in supply chain.

Fallback Strategy:
1. Try Supabase first (primary data source)
2. If Supabase fails or returns no results, fall back to JSearch API
3. Normalize JSearch results to match Supabase schema format
"""
from supabase import create_client, Client
import json
import os
import requests
from typing import Optional, List, Dict

class JobSearchTool:
    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if supabase_url and supabase_key:
            try:
                self.supabase: Client = create_client(supabase_url, supabase_key)
                self.supabase_enabled = True
            except Exception as e:
                print(f"⚠️  Supabase initialization failed: {e}")
                self.supabase_enabled = False
        else:
            self.supabase_enabled = False
        
        # Initialize JSearch API credentials (fallback)
        self.jsearch_host = os.getenv("JSEARCH_HOST", "jsearch.p.rapidapi.com")
        self.jsearch_api_key = os.getenv("JSEARCHRAPDKEY")
        self.jsearch_enabled = bool(self.jsearch_api_key)
        
        if not self.supabase_enabled and not self.jsearch_enabled:
            raise ValueError("Either SUPABASE_URL/SUPABASE_SERVICE_KEY or JSEARCHRAPDKEY must be configured")
    
    def search_jobs(
        self,
        job_title: str = None,
        location: str = None,
        min_salary: float = None,
        max_salary: float = None,
        remote_only: bool = False,
        limit: int = 10
    ) -> str:
        """
        Search job openings from Supabase with JSearch API fallback.
        
        Args:
            job_title: Search term in job title (partial match)
            location: Job location (partial match, NULL = remote)
            min_salary: Minimum salary filter (numeric)
            max_salary: Maximum salary filter (numeric)
            remote_only: If True, only return jobs where job_location IS NULL
            limit: Max number of results
        
        Returns:
            JSON string with matching job openings
        """
        # Try Supabase first (primary data source)
        if self.supabase_enabled:
            try:
                result = self._search_supabase(
                    job_title, location, min_salary, max_salary, remote_only, limit
                )
                
                # If Supabase returns results, use them
                if result and result.get("total_jobs", 0) > 0:
                    result["data_source"] = "supabase"
                    return json.dumps(result)
                
                # If Supabase returns no results but didn't error, still try fallback
                # (in case database is paused but connection works)
                print("⚠️  Supabase returned no results, trying JSearch API fallback...")
                
            except Exception as e:
                print(f"⚠️  Supabase query failed: {e}, trying JSearch API fallback...")
        
        # Fallback to JSearch API
        if self.jsearch_enabled:
            try:
                result = self._search_jsearch_api(
                    job_title, location, min_salary, max_salary, remote_only, limit
                )
                if result:
                    result["data_source"] = "jsearch_api"
                    return json.dumps(result)
            except Exception as e:
                print(f"❌ JSearch API fallback also failed: {e}")
        
        # Both sources failed
        return json.dumps({
            "status": "error",
            "message": "Both Supabase and JSearch API failed. Please check your configuration.",
            "total_jobs": 0,
            "jobs": []
        })
    
    def _search_supabase(
        self,
        job_title: str = None,
        location: str = None,
        min_salary: float = None,
        max_salary: float = None,
        remote_only: bool = False,
        limit: int = 10
    ) -> Optional[Dict]:
        """Search jobs in Supabase database."""
        try:
            query = self.supabase.table("job_flow").select("*")
            
            # Filter by job title (case-insensitive partial match)
            if job_title:
                query = query.ilike("job_title", f"%{job_title}%")
            
            # Filter by location
            if location:
                query = query.ilike("job_location", f"%{location}%")
            
            # Filter for remote jobs only (job_location IS NULL)
            if remote_only:
                query = query.is_("job_location", "null")
            
            # Execute query
            result = query.limit(limit).execute()
            
            # Post-process salary filtering (since salary fields are text)
            filtered_jobs = result.data
            if min_salary is not None or max_salary is not None:
                filtered_jobs = []
                for job in result.data:
                    min_sal = self._parse_salary(job.get("job_min_salary"))
                    max_sal = self._parse_salary(job.get("job_max_salary"))
                    
                    # Apply filters
                    if min_salary is not None and max_sal is not None and max_sal < min_salary:
                        continue
                    if max_salary is not None and min_sal is not None and min_sal > max_salary:
                        continue
                    
                    filtered_jobs.append(job)
            
            return {
                "status": "success",
                "total_jobs": len(filtered_jobs),
                "jobs": filtered_jobs,
                "filters_applied": {
                    "job_title": job_title,
                    "location": location,
                    "remote_only": remote_only,
                    "min_salary": min_salary,
                    "max_salary": max_salary
                }
            }
        except Exception as e:
            raise Exception(f"Supabase search failed: {str(e)}")
    
    def _search_jsearch_api(
        self,
        job_title: str = None,
        location: str = None,
        min_salary: float = None,
        max_salary: float = None,
        remote_only: bool = False,
        limit: int = 10
    ) -> Optional[Dict]:
        """Search jobs using JSearch API (RapidAPI) as fallback."""
        try:
            # Build JSearch API query parameters
            query_params = {
                "query": job_title or "jobs",
                "page": "1",
                "num_pages": "1"
            }
            
            # Add location filter
            if location:
                query_params["location"] = location
            elif remote_only:
                query_params["remote_jobs_only"] = "true"
            
            # Add salary filters (JSearch uses salary_min and salary_max)
            if min_salary:
                query_params["salary_min"] = str(int(min_salary))
            if max_salary:
                query_params["salary_max"] = str(int(max_salary))
            
            # Make API request
            url = f"https://{self.jsearch_host}/search"
            headers = {
                "X-RapidAPI-Key": self.jsearch_api_key,
                "X-RapidAPI-Host": self.jsearch_host
            }
            
            response = requests.get(url, headers=headers, params=query_params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Normalize JSearch results to match Supabase schema
            jobs = []
            for job in data.get("data", [])[:limit]:
                normalized_job = self._normalize_jsearch_result(job)
                if normalized_job:
                    jobs.append(normalized_job)
            
            return {
                "status": "success",
                "total_jobs": len(jobs),
                "jobs": jobs,
                "filters_applied": {
                    "job_title": job_title,
                    "location": location,
                    "remote_only": remote_only,
                    "min_salary": min_salary,
                    "max_salary": max_salary
                }
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"JSearch API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"JSearch API processing failed: {str(e)}")
    
    def _normalize_jsearch_result(self, jsearch_job: Dict) -> Optional[Dict]:
        """
        Normalize JSearch API result to match Supabase schema format.
        Converts JSearch fields to our standard format.
        """
        try:
            # Extract salary information
            min_salary = None
            max_salary = None
            salary_str = jsearch_job.get("job_min_salary") or jsearch_job.get("salary_min")
            
            if salary_str:
                min_salary = str(salary_str)
            
            salary_str = jsearch_job.get("job_max_salary") or jsearch_job.get("salary_max")
            if salary_str:
                max_salary = str(salary_str)
            
            # Determine if remote
            job_location = jsearch_job.get("job_city") or jsearch_job.get("job_location")
            if jsearch_job.get("job_is_remote") or not job_location:
                job_location = None  # NULL = remote
            
            return {
                "id": jsearch_job.get("job_id") or jsearch_job.get("job_google_link", "").split("/")[-1],
                "job_title": jsearch_job.get("job_title", ""),
                "job_location": job_location,
                "job_apply_link": jsearch_job.get("job_apply_link") or jsearch_job.get("job_google_link", ""),
                "job_salary": None,  # JSearch doesn't provide this field
                "job_min_salary": min_salary,
                "job_max_salary": max_salary,
                # Additional fields from JSearch that might be useful
                "job_description": jsearch_job.get("job_description", ""),
                "employer_name": jsearch_job.get("employer_name", ""),
                "job_posted_at": jsearch_job.get("job_posted_at_datetime_utc", ""),
            }
        except Exception as e:
            print(f"⚠️  Failed to normalize JSearch result: {e}")
            return None
    
    def _parse_salary(self, salary_str: str) -> float:
        """Parse salary string to float. Handles both annual and hourly rates."""
        if not salary_str:
            return None
        try:
            # Remove any non-numeric characters except decimal point
            cleaned = ''.join(c for c in str(salary_str) if c.isdigit() or c == '.')
            return float(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None
```

**File:** `mcp_server/staffing_backend/candidate_submission_tool.py`

Replaces: `document_generator_tool.py` (generate purchase orders)

```python
"""
Candidate Submission Tool - Generate candidate submission packages.
Equivalent to purchase order generation in supply chain.
"""
from supabase import create_client, Client
import json
import os
from datetime import datetime

class CandidateSubmissionTool:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
    
    def create_submission(
        self,
        job_opening_id: int,  # Note: Using int8 to match existing schema
        candidate_name: str,
        candidate_email: str,
        candidate_github: str = None,
        candidate_linkedin: str = None,
        recruiter_id: str = None,
        match_score: float = 0.0,
        notes: str = ""
    ) -> str:
        """
        Create a candidate submission for a job opening.
        
        Args:
            job_opening_id: Integer ID of the job opening (matches existing schema)
            candidate_name: Candidate's full name (maps to 'name' in resume_submissions)
            candidate_email: Candidate's email (maps to 'email' in resume_submissions)
            candidate_github: GitHub profile URL (optional new column)
            candidate_linkedin: LinkedIn profile URL (optional new column)
            recruiter_id: UUID of the recruiter making submission
            match_score: Automated match score (0.00-1.00)
            notes: Additional notes about the candidate
        
        Returns:
            JSON string with submission details
        """
        try:
            # Generate unique submission number
            submission_number = f"SUB-{datetime.now().strftime('%Y%m%d')}-{self._generate_random_id()}"
            
            submission_data = {
                "submission_number": submission_number,
                "job_opening_id": job_opening_id,  # Integer ID from existing table
                "name": candidate_name,  # Maps to existing 'name' column
                "email": candidate_email,  # Maps to existing 'email' column
                "candidate_github": candidate_github,  # Optional new column
                "candidate_linkedin": candidate_linkedin,  # Optional new column
                "recruiter_id": recruiter_id,
                "match_score": match_score,
                "notes": notes,
                "status": "submitted"
            }
            
            # Insert into Supabase
            result = self.supabase.table("resume_submissions").insert(submission_data).execute()
            
            # Also create initial pipeline stage
            pipeline_entry = {
                "submission_id": result.data[0]["id"],
                "stage": "screening",
                "stage_status": "pending"
            }
            self.supabase.table("hiring_pipeline").insert(pipeline_entry).execute()
            
            return json.dumps({
                "status": "success",
                "message": "Candidate submission created successfully",
                "submission": result.data[0]
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Submission creation failed: {str(e)}"
            })
    
    def _generate_random_id(self) -> str:
        """Generate random 6-digit ID."""
        import random
        return str(random.randint(100000, 999999))
```

**File:** `mcp_server/staffing_backend/hiring_pipeline_tool.py`

Replaces: `purchase_queue_tool.py` (manage purchase queue)

```python
"""
Hiring Pipeline Tool - Manage candidate interview pipeline.
Equivalent to production queue in supply chain.
"""
from supabase import create_client, Client
import json
import os

class HiringPipelineTool:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
    
    def get_pipeline_status(self, job_opening_id: int = None) -> str:
        """Get hiring pipeline status for a job or all jobs."""
        try:
            query = self.supabase.table("hiring_pipeline")\
                .select("*, resume_submissions(name, job_opening_id)")
            
            if job_opening_id:
                query = query.eq("resume_submissions.job_opening_id", job_opening_id)
            
            result = query.execute()
            
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
        submission_id: str,
        new_stage: str,
        stage_status: str = "in-progress",
        feedback: str = ""
    ) -> str:
        """
        Update candidate's pipeline stage.
        
        Args:
            submission_id: UUID of candidate submission
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
```

**Requirements Update:**

Add to `mcp_server/staffing_backend/requirements.txt`:
```txt
supabase>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
fastmcp>=0.9.0
```

**TODO:**
- [ ] Create `mcp_server/staffing_backend/` directory
- [ ] Create `requirements.txt` with Supabase and requests dependencies
- [ ] Implement `job_search_tool.py` with Supabase + JSearch API fallback
- [ ] Test fallback mechanism (simulate Supabase pause)
- [ ] Test Supabase query (primary path)
- [ ] Test JSearch API fallback when Supabase is unavailable
- [ ] Test result normalization (JSearch → Supabase schema format)
- [ ] Implement `candidate_submission_tool.py` (replaces PO generation)
- [ ] Implement `hiring_pipeline_tool.py` (replaces production queue)
- [ ] Implement `employer_management_tool.py` (replaces supplier management)
- [ ] Implement `candidate_matching_tool.py` (new - AI-powered matching)
- [ ] Keep existing `email_monitoring_tool.py` (monitor employer communications)
- [ ] Keep existing `email_response_tool.py` (send responses to employers)
- [ ] Update `document_parser_tool.py` to parse resumes instead of POs
- [ ] Create `offer_letter_generator_tool.py` (replaces PDF PO generation)

---

## 🤖 Phase 3: Agent Refactoring

### 3.1 Recruiter Orchestrator Agent

**File:** `app/staffing_agents/recruiter_orchestrator_agent/adk_agent.py`

Replaces: `app/supply_chain/buyer_orchestrator_agent/adk_agent.py`

```python
"""
ADK Recruiter Orchestrator Agent

Orchestrates recruiter workflow: job search → candidate matching → submission
Converts from buyer workflow to recruiter workflow.
"""
import logging
from google.adk.agents import LlmAgent
from app.config import config

# Import sub-agents
from app.staffing_agents.job_search_agent.agent import create_agent as create_job_search_agent
from app.staffing_agents.candidate_matching_agent.agent import create_agent as create_matching_agent
from app.staffing_agents.submission_agent.agent import create_agent as create_submission_agent

logger = logging.getLogger(__name__)

def get_recruiter_orchestrator_agent() -> LlmAgent:
    """Lazy initialization of recruiter orchestrator."""
    try:
        # Create sub-agents
        job_search_agent = create_job_search_agent()
        matching_agent = create_matching_agent()
        submission_agent = create_submission_agent()
        
        return LlmAgent(
            name="RecruiterOrchestrator",
            model=config.model,
            description="Orchestrates recruiter workflow: job search → candidate matching → submission",
            sub_agents=[job_search_agent, matching_agent, submission_agent],
            instruction="""
You coordinate the recruiter workflow through specialized agents:

1. Job Search: Find open positions matching requirements
   - Delegate to JobSearchAgent to query job openings from Supabase
   - Filter by tech stack, location, work type, urgency, experience level
   - Review job descriptions and requirements

2. Candidate Matching: Match candidates to job requirements
   - Delegate to CandidateMatchingAgent to find suitable candidates
   - Use GitHub profiles to assess technical skills
   - Calculate match scores based on job requirements vs candidate skills
   - Rank candidates by relevance

3. Candidate Submission: Submit candidates to employers
   - Delegate to SubmissionAgent to create candidate submission packages
   - Generate personalized outreach emails to candidates
   - Track submission status in hiring pipeline
   - Coordinate employer communications

**Workflow Examples:**

"Find React developer jobs" → Use JobSearchAgent
"Match candidates to job SUB-20250120-123456" → Use CandidateMatchingAgent
"Submit candidate John Doe for Senior Frontend role" → Use SubmissionAgent
"Full recruiter workflow for DevOps positions" → Coordinate all three agents

**Decision Logic:**
- If user asks about available jobs → Use JobSearchAgent
- If user wants candidate recommendations → Use CandidateMatchingAgent
- If user wants to submit a candidate → Use SubmissionAgent
- If user wants end-to-end recruiting → Coordinate all agents sequentially

Always maintain context about job requirements, candidate profiles, and submission status.
Focus on finding the best candidate-job fit to maximize placement success.
""",
            output_key="recruiter_workflow_result",
        )
    except Exception as e:
        logger.error(f"Failed to initialize recruiter orchestrator: {e}")
        return LlmAgent(
            name="RecruiterOrchestrator",
            model=config.model,
            description="Recruiter orchestrator (MCP server connection required)",
            instruction="The recruiter orchestrator requires MCP_SERVER_URL to be configured.",
            output_key="recruiter_workflow_result",
        )

recruiter_orchestrator_agent = get_recruiter_orchestrator_agent()
```

### 3.2 Employer Orchestrator Agent

**File:** `app/staffing_agents/employer_orchestrator_agent/adk_agent.py`

Replaces: `app/supply_chain/supplier_orchestrator_agent/adk_agent.py`

```python
"""
ADK Employer Orchestrator Agent

Orchestrates employer workflow: candidate review → interview scheduling → hiring decisions
Converts from supplier workflow to employer workflow.
"""
import logging
from google.adk.agents import LlmAgent
from app.config import config

# Import sub-agents
from app.staffing_agents.candidate_review_agent.agent import create_agent as create_review_agent
from app.staffing_agents.interview_scheduling_agent.agent import create_agent as create_scheduling_agent

logger = logging.getLogger(__name__)

def get_employer_orchestrator_agent() -> LlmAgent:
    """Lazy initialization of employer orchestrator."""
    try:
        # Create sub-agents
        review_agent = create_review_agent()
        scheduling_agent = create_scheduling_agent()
        
        return LlmAgent(
            name="EmployerOrchestrator",
            model=config.model,
            description="Orchestrates employer workflow: candidate review → interview scheduling → hiring decisions",
            sub_agents=[review_agent, scheduling_agent],
            instruction="""
You coordinate the employer workflow through specialized agents:

1. Candidate Review: Evaluate submitted candidates
   - Delegate to CandidateReviewAgent to assess candidate submissions
   - Review candidate profiles, GitHub activity, LinkedIn experience
   - Compare candidate skills against job requirements
   - Generate shortlists for interviews

2. Interview Scheduling: Manage interview pipeline
   - Delegate to InterviewSchedulingAgent to coordinate interviews
   - Track candidates through hiring stages (screening, technical, cultural fit)
   - Send interview confirmations and feedback requests
   - Update pipeline status

**Workflow Examples:**

"Review candidates for React Developer role" → Use CandidateReviewAgent
"Schedule technical interview for John Doe" → Use InterviewSchedulingAgent
"Show hiring pipeline status" → Use InterviewSchedulingAgent
"Process new candidate submissions" → Coordinate both agents

**Decision Logic:**
- If user wants to review candidates → Use CandidateReviewAgent
- If user wants to schedule interviews → Use InterviewSchedulingAgent
- If user asks about hiring status → Use InterviewSchedulingAgent
- If user wants full employer workflow → Coordinate both agents

Ensure candidates progress efficiently through the hiring pipeline.
Maintain clear communication with recruiters about candidate status.
""",
            output_key="employer_workflow_result",
        )
    except Exception as e:
        logger.error(f"Failed to initialize employer orchestrator: {e}")
        return LlmAgent(
            name="EmployerOrchestrator",
            model=config.model,
            description="Employer orchestrator (MCP server connection required)",
            instruction="The employer orchestrator requires MCP_SERVER_URL to be configured.",
            output_key="employer_workflow_result",
        )

employer_orchestrator_agent = get_employer_orchestrator_agent()
```

### 3.3 Sub-Agent Mapping

| Supply Chain Agent | Staffing Agent | Primary Responsibility |
|-------------------|----------------|------------------------|
| `inventory_management_agent` | `job_search_agent` | Query job openings from Supabase |
| `purchase_validation_agent` | `candidate_matching_agent` | Match candidates to job requirements |
| `purchase_order_agent` | `submission_agent` | Submit candidates to employers |
| `order_intelligence_agent` | `candidate_review_agent` | Review submitted candidates |
| `production_queue_management_agent` | `interview_scheduling_agent` | Manage interview pipeline |

**TODO:**
- [ ] Create `app/staffing_agents/` directory structure
- [ ] Implement `recruiter_orchestrator_agent/` (replaces buyer orchestrator)
- [ ] Implement `employer_orchestrator_agent/` (replaces supplier orchestrator)
- [ ] Implement `job_search_agent/` (replaces inventory management)
- [ ] Implement `candidate_matching_agent/` (replaces purchase validation)
- [ ] Implement `submission_agent/` (replaces purchase order agent)
- [ ] Implement `candidate_review_agent/` (replaces order intelligence)
- [ ] Implement `interview_scheduling_agent/` (replaces production queue)
- [ ] Update `agent.py` to import staffing orchestrators
- [ ] Update routing logic to support "Recruiter" and "Employer" modes

---

## 🎨 Phase 4: Frontend Integration

### 4.1 Update Mode Selector

**File:** `nextjs/src/components/chat/ChatProvider.tsx`

Add new modes:
```typescript
type AgentMode = "auto" | "planning" | "docs" | "recruiter" | "employer" | "email";
```

### 4.2 Update Agent Routing

**File:** `app/agent.py`

```python
root_agent = LlmAgent(
    name="OrchestrationAgent",
    model=config.model,
    description="Routes user queries to specialized agent clusters",
    instruction=f"""
# ... existing instruction ...

**7. RecruiterOrchestrator**: Staffing agency recruiter workflow
   - Examples: "Find React developer jobs", "Match candidates to this role", "Submit John for Senior Frontend position"
   - Use for: Job search, candidate matching, candidate submissions, recruiter workflows

**8. EmployerOrchestrator**: Client company employer workflow
   - Examples: "Review candidates for DevOps role", "Schedule interview with Jane", "Show hiring pipeline"
   - Use for: Candidate review, interview scheduling, hiring decisions, employer workflows

# ... mode directives ...
- If message starts with "[MODE:RECRUITER]" → IMMEDIATELY delegate to RecruiterOrchestrator
- If message starts with "[MODE:EMPLOYER]" → IMMEDIATELY delegate to EmployerOrchestrator
""",
    sub_agents=[
        # ... existing agents ...
        recruiter_orchestrator_agent,
        employer_orchestrator_agent,
    ],
)
```

### 4.3 Job Search Results Renderer

**File:** `nextjs/src/components/chat/JsonToHtmlRenderer.tsx`

Add renderer for job search results:

```typescript
function renderJobSearchResults(data: any) {
  const jobs = data.jobs || [];
  
  return (
    <div className="space-y-4">
      <h3 className="text-xl font-semibold">
        {data.total_jobs} Job Openings Found
      </h3>
      
      {jobs.map((job: any) => (
        <div key={job.id} className="border rounded-lg p-4 bg-white shadow">
          <h4 className="text-lg font-bold">{job.job_title}</h4>
          <p className="text-sm text-gray-600">{job.location} • {job.remote_type}</p>
          
          <div className="mt-2 flex flex-wrap gap-2">
            {job.tech_stack?.map((tech: string) => (
              <span key={tech} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                {tech}
              </span>
            ))}
          </div>
          
          <div className="mt-3 text-sm">
            <p><strong>Location:</strong> {job.job_location || "Remote"}</p>
            {job.job_min_salary && job.job_max_salary && (
              <p><strong>Salary:</strong> ${parseFloat(job.job_min_salary).toLocaleString()} - ${parseFloat(job.job_max_salary).toLocaleString()}</p>
            )}
            {job.job_apply_link && (
              <p><strong>Apply:</strong> <a href={job.job_apply_link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">View Application</a></p>
            )}
          </div>
          
          <div className="mt-4 flex gap-2">
            <Button
              size="sm"
              onClick={() => handleMatchCandidates(job.id)}
            >
              Find Candidates
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleViewJobDetails(job.id)}
            >
              View Details
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

**TODO:**
- [ ] Add "Recruiter" and "Employer" modes to mode selector
- [ ] Update `ChatProvider` to support new modes
- [ ] Create `renderJobSearchResults` in `JsonToHtmlRenderer`
- [ ] Create `renderCandidateSubmissions` renderer
- [ ] Create `renderHiringPipeline` renderer
- [ ] Add "Find Candidates" and "Submit Candidate" action buttons
- [ ] Style job cards similar to GitHub candidate cards
- [ ] Add urgency badges (critical = red, high = orange, medium = yellow)

---

## 🧪 Phase 5: Testing & Sample Data

### 5.1 Sample Queries

**Recruiter Mode:**
```
- "Find customer service jobs"
- "Show me all remote jobs"
- "Search for jobs in Washington, DC"
- "Find jobs with salary between $40,000 and $60,000"
- "Show me jobs with 'Customer Service' in the title"
- "Match candidates to job opening #42"
- "Submit John Doe for job ID 43"
```

**Employer Mode:**
```
- "Review candidates for our React Developer position"
- "Show hiring pipeline for all open positions"
- "Schedule technical interview with Jane Smith"
- "What's the status of submission SUB-20250120-456789?"
- "Show all candidates in the interviewing stage"
```

### 5.2 Test Data Creation

**Note:** Since you already have thousands of jobs in Supabase, we only need to seed supporting tables.

**Script:** `mcp_server/staffing_backend/seed_test_data.py`

```python
"""
Seed Supabase with test employers, recruiters, and sample submissions.
Job openings already exist in your database.
"""
from supabase import create_client, Client
import os

def seed_employers(supabase: Client):
    """Create sample employer accounts."""
    employers = [
        {
            "company_name": "TechCorp Innovations",
            "industry": "SaaS",
            "contact_name": "Sarah Johnson",
            "contact_email": "sarah@techcorp.com",
            "company_size": "medium"
        },
        {
            "company_name": "Startup Labs",
            "industry": "Fintech",
            "contact_name": "Michael Chen",
            "contact_email": "michael@startuplabs.com",
            "company_size": "startup"
        }
    ]
    
    result = supabase.table("employers").insert(employers).execute()
    return result.data

def seed_recruiters(supabase: Client):
    """Create sample recruiter accounts."""
    recruiters = [
        {
            "name": "Jane Smith",
            "email": "jane@staffingagency.com",
            "agency_name": "Tech Talent Solutions",
            "specializations": ["frontend", "backend", "devops"]
        },
        {
            "name": "Bob Johnson",
            "email": "bob@recruiters.com",
            "agency_name": "Elite Recruiting",
            "specializations": ["fullstack", "mobile"]
        }
    ]
    
    result = supabase.table("recruiters").insert(recruiters).execute()
    return result.data

if __name__ == "__main__":
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    
    print("🌱 Seeding test data...")
    
    # Get a sample job ID from existing jobs
    existing_jobs = supabase.table("job_flow").select("id").limit(1).execute()
    if existing_jobs.data:
        sample_job_id = existing_jobs.data[0]["id"]
        print(f"✅ Found existing job with ID: {sample_job_id}")
    
    employers = seed_employers(supabase)
    print(f"✅ Created {len(employers)} employers")
    
    recruiters = seed_recruiters(supabase)
    print(f"✅ Created {len(recruiters)} recruiters")
    
    print("🎉 Test data seeded successfully!")
    print(f"📊 Your existing job database has thousands of jobs ready to use!")
```

**TODO:**
- [ ] Create `seed_test_data.py` script for supporting tables only
- [ ] Add 20-30 sample employers
- [ ] Add sample recruiters
- [ ] Test job search with your existing job data
- [ ] Test candidate matching workflow using real job IDs
- [ ] Test submission creation with existing job IDs
- [ ] Test hiring pipeline updates
- [ ] Document sample queries using your actual job data

---

## 🚀 Phase 6: Deployment

### 6.1 Environment Variables

**Add to `.env`:**
```env
# Supabase Configuration (Primary Data Source)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here
SUPABASE_ANON_KEY=your-anon-key-here

# JSearch API Configuration (Fallback when Supabase is paused)
JSEARCH_HOST=jsearch.p.rapidapi.com
JSEARCHRAPDKEY=your-rapidapi-key-here

# Staffing MCP Server
STAFFING_MCP_SERVER_URL=https://staffing-mcp-xyz.run.app
```

**Environment Variables Explained:**

#### Supabase (Primary)
- **SUPABASE_URL**: Your Supabase project URL
- **SUPABASE_SERVICE_KEY**: Service role key (bypasses RLS)
- **SUPABASE_ANON_KEY**: Anonymous key (for client-side if needed)

#### JSearch API (Fallback)
- **JSEARCH_HOST**: JSearch API host (default: `jsearch.p.rapidapi.com`)
- **JSEARCHRAPDKEY**: Your RapidAPI key for JSearch
  - Get your key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
  - Free tier: 10 requests/month
  - Paid tiers available for higher limits

**Fallback Behavior:**
1. **Primary**: Always tries Supabase first (your existing database)
2. **Fallback**: If Supabase fails or returns no results, automatically uses JSearch API
3. **Normalization**: JSearch results are normalized to match your Supabase schema
4. **Transparent**: Users don't notice the fallback - same response format

### 6.2 Cloud Run Deployment

**Update Dockerfile:**
```dockerfile
# mcp_server/staffing_backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy staffing backend code
COPY . .

# Expose port 8100
EXPOSE 8100

# Set environment variables
ENV PORT=8100
ENV HOST=0.0.0.0

# Run the MCP server
CMD ["python", "mcpstaffingagent.py"]
```

**Deploy:**
```bash
cd mcp_server/staffing_backend

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/staffing-backend --project YOUR_PROJECT_ID

# Deploy with env vars (including JSearch fallback)
gcloud run deploy staffing-backend \
  --image gcr.io/YOUR_PROJECT_ID/staffing-backend \
  --platform managed \
  --region us-central1 \
  --project YOUR_PROJECT_ID \
  --allow-unauthenticated \
  --port 8100 \
  --set-env-vars "SUPABASE_URL=${SUPABASE_URL},SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY},JSEARCH_HOST=${JSEARCH_HOST},JSEARCHRAPDKEY=${JSEARCHRAPDKEY}"
```

**Note:** The JSearch API fallback ensures job search continues working even if Supabase pauses due to inactivity (common on free tier).

**TODO:**
- [ ] Create `mcp_server/staffing_backend/` directory
- [ ] Create `mcpstaffingagent.py` (main MCP server file)
- [ ] Create `requirements.txt` with Supabase dependencies
- [ ] Create `Dockerfile` for Cloud Run
- [ ] Test locally with Docker
- [ ] Deploy to Cloud Run
- [ ] Update ADK backend to use `STAFFING_MCP_SERVER_URL`
- [ ] Test end-to-end workflow in production

---

## 📊 Phase 7: Advanced Features (Future)

### 7.1 AI-Powered Candidate Matching

- [ ] Implement semantic search using embeddings (OpenAI/Vertex AI)
- [ ] Calculate match scores based on:
  - Technical skills overlap
  - Years of experience alignment
  - Location preferences
  - Salary expectations
  - GitHub activity quality
- [ ] Rank candidates by relevance to job requirements

### 7.2 Automated Candidate Outreach

- [ ] Integrate with existing email generator agent
- [ ] Generate personalized outreach emails to candidates
- [ ] Include job details, match score explanation
- [ ] Track email opens and responses

### 7.3 Interview Scheduling Automation

- [ ] Integrate with Google Calendar API
- [ ] Automatically propose interview slots
- [ ] Send calendar invites to candidates and interviewers
- [ ] Track interview completion and collect feedback

### 7.4 Analytics Dashboard

- [ ] Time-to-fill metrics per job
- [ ] Candidate submission success rates
- [ ] Recruiter performance leaderboard
- [ ] Employer satisfaction scores

---

## 🗓️ Implementation Timeline

| Phase | Estimated Duration | Priority |
|-------|-------------------|----------|
| **Phase 1: Database Migration** | 1 week | 🔴 Critical |
| **Phase 2: MCP Tools Migration** | 2 weeks | 🔴 Critical |
| **Phase 3: Agent Refactoring** | 2 weeks | 🔴 Critical |
| **Phase 4: Frontend Integration** | 1 week | 🟡 High |
| **Phase 5: Testing & Sample Data** | 1 week | 🟡 High |
| **Phase 6: Deployment** | 3 days | 🟡 High |
| **Phase 7: Advanced Features** | 4 weeks | 🟢 Medium |

**Total Core Implementation Time:** ~7 weeks

---

## ✅ Success Criteria

- [x] Supabase database already populated with thousands of job openings ✅
- [ ] MCP server successfully queries existing Supabase jobs table
- [ ] JSearch API fallback works when Supabase is paused/unavailable
- [ ] JSearch results are normalized to match Supabase schema format
- [ ] Recruiter mode can search and filter jobs using existing schema (job_title, job_location, job_min_salary, job_max_salary)
- [ ] Fallback is transparent to users (same response format from both sources)
- [ ] Candidate matching generates match scores
- [ ] Candidate submissions are created and tracked (linked to existing job IDs)
- [ ] Employer mode can review candidates
- [ ] Hiring pipeline updates are reflected in UI
- [ ] Email notifications work for submissions and interviews
- [ ] Cloud Run deployment is stable and performant
- [ ] Sample queries execute in <3 seconds (Supabase) or <5 seconds (JSearch fallback)
- [ ] UI renders job cards using existing fields (title, location, salary, apply link)

---

## 📚 Documentation Requirements

- [ ] Update README with staffing mode documentation
- [ ] Create STAFFING_AGENTS.md explaining architecture
- [ ] Document Supabase schema and relationships
- [ ] Create API reference for staffing MCP tools
- [ ] Write integration guide for recruiters
- [ ] Write integration guide for employers
- [ ] Document sample queries and workflows
- [ ] Create troubleshooting guide
- [ ] Record demo video of recruiter workflow
- [ ] Record demo video of employer workflow

---

## 🎯 Key Differentiators

**What makes this staffing suite unique:**

1. **AI-Powered Matching**: Semantic search + GitHub analysis for candidate-job fit
2. **Multi-Agent Orchestration**: Specialized agents for each workflow stage
3. **Real-Time Pipeline**: Live updates on candidate status across hiring stages
4. **Dual Mode System**: Both recruiter and employer perspectives in one platform
5. **Supabase Integration**: Real-time database with thousands of jobs
6. **Email Automation**: Existing email agent integrates for candidate outreach
7. **Cloud-Native**: Serverless MCP backend, scalable to thousands of jobs/candidates

---

## 🔗 Related Files

- Supply Chain Reference: `app/supply_chain/`
- Recruiter Agents Reference: `app/recruiter_agents/`
- MCP Server Template: `mcp_server/mcppoagent.py`
- Frontend Components: `nextjs/src/components/chat/`
- Agent Routing: `app/agent.py`

---

**Next Steps:**
1. Review this plan with stakeholders
2. Verify Supabase connection and test querying existing `job_flow` table
3. Create additional tables (employers, hiring_pipeline, recruiters)
4. Begin Phase 2: Create MCP tools that work with your existing schema
5. Test job search with your existing job data
6. Test end-to-end workflow with real job IDs

**Schema Notes:**
- ✅ Your existing `job_flow` table is ready to use (id, job_title, job_location, job_apply_link, job_salary, job_min_salary, job_max_salary)
- 📝 Additional tables needed: `employers`, `hiring_pipeline`, `recruiters`
- 🔧 MCP tools will query your existing table structure (no schema changes required)
- 💡 Optional: Add enhancement columns (tech_stack, work_type, etc.) for advanced filtering

**Questions to Answer:**
- How many jobs are currently in your database? (You mentioned "thousands")
- What's the table name in Supabase? (Using `job_flow` - confirmed)
- Do you have a RapidAPI account with JSearch API access? (Free tier: 10 req/month)
- Do you need multi-tenancy (multiple staffing agencies using the platform)?
- Should we migrate existing recruiter agents or keep them separate?
- What's the priority: Recruiter mode or Employer mode first?

**JSearch API Setup:**
1. Sign up at https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Subscribe to a plan (Free tier available for testing)
3. Copy your API key from the RapidAPI dashboard
4. Add `JSEARCHRAPDKEY` to your `.env` file
5. The fallback will automatically activate if Supabase is unavailable

## VERY IMPORTANT
Checking the database schema and tools to understand how `job_opening_id` is created and why it's needed:


## Who creates `job_opening_id`?

**Answer: Jobs are not created by the MCP tools.**

1. The `job_flow` table already exists in Supabase with an `id` column (int8) as the primary key.
2. The `job_search_tool` only reads from `job_flow` — it does not insert new jobs.
3. There is no `create_job` or `insert_job` MCP tool.
4. Jobs must be created manually:
   - Through the Supabase UI
   - Via SQL INSERT statements
   - Through another process/system
   - Imported from external sources

5. JSearch API fallback: When Supabase is unavailable, `search_jobs` can return jobs from JSearch API, but these are not saved to Supabase — they're only returned in the search results.

## Why is `job_opening_id` necessary?

**It links candidate submissions to specific job openings:**

1. Required parameter: `create_candidate_submission` requires `job_opening_id` (see line 32 in `candidate_submission_tool.py`).
2. Data relationship: Links a candidate submission to a specific job in `resume_submissions.job_opening_id`.
3. Pipeline tracking: Enables tracking which job a candidate is being considered for.
4. Filtering and reporting: Allows filtering submissions by job, tracking pipeline status per job, etc.

## The current limitation

The system can search for existing jobs but cannot create new ones. If a user wants to submit a candidate for a job that doesn't exist in `job_flow`, the agent cannot proceed because:
- It can search for jobs (read-only)
- It cannot create jobs (no tool exists)
- It requires `job_opening_id` to create a submission

**Possible solutions:**
1. Add a `create_job` MCP tool to allow creating jobs programmatically.
2. Make `job_opening_id` optional in submissions (allow submissions without linking to a job).
3. Instruct the agent to ask the user to create the job first, or provide the `job_opening_id` if the job already exists.

Should I implement one of these solutions?

Checking the schema and migration files for a foreign key constraint between these tables:


There is a data integrity issue. Findings:

## Current state: no validation

1. No foreign key constraint:
   - Line 6 of `migrate_resume_submissions.sql` states: "job_opening_id is a plain INTEGER (no foreign key) to keep tables independent"
   - The schema does not enforce referential integrity

2. No application-level validation:
   - `candidate_submission_tool.py` does not check if `job_opening_id` exists in `job_flow` before inserting
   - It accepts any integer value

3. Result:
   - You can create a submission with `job_opening_id = 99999` even if that job doesn't exist
   - Orphaned submissions can exist
   - No guarantee that `job_opening_id` in `resume_submissions` references a valid job in `job_flow`

## The problem

```python
# Current code (candidate_submission_tool.py, line 73-74):
if "job_opening_id" in available_columns:
    submission_data["job_opening_id"] = job_opening_id  # No validation!
```

This allows invalid `job_opening_id` values to be inserted.

## Solutions

### Option 1: Add application-level validation (recommended)
Add a validation check in `create_submission` before inserting:

```python
# In candidate_submission_tool.py, before line 98:
# Validate job_opening_id exists in job_flow
if job_opening_id:
    job_check = self.supabase.table("job_flow")\
        .select("id")\
        .eq("id", job_opening_id)\
        .limit(1)\
        .execute()
    
    if not job_check.data or len(job_check.data) == 0:
        return json.dumps({
            "status": "error",
            "message": f"Job opening ID {job_opening_id} does not exist in job_flow table. Please use a valid job ID from search_jobs results.",
            "error_type": "InvalidJobId"
        })
```

### Option 2: Add database foreign key constraint
Add a foreign key at the database level:

```sql
-- Add foreign key constraint
ALTER TABLE resume_submissions 
ADD CONSTRAINT fk_job_opening 
FOREIGN KEY (job_opening_id) 
REFERENCES job_flow(id);
```

Note: This requires that `job_flow.id` and `resume_submissions.job_opening_id` have compatible types (both INTEGER/int8).

### Option 3: Both (most robust)
- Add the foreign key constraint for database-level enforcement
- Add application-level validation for clearer error messages

## Recommendation

Implement Option 1 (application-level validation) first because:
- It provides immediate protection
- It gives clear error messages
- It doesn't require a schema change
- It works even if the foreign key isn't added

Should I implement the validation check?

Checking the code for any validation:


## Direct answer: we don't know for sure

There is no validation. The code does not verify that `job_opening_id` exists in `job_flow` before creating a submission.

### Current code flow:

```python
# Line 73-74 in candidate_submission_tool.py:
if "job_opening_id" in available_columns:
    submission_data["job_opening_id"] = job_opening_id  # ← No validation!

# Line 99:
result = self.supabase.table("resume_submissions").insert(submission_data).execute()
# ← Inserts without checking if job exists
```

### What this means:

- You can create a submission with `job_opening_id = 99999` even if that job doesn't exist
- You can create a submission with `job_opening_id = 0` or any random number
- There's no database foreign key constraint (as noted in the migration file)
- There's no application-level validation check

### The problem:

There is no guarantee that:
- `job_opening_id` in `resume_submissions` references a valid job in `job_flow`
- `submission_number` is linked to a real job opening
- The data relationship is valid

### What should happen:

Before inserting, the code should validate:

```python
# VALIDATION NEEDED (but currently missing):
# 1. Check if job_opening_id exists in job_flow table
# 2. Only then insert the submission
# 3. Return error if job doesn't exist
```

### Current state:

- No database foreign key constraint
- No application-level validation
- No guarantee of data integrity

This is a data integrity gap. The system assumes the `job_opening_id` is valid but does not verify it.

Should I add validation to ensure `job_opening_id` exists in `job_flow` before creating a submission?