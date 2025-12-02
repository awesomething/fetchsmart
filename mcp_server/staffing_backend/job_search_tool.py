"""
Job Search Tool - Query job openings from JSearch API with Supabase fallback.
Equivalent to inventory analysis in supply chain.

Fallback Strategy:
1. Try JSearch API first (primary data source)
2. If JSearch API fails or returns no results, fall back to Supabase
3. Normalize JSearch results to match Supabase schema format
"""
from supabase import create_client, Client
import json
import os
import requests
from typing import Optional, List, Dict

class JobSearchTool:
    def __init__(self):
        import logging
        logger = logging.getLogger(__name__)
        
        # PRIORITY 1: Initialize JSearch API credentials (primary data source)
        self.jsearch_host = os.getenv("JSEARCH_HOST", "jsearch.p.rapidapi.com")
        self.jsearch_api_key = os.getenv("JSEARCHRAPDKEY")
        self.jsearch_enabled = bool(self.jsearch_api_key)
        
        if self.jsearch_enabled:
            logger.info(f"[JobSearchTool] ✅ JSearch API enabled (key length: {len(self.jsearch_api_key)})")
        else:
            logger.warning(f"[JobSearchTool] ⚠️  JSearch API disabled: JSEARCHRAPDKEY not set")
        
        # PRIORITY 2: Initialize Supabase client (fallback)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        # Allow server to start even if Supabase is not configured
        # Tools will use JSearch API as primary source
        if supabase_url and supabase_key:
            try:
                self.supabase: Client = create_client(supabase_url, supabase_key)
                self.supabase_enabled = True
                logger.info(f"[JobSearchTool] ✅ Supabase enabled (fallback)")
            except Exception as e:
                logger.warning(f"[JobSearchTool] ⚠️  Supabase initialization failed: {e}")
                logger.info("[JobSearchTool] Server will continue with JSearch API only")
                self.supabase_enabled = False
                self.supabase = None
        else:
            logger.info("[JobSearchTool] Supabase credentials not set. Using JSearch API only.")
            self.supabase_enabled = False
            self.supabase = None
        
        if not self.jsearch_enabled and not self.supabase_enabled:
            error_msg = "CRITICAL: Neither JSEARCHRAPDKEY nor SUPABASE_URL/SUPABASE_SERVICE_KEY is configured. At least one must be set."
            logger.error(f"[JobSearchTool] ❌ {error_msg}")
            raise ValueError(error_msg)
        
        logger.info(f"[JobSearchTool] Initialization complete: JSearch={self.jsearch_enabled}, Supabase={self.supabase_enabled}")
    
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
        Search job openings from JSearch API with Supabase fallback.
        
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
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[JobSearchTool] Starting job search: title='{job_title}', location='{location}', limit={limit}")
        logger.info(f"[JobSearchTool] JSearch enabled: {self.jsearch_enabled}, Supabase enabled: {self.supabase_enabled}")
        
        # PRIORITY 1: Try JSearch API first (primary data source)
        if self.jsearch_enabled:
            try:
                logger.info(f"[JobSearchTool] Attempting JSearch API search...")
                result = self._search_jsearch_api(
                    job_title, location, min_salary, max_salary, remote_only, limit
                )
                
                # If JSearch API returns results, use them immediately
                if result and result.get("total_jobs", 0) > 0:
                    result["data_source"] = "jsearch_api"
                    logger.info(f"[JobSearchTool] ✅ JSearch API success: {result.get('total_jobs')} jobs found")
                    return json.dumps(result)
                
                # If JSearch API returns no results but didn't error, still try fallback
                logger.warning(f"[JobSearchTool] ⚠️  JSearch API returned 0 results, trying Supabase fallback...")
                
            except Exception as e:
                logger.error(f"[JobSearchTool] ❌ JSearch API query failed: {e}", exc_info=True)
                logger.info(f"[JobSearchTool] Attempting Supabase fallback...")
        
        # PRIORITY 2: Fallback to Supabase
        if self.supabase_enabled:
            try:
                logger.info(f"[JobSearchTool] Attempting Supabase search...")
                result = self._search_supabase(
                    job_title, location, min_salary, max_salary, remote_only, limit
                )
                if result and result.get("total_jobs", 0) > 0:
                    result["data_source"] = "supabase"
                    logger.info(f"[JobSearchTool] ✅ Supabase fallback success: {result.get('total_jobs')} jobs found")
                    return json.dumps(result)
                else:
                    logger.warning(f"[JobSearchTool] ⚠️  Supabase returned 0 results")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"[JobSearchTool] ❌ Supabase fallback also failed: {error_msg}", exc_info=True)
                # Log specific error types for better debugging
                if "RLS" in error_msg or "row-level security" in error_msg.lower():
                    logger.error("[JobSearchTool] Supabase RLS policy violation - check service key permissions")
                elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                    logger.error("[JobSearchTool] Supabase connection error - check SUPABASE_URL")
                elif "authentication" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                    logger.error("[JobSearchTool] Supabase authentication error - check SUPABASE_SERVICE_KEY")
        
        # Both sources failed or returned no results
        error_details = []
        if not self.jsearch_enabled:
            error_details.append("JSEARCHRAPDKEY not configured")
        if not self.supabase_enabled:
            error_details.append("SUPABASE_URL or SUPABASE_SERVICE_KEY not configured")
        if self.jsearch_enabled and self.supabase_enabled:
            error_details.append("Both JSearch API and Supabase returned no results or encountered errors")
        
        error_msg = "Job search failed. " + "; ".join(error_details) if error_details else "No job search services available."
        logger.error(f"[JobSearchTool] ❌ {error_msg}")
        
        # Create a detailed error response that the agent can easily parse
        error_response = {
            "status": "error",
            "message": error_msg,
            "total_jobs": 0,
            "jobs": [],
            "error_type": "JobSearchError",
            "error_details": {
                "jsearch_enabled": self.jsearch_enabled,
                "supabase_enabled": self.supabase_enabled,
                "job_title": job_title or "N/A",
                "location": location or "N/A",
                "suggestions": []
            }
        }
        
        # Add actionable suggestions based on what's missing
        if not self.jsearch_enabled and not self.supabase_enabled:
            error_response["error_details"]["suggestions"] = [
                "Set JSEARCHRAPDKEY environment variable for JSearch API access, OR",
                "Set SUPABASE_URL and SUPABASE_SERVICE_KEY for Supabase database access"
            ]
        elif not self.jsearch_enabled:
            error_response["error_details"]["suggestions"] = [
                "JSearch API is not configured. Set JSEARCHRAPDKEY environment variable.",
                "Currently using Supabase only, which may have limited job listings."
            ]
        elif not self.supabase_enabled:
            error_response["error_details"]["suggestions"] = [
                "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY.",
                "Currently using JSearch API only, which may have rate limits."
            ]
        else:
            error_response["error_details"]["suggestions"] = [
                "Both services are configured but returned no results.",
                "Check Cloud Run logs for detailed error messages from JSearch API or Supabase.",
                "Verify that the search query parameters are correct."
            ]
        
        return json.dumps(error_response, indent=2)
    
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
        """Search jobs using JSearch API (RapidAPI) as primary data source."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if not self.jsearch_api_key:
                raise ValueError("JSEARCHRAPDKEY is not configured")
            
            # Build JSearch API query parameters
            # Use a sensible default if no job title provided
            search_query = job_title or "software engineer"
            query_params = {
                "query": search_query,
                "page": "1",
                "num_pages": "1"
            }
            logger.info(f"[JobSearchTool] JSearch API query: '{search_query}'")
            
            # Add location filter (empty string means no location filter)
            # Normalize common location formats for JSearch API
            if location and location.strip():
                # Normalize location names
                location_normalized = location.strip()
                # Map common abbreviations to full names
                location_map = {
                    "u.s.": "United States",
                    "us": "United States",
                    "usa": "United States",
                    "u.s.a.": "United States",
                    "united states": "United States"
                }
                location_lower = location_normalized.lower()
                if location_lower in location_map:
                    location_normalized = location_map[location_lower]
                
                query_params["location"] = location_normalized
                logger.info(f"[JobSearchTool] Using location: '{location_normalized}' (normalized from '{location}')")
            elif remote_only:
                query_params["remote_jobs_only"] = "true"
                logger.info(f"[JobSearchTool] Searching for remote jobs only")
            
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
            
            logger.info(f"[JobSearchTool] Calling JSearch API: {url} with query='{query_params.get('query')}', location='{query_params.get('location', 'N/A')}'")
            
            response = requests.get(url, headers=headers, params=query_params, timeout=15)
            
            # Log response status
            logger.info(f"[JobSearchTool] JSearch API response status: {response.status_code}")
            
            # Handle different HTTP status codes
            if response.status_code == 401:
                raise Exception("JSearch API authentication failed. Check JSEARCHRAPDKEY.")
            elif response.status_code == 429:
                raise Exception("JSearch API rate limit exceeded. Please try again later.")
            elif response.status_code == 403:
                raise Exception("JSearch API access forbidden. Check API key permissions.")
            
            response.raise_for_status()
            
            data = response.json()
            
            # Check if API returned data
            if not data or "data" not in data:
                logger.warning(f"[JobSearchTool] JSearch API returned unexpected format: {data}")
                return {
                    "status": "success",
                    "total_jobs": 0,
                    "jobs": [],
                    "filters_applied": {
                        "job_title": job_title,
                        "location": location,
                        "remote_only": remote_only,
                        "min_salary": min_salary,
                        "max_salary": max_salary
                    }
                }
            
            # Normalize JSearch results to match Supabase schema
            jobs = []
            raw_jobs = data.get("data", [])
            logger.info(f"[JobSearchTool] JSearch API returned {len(raw_jobs)} raw jobs, normalizing...")
            
            for job in raw_jobs[:limit]:
                normalized_job = self._normalize_jsearch_result(job)
                if normalized_job:
                    jobs.append(normalized_job)
            
            logger.info(f"[JobSearchTool] Successfully normalized {len(jobs)} jobs from JSearch API")
            
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
            
        except requests.exceptions.Timeout:
            raise Exception("JSearch API request timed out. The service may be slow or unavailable.")
        except requests.exceptions.ConnectionError:
            raise Exception("JSearch API connection failed. Check your internet connection.")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"JSearch API HTTP error ({e.response.status_code}): {str(e)}")
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

