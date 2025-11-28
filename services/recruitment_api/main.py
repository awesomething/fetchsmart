"""Mock Recruiting API for Dashboard MVP."""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os

app = FastAPI(
    title="Recruiting API",
    description="Mock API for recruiting dashboard",
    version="0.1.0"
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Data Models ====================

class GitHubProfile(BaseModel):
    username: str
    url: str
    repos: int
    stars: int
    contributions_last_year: int
    top_languages: List[str]


class Candidate(BaseModel):
    id: str
    name: str
    email: str
    location: str
    skills: List[str]
    experience_years: int
    technical_level: str
    github_profile: Optional[GitHubProfile] = None
    status: str
    source: str


class Job(BaseModel):
    id: str
    title: str
    department: str
    level: str
    location: str
    remote_policy: str
    required_skills: List[str]
    status: str


class Application(BaseModel):
    id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    stage: str
    applied_date: str
    source: str


class DashboardMetrics(BaseModel):
    total_candidates: int
    active_jobs: int
    applications_this_month: int
    avg_time_to_hire: int
    candidate_sources: dict
    pipeline_stages: dict


class ProductivitySummary(BaseModel):
    window: str
    total_hours: float
    activities: dict
    efficiency_metrics: dict


# ==================== Seed Data ====================

SEED_CANDIDATES = [
    Candidate(
        id="c1",
        name="Alice Johnson",
        email="alice.j@example.com",
        location="San Francisco, CA",
        skills=["Python", "React", "AWS", "Docker"],
        experience_years=5,
        technical_level="senior",
        github_profile=GitHubProfile(
            username="alicej",
            url="https://github.com/alicej",
            repos=45,
            stars=230,
            contributions_last_year=450,
            top_languages=["Python", "JavaScript", "Go"]
        ),
        status="active",
        source="GitHub"
    ),
    Candidate(
        id="c2",
        name="Bob Chen",
        email="bob.chen@example.com",
        location="Austin, TX",
        skills=["Java", "Kubernetes", "PostgreSQL", "Terraform"],
        experience_years=7,
        technical_level="staff",
        github_profile=GitHubProfile(
            username="bobchen",
            url="https://github.com/bobchen",
            repos=78,
            stars=890,
            contributions_last_year=620,
            top_languages=["Java", "Python", "TypeScript"]
        ),
        status="active",
        source="GitHub"
    ),
    Candidate(
        id="c3",
        name="Carol Davis",
        email="carol.d@example.com",
        location="New York, NY",
        skills=["TypeScript", "Node.js", "React", "GraphQL"],
        experience_years=4,
        technical_level="mid",
        github_profile=GitHubProfile(
            username="carold",
            url="https://github.com/carold",
            repos=32,
            stars=145,
            contributions_last_year=380,
            top_languages=["TypeScript", "JavaScript"]
        ),
        status="active",
        source="GitHub"
    ),
]

SEED_JOBS = [
    Job(
        id="j1",
        title="Senior Backend Engineer",
        department="Engineering",
        level="senior",
        location="San Francisco, CA",
        remote_policy="hybrid",
        required_skills=["Python", "AWS", "PostgreSQL", "Docker"],
        status="open"
    ),
    Job(
        id="j2",
        title="Staff DevOps Engineer",
        department="Infrastructure",
        level="staff",
        location="Remote",
        remote_policy="remote",
        required_skills=["Kubernetes", "Terraform", "AWS", "Python"],
        status="open"
    ),
    Job(
        id="j3",
        title="Frontend Engineer",
        department="Engineering",
        level="mid",
        location="New York, NY",
        remote_policy="onsite",
        required_skills=["React", "TypeScript", "CSS", "GraphQL"],
        status="open"
    ),
]

SEED_APPLICATIONS = [
    Application(
        id="a1",
        candidate_id="c1",
        candidate_name="Alice Johnson",
        job_id="j1",
        job_title="Senior Backend Engineer",
        stage="technical_interview",
        applied_date="2025-11-01",
        source="GitHub"
    ),
    Application(
        id="a2",
        candidate_id="c2",
        candidate_name="Bob Chen",
        job_id="j2",
        job_title="Staff DevOps Engineer",
        stage="offer",
        applied_date="2025-10-28",
        source="GitHub"
    ),
    Application(
        id="a3",
        candidate_id="c3",
        candidate_name="Carol Davis",
        job_id="j3",
        job_title="Frontend Engineer",
        stage="screening",
        applied_date="2025-11-05",
        source="GitHub"
    ),
]


# ==================== Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "recruiting-api"}


@app.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    """Get dashboard summary metrics."""
    return DashboardMetrics(
        total_candidates=len(SEED_CANDIDATES),
        active_jobs=len([j for j in SEED_JOBS if j.status == "open"]),
        applications_this_month=len(SEED_APPLICATIONS),
        avg_time_to_hire=32,
        candidate_sources={
            "GitHub": 3,
        },
        pipeline_stages={
            "screening": 1,
            "technical_interview": 1,
            "offer": 1,
        }
    )


@app.get("/candidates", response_model=List[Candidate])
async def get_candidates(
    query: Optional[str] = Query(None),
    skills: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
):
    """Get candidates list with optional filters."""
    candidates = SEED_CANDIDATES.copy()
    
    if query:
        candidates = [c for c in candidates if query.lower() in c.name.lower() or query.lower() in c.email.lower()]
    
    if skills:
        skill_list = [s.strip() for s in skills.split(",")]
        candidates = [c for c in candidates if any(skill in c.skills for skill in skill_list)]
    
    if location:
        candidates = [c for c in candidates if location.lower() in c.location.lower()]
    
    return candidates


@app.get("/candidates/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: str):
    """Get candidate details by ID."""
    for candidate in SEED_CANDIDATES:
        if candidate.id == candidate_id:
            return candidate
    return {"error": "Candidate not found"}


@app.get("/jobs", response_model=List[Job])
async def get_jobs(
    stack: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
):
    """Get jobs list with optional filters."""
    jobs = SEED_JOBS.copy()
    
    if stack:
        jobs = [j for j in jobs if stack in j.required_skills]
    
    if level:
        jobs = [j for j in jobs if j.level == level]
    
    return jobs


@app.get("/applications", response_model=List[Application])
async def get_applications(
    stage: Optional[str] = Query(None),
):
    """Get applications list with optional filters."""
    applications = SEED_APPLICATIONS.copy()
    
    if stage:
        applications = [a for a in applications if a.stage == stage]
    
    return applications


@app.get("/productivity/summary", response_model=ProductivitySummary)
async def get_productivity_summary(
    window: str = Query("7d", regex="^(7d|30d)$"),
):
    """Get recruiter productivity summary."""
    if window == "7d":
        return ProductivitySummary(
            window="7d",
            total_hours=42.5,
            activities={
                "sourcing": 15.5,
                "screening": 12.0,
                "interviews": 8.0,
                "admin": 7.0,
            },
            efficiency_metrics={
                "candidates_sourced_per_hour": 3.2,
                "screens_per_hour": 1.5,
                "github_outreach_success_rate": 0.45,
            }
        )
    else:  # 30d
        return ProductivitySummary(
            window="30d",
            total_hours=180.0,
            activities={
                "sourcing": 68.0,
                "screening": 52.0,
                "interviews": 35.0,
                "admin": 25.0,
            },
            efficiency_metrics={
                "candidates_sourced_per_hour": 3.5,
                "screens_per_hour": 1.6,
                "github_outreach_success_rate": 0.48,
            }
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8085"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)

