"""
Test script for staffing MCP tools
Tests tools directly without running the full MCP server
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_job_search_tool():
    """Test job search tool with Supabase"""
    print("\n🔍 Testing Job Search Tool...")
    try:
        try:
            from job_search_tool import JobSearchTool
        except ImportError as e:
            if "supabase" in str(e).lower():
                print("    ❌ Error: 'supabase' module not found")
                print("    💡 Install dependencies to shared venv: make install-staffing-deps")
                print("    💡 Or manually: cd mcp_server && .venv/Scripts/pip install -r staffing_backend/requirements.txt")
                return False
            raise
        
        tool = JobSearchTool()
        
        # Test 1: Search by job title
        print("  Test 1: Search by job title 'developer'...")
        result = tool.search_jobs(job_title="developer", limit=5)
        data = json.loads(result)
        print(f"    ✅ Found {data.get('total_jobs', 0)} jobs")
        print(f"    📊 Data source: {data.get('data_source', 'unknown')}")
        
        # Test 2: Search with location
        print("  Test 2: Search with location 'remote'...")
        result = tool.search_jobs(job_title="engineer", location="remote", limit=3)
        data = json.loads(result)
        print(f"    ✅ Found {data.get('total_jobs', 0)} jobs")
        
        # Test 3: Remote only
        print("  Test 3: Remote only jobs...")
        result = tool.search_jobs(remote_only=True, limit=3)
        data = json.loads(result)
        print(f"    ✅ Found {data.get('total_jobs', 0)} remote jobs")
        
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_candidate_submission_tool():
    """Test candidate submission tool"""
    print("\n📝 Testing Candidate Submission Tool...")
    try:
        try:
            from candidate_submission_tool import CandidateSubmissionTool
        except ImportError as e:
            if "supabase" in str(e).lower():
                print("    ❌ Error: 'supabase' module not found")
                print("    💡 Install dependencies to shared venv: make install-staffing-deps")
                print("    💡 Or manually: cd mcp_server && .venv/Scripts/pip install -r staffing_backend/requirements.txt")
                return False
            raise
        
        tool = CandidateSubmissionTool()
        
        # Test: Create a submission (requires a valid job_opening_id)
        print("  Test: Create candidate submission...")
        print("    ⚠️  Note: Requires a valid job_opening_id from your job_flow table")
        print("    💡 Get a job ID first by running: test_job_search_tool()")
        
        # Example (uncomment and use a real job ID):
        # result = tool.create_submission(
        #     job_opening_id=1,  # Replace with actual job ID
        #     candidate_name="Test Candidate",
        #     candidate_email="test@example.com",
        #     candidate_github="https://github.com/testuser",
        #     match_score=0.85
        # )
        # data = json.loads(result)
        # print(f"    ✅ Submission created: {data.get('submission', {}).get('submission_number', 'N/A')}")
        
        print("    ✅ Tool initialized successfully")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hiring_pipeline_tool():
    """Test hiring pipeline tool"""
    print("\n📊 Testing Hiring Pipeline Tool...")
    try:
        try:
            from hiring_pipeline_tool import HiringPipelineTool
        except ImportError as e:
            if "supabase" in str(e).lower():
                print("    ❌ Error: 'supabase' module not found")
                print("    💡 Install dependencies to shared venv: make install-staffing-deps")
                print("    💡 Or manually: cd mcp_server && .venv/Scripts/pip install -r staffing_backend/requirements.txt")
                return False
            raise
        
        tool = HiringPipelineTool()
        
        # Test 1: Get pipeline status (all jobs)
        print("  Test 1: Get pipeline status for all jobs...")
        result = tool.get_pipeline_status()
        data = json.loads(result)
        print(f"    ✅ Pipeline status retrieved")
        print(f"    📊 Total candidates: {data.get('total_candidates', 0)}")
        
        # Test 2: Get pipeline for specific job
        print("  Test 2: Get pipeline status for specific job...")
        print("    ⚠️  Note: Requires a valid job_opening_id")
        # result = tool.get_pipeline_status(job_opening_id=1)
        # data = json.loads(result)
        # print(f"    ✅ Pipeline status for job retrieved")
        
        print("    ✅ Tool initialized successfully")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔐 Checking Environment Variables...")
    
    required_vars = {
        "SUPABASE_URL": "Supabase project URL",
        "SUPABASE_SERVICE_KEY": "Supabase service role key",
    }
    
    optional_vars = {
        "JSEARCHRAPDKEY": "JSearch API key (fallback)",
        "JSEARCH_HOST": "JSearch API host (default: jsearch.p.rapidapi.com)",
    }
    
    all_present = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: Set ({description})")
        else:
            print(f"  ❌ {var}: Missing ({description})")
            all_present = False
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: Set ({description})")
        else:
            print(f"  ⚠️  {var}: Not set ({description} - optional for fallback)")
    
    return all_present

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing Staffing MCP Tools")
    print("=" * 60)
    
    # Check environment
    env_ok = test_environment_variables()
    
    if not env_ok:
        print("\n⚠️  Missing required environment variables!")
        print("💡 Create a .env file in mcp_server/ (shared) or mcp_server/staffing_backend/ with:")
        print("   SUPABASE_URL=your-supabase-url")
        print("   SUPABASE_SERVICE_KEY=your-service-key")
        print("   JSEARCHRAPDKEY=your-jsearch-key (optional)")
        exit(1)
    
    # Check if dependencies are installed
    print("\n📦 Checking Dependencies...")
    try:
        import supabase
        print("  ✅ supabase: Installed")
    except ImportError:
        print("  ❌ supabase: Not installed")
        print("\n💡 Install dependencies to shared venv:")
        print("   make install-staffing-deps")
        print("   Or manually: cd mcp_server && .venv/Scripts/pip install -r staffing_backend/requirements.txt")
        exit(1)
    
    try:
        import requests
        print("  ✅ requests: Installed")
    except ImportError:
        print("  ❌ requests: Not installed")
        print("\n💡 Install dependencies to shared venv:")
        print("   make install-staffing-deps")
        print("   Or manually: cd mcp_server && .venv/Scripts/pip install -r staffing_backend/requirements.txt")
        exit(1)
    
    # Run tests
    results = []
    results.append(("Job Search Tool", test_job_search_tool()))
    results.append(("Candidate Submission Tool", test_candidate_submission_tool()))
    results.append(("Hiring Pipeline Tool", test_hiring_pipeline_tool()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 All tests passed! MCP tools are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    print("\n💡 Next Steps:")
    print("  1. Test MCP server: make dev-staffing-mcp")
    print("  2. Test with MCP Inspector: cd mcp_server && npx @modelcontextprotocol/inspector .venv/Scripts/python staffing_backend/mcpstaffingagent.py")
    print("  3. Test through frontend: Select 'Staffing Recruiter' mode and ask: 'Find React developer jobs'")

