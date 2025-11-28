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
        
        # Allow server to start even if Supabase is not configured
        # Tools will use JSearch API fallback
        if supabase_url and supabase_key:
            try:
                self.supabase: Client = create_client(supabase_url, supabase_key)
                self.supabase_enabled = True
            except Exception as e:
                print(f"[WARNING] Supabase initialization failed: {e}")
                print("[INFO] Server will continue with JSearch API fallback only")
                self.supabase_enabled = False
                self.supabase = None
        else:
            print("[INFO] Supabase credentials not set. Using JSearch API fallback only.")
            self.supabase_enabled = False
            self.supabase = None
        
        # Initialize JSearch API credentials (fallback)
        self.jsearch_host = os.getenv("JSEARCH_HOST", "jsearch.p.rapidapi.com")
        self.jsearch_api_key = os.getenv("JSEARCHRAPDKEY")
        self.jsearch_enabled = bool(self.jsearch_api_key)
        
        if not self.supabase_enabled and not self.jsearch_enabled:
            raise ValueError("Either SUPABASE_URL/SUPABASE_SERVICE_KEY or JSEARCHRAPDKEY must be configured")
    
    def search_jobs(
        self,
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
        location: str = "",
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
            
            # Filter by location (empty string means no location filter)
            # If location is provided and not empty, filter by location
            if location and location.strip():
                query = query.ilike("job_location", f"%{location}%")
            
            # Filter for remote jobs only (job_location IS NULL)
            # Note: remote_only takes precedence over location filter
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
                    
                    # Skip jobs with no salary information if both filters are specified
                    if min_sal is None and max_sal is None:
                        if min_salary is not None and max_salary is not None:
                            continue  # Both filters specified, skip jobs without salary
                        # If only one filter is specified, include jobs without salary
                        # (user can decide if they want jobs without salary info)
                    
                    # Apply salary range filters
                    # Job is included if its salary range overlaps with the requested range
                    # (i.e., job's range intersects with requested range)
                    include_job = True
                    
                    if min_salary is not None:
                        # Job's max salary must be >= requested min salary
                        if max_sal is not None and max_sal < min_salary:
                            include_job = False
                        # If job only has min_sal, we can't verify it meets min_salary requirement
                        # So we include it (let user see it)
                    
                    if max_salary is not None:
                        # Job's min salary must be <= requested max salary
                        if min_sal is not None and min_sal > max_salary:
                            include_job = False
                        # If job only has max_sal, we can't verify it meets max_salary requirement
                        # So we include it (let user see it)
                    
                    if include_job:
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
        location: str = "",
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
            
            # Add location filter (empty string means no location filter)
            if location and location.strip():
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

