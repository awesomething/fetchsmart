from typing import Dict, Any
import json
from datetime import datetime, timedelta
import random
import os

# Import the intelligent matcher
try:
    from candidate_matcher import CandidateMatcher
    MATCHER_AVAILABLE = True
except ImportError:
    MATCHER_AVAILABLE = False
    print("[WARN] CandidateMatcher not available. Install or check candidate_matcher.py")

class MockRecruitmentService:
    """Mock recruitment data service for development"""
    
    def __init__(self):
        # Try to load real GitHub profiles, fallback to mock data
        self.candidates = self._load_candidates()
        self.jobs = self._generate_mock_jobs()
        self.applications = self._generate_mock_applications()
        
        # Initialize matcher if available
        if MATCHER_AVAILABLE:
            self.matcher = CandidateMatcher()
            print("[OK] Intelligent candidate matcher initialized")
        else:
            self.matcher = None
            print("[WARN] Using basic search (matcher not available)")
    
    def handle_query(self, query: str) -> str:
        """Route queries to appropriate handler"""
        query_lower = query.lower()
        
        # INTELLIGENT SEARCH - Job-based candidate search
        if any(keyword in query_lower for keyword in ["search for", "find candidates", "looking for", "need a", "hire a"]):
            return self._search_candidates_by_job(query)
        
        # Candidate sourcing queries
        elif "pipeline" in query_lower or "sourcing" in query_lower or "candidates" in query_lower:
            return self._get_candidate_pipeline()
        
        # Compensation queries
        elif "salary" in query_lower or "compensation" in query_lower or "offer" in query_lower:
            return self._get_compensation_data()
        
        # Candidate portfolio queries
        elif "resume" in query_lower or "skills" in query_lower or "qualifications" in query_lower:
            return self._get_candidate_profiles()
        
        # Goals queries
        elif "goals" in query_lower or "target" in query_lower or "hiring" in query_lower:
            return self._get_hiring_goals()
        
        # Market insights queries  
        elif "market" in query_lower or "trends" in query_lower or "insights" in query_lower:
            return self._get_market_insights()
        
        # Time tracking / productivity queries
        elif "time" in query_lower or "productivity" in query_lower or "hours" in query_lower or "tracking" in query_lower:
            return self._get_time_tracking_data()
        
        else:
            return self._get_general_info()
    
    def _load_candidates(self) -> list:
        """Load real GitHub profiles if available, otherwise generate mock data"""
        json_path = os.path.join(os.path.dirname(__file__), 'github_profiles_100.json')
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                print(f"[OK] Loaded {len(profiles)} real GitHub profiles from {json_path}")
                return profiles
            except Exception as e:
                print(f"[WARN] Error loading GitHub profiles: {e}")
                print("   Falling back to mock data")
                return self._generate_mock_candidates()
        else:
            print(f"[INFO] No GitHub profiles found at {json_path}")
            print("   Using mock data. Run github_scraper.py to collect real profiles.")
            return self._generate_mock_candidates()
    
    def _search_candidates_by_job(self, query: str) -> str:
        """
        Intelligent search for candidates based on job requirements.
        This is the CORE MVP feature.
        """
        if not self.matcher:
            # Fallback to simple keyword search if matcher not available
            return self._simple_candidate_search(query)
        
        try:
            # Use intelligent matcher
            results = self.matcher.match_candidates(
                candidates=self.candidates,
                job_description=query,
                limit=8
            )
            
            # Format results for agent consumption
            response = {
                "query": query,
                "total_matches": results['total_matches'],
                "showing_top": results['showing'],
                "requirements_detected": results['requirements'],
                "top_candidates": []
            }
            
            for match in results['top_candidates']:
                candidate = match['candidate']
                response['top_candidates'].append({
                    "id": candidate.get('id', candidate.get('github_username')),
                    "name": candidate.get('name'),
                    "github_username": candidate.get('github_username'),
                    "github_profile_url": candidate.get('github_profile_url'),
                    "avatar_url": candidate.get('avatar_url'),
                    "role": candidate.get('likely_roles', ['Software Engineer'])[0] if candidate.get('likely_roles') else 'Software Engineer',
                    "experience_level": candidate.get('estimated_experience_level'),
                    "location": candidate.get('location'),
                    "primary_language": candidate.get('primary_language'),
                    "skills": candidate.get('skills', [])[:8],  # Top 8 skills
                    "languages": candidate.get('languages', [])[:5],
                    "github_stats": {
                        "repos": candidate.get('public_repos'),
                        "stars": candidate.get('total_stars'),
                        "followers": candidate.get('followers'),
                    },
                    "notable_repos": candidate.get('notable_repos', [])[:3],
                    "bio": candidate.get('bio', ''),
                    "match_score": match['match_score'],
                    "match_reasons": match['match_reasons'],
                    "matched_skills": match['matched_skills'],
                    "is_open_source_contributor": candidate.get('open_source_contributor', False),
                    "has_popular_repos": candidate.get('has_popular_repos', False),
                })
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            print(f"Error in intelligent search: {e}")
            return self._simple_candidate_search(query)
    
    def _simple_candidate_search(self, query: str) -> str:
        """Fallback simple search if matcher not available"""
        # Simple keyword matching
        query_words = set(query.lower().split())
        scored = []
        
        for candidate in self.candidates:
            score = 0
            candidate_text = " ".join([
                candidate.get('primary_language', ''),
                " ".join(candidate.get('skills', [])),
                " ".join(candidate.get('languages', [])),
                candidate.get('bio', '')
            ]).lower()
            
            for word in query_words:
                if word in candidate_text:
                    score += 1
            
            if score > 0:
                scored.append((score, candidate))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        top_candidates = [c[1] for c in scored[:8]]
        
        return json.dumps({
            "query": query,
            "total_matches": len(scored),
            "showing_top": len(top_candidates),
            "top_candidates": top_candidates
        }, indent=2)
    
    def _generate_mock_candidates(self) -> list:
        """Generate mock tech candidates with real GitHub profiles"""
        # Real GitHub profiles to showcase on sourcing page - updated from ChatContainer.tsx
        featured_profiles = [
            {
                "id": "CAND-001",
                "name": "awesomething",
                "email": "awesomething@github.com",
                "role": "Senior Software Engineer",
                "experience_years": 8,
                "source": "GitHub",
                "status": "Screening",
                "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "MCP"],
                "applied_date": (datetime.now() - timedelta(days=5)).isoformat(),
                "location": "Remote - US",
                "github_profile": "https://github.com/awesomething",
                "github_profile_url": "https://github.com/awesomething",
                "github_username": "awesomething",
                "public_repos": 342,
                "github_repos": 342,
                "total_stars": 285,
                "github_stars": 285,
                "followers": 27,
                "github_contributions": 3421,
                "coding_assessment_score": 92,
                "system_design_level": "Senior",
                "open_source_contributor": True,
                "avatar_url": "https://avatars.githubusercontent.com/awesomething",
                "primary_language": "Python",
                "languages": ["Python", "JavaScript", "React"],
            },
            {
                "id": "CAND-002",
                "name": "Mithonmasud",
                "email": "mithonmasud@github.com",
                "role": "Full Stack Engineer",
                "experience_years": 6,
                "source": "GitHub",
                "status": "Technical Interview",
                "skills": ["TypeScript", "React", "Node.js", "GraphQL", "PostgreSQL"],
                "applied_date": (datetime.now() - timedelta(days=12)).isoformat(),
                "location": "San Francisco, CA",
                "github_profile": "https://github.com/Mithonmasud",
                "github_profile_url": "https://github.com/Mithonmasud",
                "github_username": "Mithonmasud",
                "public_repos": 38,
                "github_repos": 38,
                "total_stars": 156,
                "github_stars": 156,
                "followers": 892,
                "github_contributions": 2156,
                "coding_assessment_score": 88,
                "system_design_level": "Mid",
                "open_source_contributor": True,
                "avatar_url": "https://avatars.githubusercontent.com/Mithonmasud",
                "primary_language": "TypeScript",
                "languages": ["TypeScript", "React", "Node.js"],
            },
            {
                "id": "CAND-003",
                "name": "Marquish",
                "email": "marquish@github.com",
                "role": "Backend Engineer",
                "experience_years": 7,
                "source": "GitHub",
                "status": "System Design",
                "skills": ["Go", "Rust", "Kubernetes", "Docker", "Microservices"],
                "applied_date": (datetime.now() - timedelta(days=8)).isoformat(),
                "location": "Austin, TX",
                "github_profile": "https://github.com/Marquish",
                "github_profile_url": "https://github.com/Marquish",
                "github_username": "Marquish",
                "public_repos": 29,
                "github_repos": 29,
                "total_stars": 412,
                "github_stars": 412,
                "followers": 1589,
                "github_contributions": 4123,
                "coding_assessment_score": 95,
                "system_design_level": "Senior",
                "open_source_contributor": True,
                "avatar_url": "https://avatars.githubusercontent.com/Marquish",
                "primary_language": "Go",
                "languages": ["Go", "Rust"],
            },
            {
                "id": "CAND-004",
                "name": "Ekeneakubue",
                "email": "ekeneakubue@github.com",
                "role": "DevOps Engineer",
                "experience_years": 5,
                "source": "GitHub",
                "status": "Applied",
                "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "Python"],
                "applied_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "location": "Remote - Global",
                "github_profile": "https://github.com/Ekeneakubue",
                "github_profile_url": "https://github.com/Ekeneakubue",
                "github_username": "Ekeneakubue",
                "public_repos": 31,
                "github_repos": 31,
                "total_stars": 198,
                "github_stars": 198,
                "followers": 743,
                "github_contributions": 1876,
                "coding_assessment_score": 86,
                "system_design_level": "Mid",
                "open_source_contributor": True,
                "avatar_url": "https://avatars.githubusercontent.com/Ekeneakubue",
                "primary_language": "AWS",
                "languages": ["Python", "Terraform"],
            },
            {
                "id": "CAND-005",
                "name": "Sarah Chen",
                "email": "sarahchen@github.com",
                "role": "Frontend Engineer",
                "experience_years": 4,
                "source": "GitHub",
                "status": "Screening",
                "skills": ["React", "Vue.js", "TypeScript", "CSS", "Webpack"],
                "applied_date": (datetime.now() - timedelta(days=15)).isoformat(),
                "location": "Seattle, WA",
                "github_profile": "https://github.com/sarahchen",
                "github_profile_url": "https://github.com/sarahchen",
                "github_username": "sarahchen",
                "public_repos": 52,
                "github_repos": 52,
                "total_stars": 324,
                "github_stars": 324,
                "followers": 567,
                "github_contributions": 2890,
                "coding_assessment_score": 84,
                "system_design_level": "Mid",
                "open_source_contributor": True,
                "avatar_url": "https://avatars.githubusercontent.com/sarahchen",
                "primary_language": "JavaScript",
                "languages": ["JavaScript", "TypeScript", "React"],
            },
            {
                "id": "CAND-006",
                "name": "Michael Kerr",
                "email": "olafaloofian@github.com",
                "role": "Senior Full Stack Engineer",
                "experience_years": 10,
                "source": "GitHub",
                "status": "Technical Interview",
                "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes"],
                "applied_date": (datetime.now() - timedelta(days=20)).isoformat(),
                "location": "Remote - US",
                "github_profile": "https://github.com/Olafaloofian",
                "github_profile_url": "https://github.com/Olafaloofian",
                "github_username": "Olafaloofian",
                "public_repos": 106,
                "github_repos": 106,
                "total_stars": 285,
                "github_stars": 285,
                "followers": 58,
                "github_contributions": 3421,
                "coding_assessment_score": 87,
                "system_design_level": "Senior",
                "open_source_contributor": True,
                "avatar_url": "https://avatars.githubusercontent.com/Olafaloofian",
                "primary_language": "Python",
                "languages": ["Python", "JavaScript", "React"],
            },
            {
                "id": "CAND-007",
                "name": "xiiiiiiiiii",
                "email": "xiiiiiiiiii@github.com",
                "role": "Data Engineer",
                "experience_years": 5,
                "source": "GitHub",
                "status": "Applied",
                "skills": ["Python", "Spark", "Airflow", "SQL", "Data Pipelines", "MCP"],
                "applied_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "location": "San Francisco, CA",
                "github_profile": "https://github.com/xiiiiiiiiii",
                "github_profile_url": "https://github.com/xiiiiiiiiii",
                "github_username": "xiiiiiiiiii",
                "public_repos": 27,
                "github_repos": 27,
                "total_stars": 178,
                "github_stars": 178,
                "followers": 312,
                "github_contributions": 1654,
                "coding_assessment_score": 81,
                "system_design_level": "Mid",
                "open_source_contributor": True,
                "avatar_url": "https://avatars.githubusercontent.com/xiiiiiiiiii",
                "primary_language": "Python",
                "languages": ["Python", "SQL"],
            },
            {
                "id": "CAND-008",
                "name": "Rowens72",
                "email": "rowens72@github.com",
                "role": "Security Engineer",
                "experience_years": 8,
                "source": "GitHub",
                "status": "System Design",
                "skills": ["Rust", "Security", "Dotnet", "C#", "Network Security", "Penetration Testing"],
                "applied_date": (datetime.now() - timedelta(days=10)).isoformat(),
                "location": "London, UK",
                "github_profile": "https://github.com/Rowens72",
                "github_profile_url": "https://github.com/Rowens72",
                "github_username": "Rowens72",
                "public_repos": 19,
                "github_repos": 19,
                "total_stars": 456,
                "github_stars": 456,
                "followers": 892,
                "github_contributions": 1432,
                "coding_assessment_score": 93,
                "system_design_level": "Senior",
                "open_source_contributor": True,
                "avatar_url": "https://avatars.githubusercontent.com/Rowens72",
                "primary_language": "Rust",
                "languages": ["Rust", "C#"],
            },
        ]
        
        # Add more generic candidates
        tech_roles = ["Software Engineer", "Senior Software Engineer", "Staff Engineer", 
                      "Frontend Engineer", "Backend Engineer", "Full Stack Engineer",
                      "DevOps Engineer", "Data Scientist", "ML Engineer"]
        sources = ["GitHub", "Referral", "Tech Conference", "Open Source Community", "Direct Application"]
        statuses = ["Applied", "Screening", "Technical Interview", "System Design", "Offer", "Hired"]
        tech_skills = ["Python", "JavaScript", "TypeScript", "React", "Node.js", "Go", "Rust",
                      "AWS", "Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Redis",
                      "Machine Learning", "System Design", "Microservices", "GraphQL", "REST APIs"]
        
        candidates = featured_profiles.copy()
        
        for i in range(9, 21):
            github_username = f"techdev{i}"
            candidate = {
                "id": f"CAND-{i:03d}",
                "name": f"Tech Candidate {i}",
                "email": f"techcandidate{i}@email.com",
                "role": random.choice(tech_roles),
                "experience_years": random.randint(2, 15),
                "source": random.choice(sources),
                "status": random.choice(statuses),
                "skills": random.sample(tech_skills, k=random.randint(5, 10)),
                "applied_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "location": random.choice(["San Francisco, CA", "New York, NY", "Austin, TX", 
                                          "Seattle, WA", "Remote - US", "Remote - Global"]),
                # Tech-specific fields
                "github_profile": f"https://github.com/{github_username}",
                "github_username": github_username,
                "github_repos": random.randint(5, 50),
                "github_stars": random.randint(10, 500),
                "github_contributions": random.randint(100, 2000),
                "coding_assessment_score": random.randint(65, 100),
                "system_design_level": random.choice(["Junior", "Mid", "Senior", "Staff"]),
                "open_source_contributor": random.choice([True, False]),
                "avatar_url": f"https://avatars.githubusercontent.com/{github_username}",
            }
            candidates.append(candidate)
        return candidates
    
    def _generate_mock_jobs(self) -> list:
        """Generate mock job postings"""
        return [
            {
                "id": "JOB-001",
                "title": "Senior Software Engineer",
                "department": "Engineering",
                "status": "Open",
                "openings": 3,
                "applications": 45,
                "salary_range": "$150,000 - $200,000"
            },
            {
                "id": "JOB-002",
                "title": "Product Manager",
                "department": "Product",
                "status": "Open",
                "openings": 2,
                "applications": 32,
                "salary_range": "$140,000 - $180,000"
            }
        ]
    
    def _generate_mock_applications(self) -> list:
        """Generate mock applications.

        Scraped GitHub profiles won't have recruitment pipeline fields like `status`,
        so we synthesize a reasonable default instead of raising KeyError.
        """
        applications: list[Dict[str, Any]] = []
        for c in self.candidates[:15]:
            applications.append(
                {
                    "candidate_id": c.get("id"),
                    "job_id": "JOB-001",
                    # Default to Applied if no explicit status present
                    "stage": c.get("status", "Applied"),
                }
            )
        return applications
    
    def _get_candidate_pipeline(self) -> str:
        """Return pipeline analysis"""
        by_source = {}
        for c in self.candidates:
            # Scraped GitHub profiles may not have "source", default to GitHub
            source = c.get("source", "GitHub")
            by_source[source] = by_source.get(source, 0) + 1
        
        return json.dumps({
            "total_candidates": len(self.candidates),
            "by_source": by_source,
            "recent_candidates": self.candidates[:5],
            "conversion_rate": "35%",
            "avg_time_to_hire": "28 days"
        }, indent=2)
    
    def _get_compensation_data(self) -> str:
        """Return compensation benchmarks"""
        return json.dumps({
            "role": "Senior Software Engineer",
            "market_data": {
                "p25": 140000,
                "p50": 165000,
                "p75": 190000,
                "p90": 225000
            },
            "location_adjustment": {
                "San Francisco": 1.25,
                "New York": 1.20,
                "Austin": 0.95,
                "Remote": 1.0
            },
            "recommended_range": "$150,000 - $200,000",
            "equity": "0.05% - 0.15%",
            "benefits_value": "$25,000/year"
        }, indent=2)
    
    def _get_candidate_profiles(self) -> str:
        """Return candidate details"""
        # Scraped profiles may not have explicit experience_years; fall back to
        # inferred account_age_years from GitHub or 0.
        top_candidates = sorted(
            self.candidates,
            key=lambda x: x.get("experience_years", x.get("account_age_years", 0)),
            reverse=True,
        )[:3]
        return json.dumps({
            "total_reviewed": len(self.candidates),
            "top_matches": top_candidates,
            "skill_gaps": ["Kubernetes", "System Design", "Leadership"],
            "recommendations": [
                "Focus on candidates with 5+ years experience",
                "Prioritize referral sources (higher quality)",
                "Schedule technical screens for top 3 candidates"
            ]
        }, indent=2)
    
    def _get_hiring_goals(self) -> str:
        """Return hiring goals and progress"""
        return json.dumps({
            "quarterly_target": 12,
            "hired_this_quarter": 7,
            "in_pipeline": 45,
            "progress": "58%",
            "departments": {
                "Engineering": {"target": 8, "hired": 5, "pipeline": 28},
                "Product": {"target": 2, "hired": 1, "pipeline": 10},
                "Design": {"target": 2, "hired": 1, "pipeline": 7}
            },
            "bottlenecks": [
                "Technical interview stage (avg 12 days)",
                "Offer acceptance rate lower than target (65% vs 80%)"
            ]
        }, indent=2)
    
    def _get_market_insights(self) -> str:
        """Return tech market trends"""
        return json.dumps({
            "market_conditions": "Highly competitive for tech talent",
            "salary_trends": {
                "Software Engineers": "+8% YoY",
                "Senior Engineers": "+10% YoY",
                "Staff Engineers": "+12% YoY",
                "ML Engineers": "+15% YoY"
            },
            "talent_availability": {
                "Junior Engineers": "Moderate competition",
                "Mid-level Engineers": "High competition",
                "Senior Engineers": "Very high competition",
                "Staff/Principal": "Extremely high competition"
            },
            "recommendations": [
                "Leverage GitHub and open-source communities for sourcing",
                "Offer competitive equity packages (0.1-0.5% for senior roles)",
                "Accelerate technical interview process (< 2 weeks ideal)",
                "Highlight engineering culture and technical challenges",
                "Consider remote-first to expand talent pool globally"
            ],
            "competitor_intelligence": {
                "avg_time_to_offer": "18 days",
                "avg_salary_for_senior": "$175,000 + equity",
                "top_sourcing_channels": ["GitHub", "Referrals", "Tech Conferences"]
            }
        }, indent=2)
    
    def _get_time_tracking_data(self) -> str:
        """Return recruiter time tracking and productivity analytics"""
        return json.dumps({
            "recruiter_id": "REC-001",
            "recruiter_name": "Sarah Johnson",
            "period": "Last 7 days",
            "total_hours": 40,
            "activity_breakdown": {
                "Candidate Sourcing": {"hours": 12, "percentage": "30%"},
                "GitHub Research": {"hours": 10, "percentage": "25%"},
                "Phone Screenings": {"hours": 8, "percentage": "20%"},
                "Technical Interviews": {"hours": 5, "percentage": "12.5%"},
                "Admin & Scheduling": {"hours": 3, "percentage": "7.5%"},
                "Follow-ups": {"hours": 2, "percentage": "5%"}
            },
            "productivity_metrics": {
                "candidates_sourced": 25,
                "outreach_sent": 45,
                "responses_received": 12,
                "response_rate": "26.7%",
                "screens_completed": 8,
                "candidates_advanced": 5
            },
            "bottlenecks": [
                "High time on admin tasks (7.5% - consider automation)",
                "GitHub outreach response rate lower than target (28% vs 35%)",
                "Direct application screening taking too long (needs automation)"
            ],
            "recommendations": [
                "Increase GitHub open-source community engagement",
                "Automate scheduling to reduce admin time",
                "Optimize GitHub issue/PR engagement templates",
                "Focus on warm referrals which have 60% higher conversion"
            ],
            "comparison_to_team_avg": {
                "sourcing_time": "+2 hours (above average)",
                "screening_efficiency": "1.6 screens/hour (team avg: 1.4)",
                "github_response_rate": "28% (team avg: 31%)"
            }
        }, indent=2)
    
    def _get_general_info(self) -> str:
        """Return general recruitment info"""
        return json.dumps({
            "message": "Recruitment system active",
            "total_candidates": len(self.candidates),
            "total_jobs": len(self.jobs),
            "total_applications": len(self.applications),
            "system_status": "operational"
        }, indent=2)

# Singleton instance
recruitment_service = MockRecruitmentService()

