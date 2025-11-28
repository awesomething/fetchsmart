"""Quick test script for the mock recruitment service"""
import json
from recruitment_service import recruitment_service

def test_mock_service():
    """Test all the mock service endpoints"""
    print("=" * 60)
    print("TESTING MOCK RECRUITMENT SERVICE")
    print("=" * 60)
    
    # Test 1: Candidate Pipeline
    print("\n1️⃣ Testing Candidate Pipeline Query...")
    result = recruitment_service.handle_query("Show me the candidate pipeline")
    data = json.loads(result)
    print(f"✅ Total Candidates: {data['total_candidates']}")
    print(f"✅ By Source: {data['by_source']}")
    
    # Test 2: Compensation Data
    print("\n2️⃣ Testing Compensation Query...")
    result = recruitment_service.handle_query("What's the salary for Senior Software Engineer?")
    data = json.loads(result)
    print(f"✅ Role: {data['role']}")
    print(f"✅ Recommended Range: {data['recommended_range']}")
    print(f"✅ Market Data (p50): ${data['market_data']['p50']:,}")
    
    # Test 3: Candidate Profiles
    print("\n3️⃣ Testing Candidate Profile Query...")
    result = recruitment_service.handle_query("Show me candidate skills")
    data = json.loads(result)
    print(f"✅ Total Reviewed: {data.get('total_reviewed', 'N/A')}")
    print(f"✅ Top Matches: {len(data['top_matches'])}")
    if data['top_matches']:
        top = data['top_matches'][0]
        print(f"   - {top['name']}: {top['role']} ({top['experience_years']}yrs)")
        print(f"   - GitHub: {top['github_profile']} ({top['github_repos']} repos, {top['github_stars']} stars)")
    
    # Test 4: Hiring Goals
    print("\n4️⃣ Testing Hiring Goals Query...")
    result = recruitment_service.handle_query("Show hiring goals progress")
    data = json.loads(result)
    print(f"✅ Quarterly Target: {data['quarterly_target']}")
    print(f"✅ Hired This Quarter: {data['hired_this_quarter']}")
    print(f"✅ Progress: {data['progress']}")
    
    # Test 5: Market Insights
    print("\n5️⃣ Testing Market Insights Query...")
    result = recruitment_service.handle_query("What are the market trends?")
    data = json.loads(result)
    print(f"✅ Market Conditions: {data['market_conditions']}")
    print(f"✅ Top Sourcing Channels: {data['competitor_intelligence']['top_sourcing_channels']}")
    
    # Test 6: Time Tracking
    print("\n6️⃣ Testing Time Tracking Query...")
    result = recruitment_service.handle_query("Show my time tracking data")
    data = json.loads(result)
    print(f"✅ Recruiter: {data['recruiter_name']}")
    print(f"✅ Total Hours: {data['total_hours']}")
    print(f"✅ Top Activity: GitHub Research - {data['activity_breakdown']['GitHub Research']['hours']} hours ({data['activity_breakdown']['GitHub Research']['percentage']})")
    
    # Test 7: General Info
    print("\n7️⃣ Testing General Info Query...")
    result = recruitment_service.handle_query("Hello")
    data = json.loads(result)
    print(f"✅ System Status: {data['system_status']}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n📋 Summary:")
    print(f"   - Mock service is working correctly")
    print(f"   - {data['total_candidates']} tech candidates generated")
    print(f"   - {data['total_jobs']} job postings available")
    print(f"   - {data['total_applications']} applications tracked")
    print(f"   - GitHub-focused sourcing data included")
    print(f"   - Time tracking analytics available")
    print("\n🚀 Ready to start the A2A server!")
    print("   Run: python server.py")
    print()

if __name__ == "__main__":
    test_mock_service()

