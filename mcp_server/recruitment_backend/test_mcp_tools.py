import os
import sys
sys.path.insert(0, '.')

from server import (
    search_candidates_tool,
    scrape_github_profiles_tool,
    get_compensation_data_tool,
    analyze_portfolio_tool,
    get_time_tracking_tool
)

# Test search_candidates_tool
print("Testing search_candidates_tool...")
result = search_candidates_tool(
    job_description="Find Senior React Engineers with TypeScript experience",
    job_title="Senior Frontend Engineer",
    limit=5
)
print(result[:500])  # Print first 500 chars
print("\n✅ search_candidates_tool works!\n")

# Test get_compensation_data_tool
print("Testing get_compensation_data_tool...")
result = get_compensation_data_tool("Senior Software Engineer", "Remote")
print(result[:500])
print("\n✅ get_compensation_data_tool works!\n")

# Test analyze_portfolio_tool (if you have a candidate)
print("Testing analyze_portfolio_tool...")
# Use a GitHub username from your github_profiles_100.json
result = analyze_portfolio_tool("Rowens72")  # Example from your data
print(result[:500])
print("\n✅ analyze_portfolio_tool works!\n")