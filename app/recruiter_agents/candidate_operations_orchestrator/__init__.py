"""
Recruiter Email Loop Agent

This package now exposes a SequentialAgent + LoopAgent workflow that focuses on
delivering production-ready recruitment outreach emails.

Architecture:
- Step 1: Email Generator (LlmAgent) – produces the initial draft once a JD exists
- Step 2: Email Refinement Loop (LoopAgent)
    - Email Reviewer (LlmAgent) – checks tone, personalization, CTA, correctness
    - Email Refiner (LlmAgent + GitHub profile lookup tool) – applies feedback and
      enriches the copy with repository/skill highlights

Highlights:
- Enforces the presence of a job description before drafting
- Iteratively improves copy until the reviewer calls `exit_loop`
- Reads local `github_profiles_100.json` to ground personalization
- Returns a final email body ready for the recruiter handoff

Usage:
Run this agent on port 8102 to provide `[MODE:EMAIL]` support inside the root orchestrator.
"""

