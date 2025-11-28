"""Test Supabase connection and job search"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

print("Testing Supabase Connection...")
print("=" * 60)

# Check environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url:
    print("ERROR: SUPABASE_URL not set")
    exit(1)
if not supabase_key:
    print("ERROR: SUPABASE_SERVICE_KEY not set")
    exit(1)

print(f"SUPABASE_URL: {supabase_url[:30]}...")
print(f"SUPABASE_SERVICE_KEY: {supabase_key[:20]}...")

# Test connection
try:
    from supabase import create_client
    supabase = create_client(supabase_url, supabase_key)
    print("SUCCESS: Supabase client created")
    
    # Test query
    print("\nTesting query to job_flow table...")
    result = supabase.table("job_flow").select("id, job_title, job_location").limit(5).execute()
    
    print(f"SUCCESS: Query successful!")
    print(f"Found {len(result.data)} jobs")
    
    if result.data:
        print("\nSample jobs:")
        for job in result.data[:3]:
            title = job.get("job_title", "N/A")
            location = job.get("job_location") or "Remote"
            print(f"  - ID: {job.get('id')}, Title: {title}, Location: {location}")
    else:
        print("WARNING: No jobs found in database (table might be empty)")
        
except Exception as e:
    print(f"ERROR: Supabase connection failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test Job Search Tool
print("\n" + "=" * 60)
print("Testing Job Search Tool...")
print("=" * 60)

try:
    from job_search_tool import JobSearchTool
    tool = JobSearchTool()
    print("SUCCESS: JobSearchTool initialized")
    
    # Test search
    print("\nTesting job search: 'react'...")
    result = tool.search_jobs(job_title="react", limit=3)
    
    data = json.loads(result)
    print(f"SUCCESS: Search completed!")
    print(f"Status: {data.get('status')}")
    print(f"Total jobs: {data.get('total_jobs', 0)}")
    print(f"Data source: {data.get('data_source', 'unknown')}")
    
    if data.get("jobs"):
        print(f"\nFound {len(data['jobs'])} jobs:")
        for job in data["jobs"][:3]:
            title = job.get("job_title", "N/A")
            location = job.get("job_location") or "Remote"
            print(f"  - {title} at {location}")
    else:
        print("WARNING: No jobs found")
        
except Exception as e:
    print(f"ERROR: Job search test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)

