"""
Simple test script that tests MCP tools without requiring full server startup.
This avoids needing google-adk installed just to test the tool functions.
"""
import os
import sys
import json

# Add current directory to path
sys.path.insert(0, '.')

# Import only what we need (without ADK dependencies)
from recruitment_service import recruitment_service
from candidate_matcher import CandidateMatcher

# Initialize matcher
matcher = CandidateMatcher()

def test_search_candidates_tool():
    """Test search_candidates_tool logic"""
    print("Testing search_candidates_tool logic...")
    try:
        candidates = recruitment_service.candidates
        results = matcher.match_candidates(
            candidates=candidates,
            job_description="Find Senior React Engineers with TypeScript experience",
            job_title="Senior Frontend Engineer",
            limit=5
        )
        
        # Format response (same as in server.py)
        response = {
            "query": "Find Senior React Engineers with TypeScript experience",
            "total_matches": results['total_matches'],
            "showing_top": results['showing'],
            "top_candidates": []
        }
        
        for match in results['top_candidates']:
            candidate = match['candidate']
            likely_roles = candidate.get('likely_roles') or []
            role = likely_roles[0] if likely_roles else 'Software Engineer'
            candidate_id = candidate.get('id') or candidate.get('github_username') or 'unknown'
            
            response['top_candidates'].append({
                "id": candidate_id,
                "name": candidate.get('name') or candidate.get('github_username', 'Unknown'),
                "github_username": candidate.get('github_username', ''),
                "role": role,
                "experience_level": candidate.get('estimated_experience_level', 'Mid'),
                "match_score": match.get('match_score', 0),
                "match_reasons": match.get('match_reasons', [])[:3],  # First 3 reasons
            })
        
        print(f"✅ Found {len(response['top_candidates'])} candidates")
        print(f"Top candidate: {response['top_candidates'][0]['name']} (Score: {response['top_candidates'][0]['match_score']})")
        print(json.dumps(response, indent=2)[:500])
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analyze_portfolio_tool():
    """Test analyze_portfolio_tool logic"""
    print("\nTesting analyze_portfolio_tool logic...")
    try:
        candidates = recruitment_service.candidates
        github_username = "filipedeschamps"
        github_username_lower = github_username.lower()
        
        candidate = next(
            (c for c in candidates if c.get('github_username', '').lower() == github_username_lower),
            None
        )
        
        if not candidate:
            available_usernames = [c.get('github_username', 'N/A') for c in candidates[:10]]
            print(f"❌ Candidate {github_username} not found")
            print(f"Available samples: {available_usernames}")
            return False
        
        # Build analysis
        analysis = {
            "github_username": github_username,
            "name": candidate.get('name'),
            "primary_language": candidate.get('primary_language'),
            "languages": candidate.get('languages', []),
            "github_stats": {
                "repos": candidate.get('public_repos', 0),
                "stars": candidate.get('total_stars', 0),
                "followers": candidate.get('followers', 0),
            },
            "experience_level": candidate.get('estimated_experience_level'),
        }
        
        print(f"✅ Found candidate: {analysis['name']}")
        print(f"   Language: {analysis['primary_language']}")
        print(f"   Stats: {analysis['github_stats']['repos']} repos, {analysis['github_stats']['stars']} stars")
        print(json.dumps(analysis, indent=2)[:500])
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compensation_tool():
    """Test compensation data"""
    print("\nTesting get_compensation_data_tool logic...")
    try:
        result = recruitment_service._get_compensation_data()
        print("✅ Compensation data retrieved")
        print(result[:500])
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing MCP Tools (Simple Version - No ADK Required)\n")
    print("=" * 60)
    
    results = []
    results.append(("search_candidates_tool", test_search_candidates_tool()))
    results.append(("analyze_portfolio_tool", test_analyze_portfolio_tool()))
    results.append(("compensation_tool", test_compensation_tool()))
    
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

