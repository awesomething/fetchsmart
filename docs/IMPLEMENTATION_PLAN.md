# Recruiting Dashboard Integration - Implementation Plan

**Reference**: This document provides step-by-step manual implementation instructions based on the approved Build Plan.

**Goal**: Integrate the recruiting dashboard UI from `refs/ai_agent_rocket` into the current Next.js app, powered by a mock Recruiting API, running via Docker Compose.

---

## Prerequisites

- Docker and Docker Compose installed
- Node.js 20+ installed (for local development)
- Python 3.11+ installed (for local development)
- Git repository at `C:\Users\Honri\Downloads\transformer`

---

## Phase 1: Mock Recruiting API Setup

### Step 1.1: Create Service Directory Structure

```bash
# From repo root
mkdir -p services/recruitment_api
cd services/recruitment_api
```

### Step 1.2: Create `pyproject.toml`

Create `services/recruitment_api/pyproject.toml`:

```toml
[project]
name = "recruitment-api"
version = "0.1.0"
description = "Mock Recruiting API for dashboard MVP"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "python-dotenv>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Step 1.3: Create `.env.example`

Create `services/recruitment_api/.env.example`:

```bash
# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://frontend:3000

# Server Configuration
PORT=8085
HOST=0.0.0.0

# Data Configuration
SEED_DATA=true
```

### Step 1.4: Create Main API File

Create `services/recruitment_api/main.py`:

```python
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
        linkedin_profile=LinkedInProfile(
            url="https://linkedin.com/in/alicej",
            connections=500,
            headline="Senior Software Engineer"
        ),
        status="active",
        source="LinkedIn"
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
        linkedin_profile=LinkedInProfile(
            url="https://linkedin.com/in/bobchen",
            connections=850,
            headline="Staff Engineer"
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
        linkedin_profile=LinkedInProfile(
            url="https://linkedin.com/in/carold",
            connections=420,
            headline="Full Stack Engineer"
        ),
        status="active",
        source="Referral"
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
        source="LinkedIn"
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
        source="Referral"
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
            "LinkedIn": 1,
            "GitHub": 1,
            "Referral": 1,
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
                "linkedin_response_rate": 0.23,
                "github_response_rate": 0.45,
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
                "linkedin_response_rate": 0.25,
                "github_response_rate": 0.48,
            }
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8085"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
```

### Step 1.5: Create Dockerfile

Create `services/recruitment_api/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY main.py ./

# Expose port
EXPOSE 8085

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8085/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085"]
```

### Step 1.6: Test API Locally (Optional)

```bash
# From services/recruitment_api/
pip install -e .
python main.py

# In another terminal:
curl http://localhost:8085/health
curl http://localhost:8085/dashboard/metrics
```

**Expected**: Health check returns `{"status": "ok"}`, metrics return summary data.

---

## Phase 2: Docker Compose Setup

### Step 2.1: Create docker-compose.yml

Create `docker-compose.yml` in repo root:

```yaml
version: '3.8'

services:
  recruitment-api:
    build:
      context: ./services/recruitment_api
      dockerfile: Dockerfile
    container_name: recruitment-api
    ports:
      - "8085:8085"
    environment:
      - PORT=8085
      - HOST=0.0.0.0
      - CORS_ORIGINS=http://localhost:3000,http://frontend:3000
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8085/health')"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
    networks:
      - app-network

  frontend:
    build:
      context: ./nextjs
      dockerfile: Dockerfile
    container_name: nextjs-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_RECRUITING_API_URL=http://recruitment-api:8085
      - NODE_ENV=development
    depends_on:
      recruitment-api:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Step 2.2: Create Frontend Dockerfile

Create `nextjs/Dockerfile`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Health check endpoint needs to exist (we'll add it in Phase 3)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run in development mode for MVP
CMD ["npm", "run", "dev"]
```

### Step 2.3: Test Docker Compose

```bash
# From repo root
docker compose up --build

# In another terminal:
curl http://localhost:8085/health
curl http://localhost:3000
```

**Expected**: Both services start successfully, health checks pass.

---

## Phase 3: Frontend - API Client & Types

### Step 3.1: Create TypeScript Types

Create `nextjs/src/types/recruiting.ts`:

```typescript
export interface GitHubProfile {
  username: string;
  url: string;
  repos: number;
  stars: number;
  contributions_last_year: number;
  top_languages: string[];
}

export interface LinkedInProfile {
  url: string;
  connections: number;
  headline: string;
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  location: string;
  skills: string[];
  experience_years: number;
  technical_level: string;
  github_profile?: GitHubProfile;
  linkedin_profile?: LinkedInProfile;
  status: string;
  source: string;
}

export interface Job {
  id: string;
  title: string;
  department: string;
  level: string;
  location: string;
  remote_policy: string;
  required_skills: string[];
  status: string;
}

export interface Application {
  id: string;
  candidate_id: string;
  candidate_name: string;
  job_id: string;
  job_title: string;
  stage: string;
  applied_date: string;
  source: string;
}

export interface DashboardMetrics {
  total_candidates: number;
  active_jobs: number;
  applications_this_month: number;
  avg_time_to_hire: number;
  candidate_sources: Record<string, number>;
  pipeline_stages: Record<string, number>;
}

export interface ProductivitySummary {
  window: string;
  total_hours: number;
  activities: Record<string, number>;
  efficiency_metrics: Record<string, number>;
}
```

### Step 3.2: Create API Client

Create `nextjs/src/lib/recruiting-api.ts`:

```typescript
import type {
  Candidate,
  Job,
  Application,
  DashboardMetrics,
  ProductivitySummary,
} from '@/types/recruiting';

const API_BASE_URL = process.env.NEXT_PUBLIC_RECRUITING_API_URL || 'http://localhost:8085';

async function fetchAPI<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  return fetchAPI<DashboardMetrics>('/dashboard/metrics');
}

export async function getCandidates(params?: {
  query?: string;
  skills?: string;
  location?: string;
}): Promise<Candidate[]> {
  const searchParams = new URLSearchParams();
  if (params?.query) searchParams.append('query', params.query);
  if (params?.skills) searchParams.append('skills', params.skills);
  if (params?.location) searchParams.append('location', params.location);
  
  const query = searchParams.toString();
  return fetchAPI<Candidate[]>(`/candidates${query ? `?${query}` : ''}`);
}

export async function getCandidate(id: string): Promise<Candidate> {
  return fetchAPI<Candidate>(`/candidates/${id}`);
}

export async function getJobs(params?: {
  stack?: string;
  level?: string;
}): Promise<Job[]> {
  const searchParams = new URLSearchParams();
  if (params?.stack) searchParams.append('stack', params.stack);
  if (params?.level) searchParams.append('level', params.level);
  
  const query = searchParams.toString();
  return fetchAPI<Job[]>(`/jobs${query ? `?${query}` : ''}`);
}

export async function getApplications(params?: {
  stage?: string;
}): Promise<Application[]> {
  const searchParams = new URLSearchParams();
  if (params?.stage) searchParams.append('stage', params.stage);
  
  const query = searchParams.toString();
  return fetchAPI<Application[]>(`/applications${query ? `?${query}` : ''}`);
}

export async function getProductivitySummary(window: '7d' | '30d' = '7d'): Promise<ProductivitySummary> {
  return fetchAPI<ProductivitySummary>(`/productivity/summary?window=${window}`);
}
```

### Step 3.3: Create Health Check API Route

Create `nextjs/src/app/api/health/route.ts` (if it doesn't exist):

```typescript
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ status: 'ok' });
}
```

### Step 3.4: Create Environment File Example

Create `nextjs/.env.local.example`:

```bash
# Existing variables (unchanged)
BACKEND_URL=http://127.0.0.1:8000
NODE_ENV=development

# New variable for recruiting dashboard
NEXT_PUBLIC_RECRUITING_API_URL=http://127.0.0.1:8085
```

### Step 3.5: Create Local Environment File

```bash
# Copy example and adjust for local dev
cp nextjs/.env.local.example nextjs/.env.local
```

---

## Phase 4: Frontend - Recruiter Pages

### Step 4.1: Create Recruiter Landing Page

Create `nextjs/src/app/recruiter/page.tsx`:

```typescript
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

export default function RecruiterPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Recruiter Hub</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Link href="/recruiter/dashboard">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>Dashboard</CardTitle>
              <CardDescription>View recruiting metrics and analytics</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/recruiter/dashboard/candidates">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>Candidates</CardTitle>
              <CardDescription>Browse and manage candidates</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/recruiter/dashboard/jobs">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>Jobs</CardTitle>
              <CardDescription>Manage open positions</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/recruiter/dashboard/applications">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>Applications</CardTitle>
              <CardDescription>Track application pipeline</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/recruiter/dashboard/productivity">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle>Productivity</CardTitle>
              <CardDescription>View time tracking and analytics</CardDescription>
            </CardHeader>
          </Card>
        </Link>
      </div>
    </div>
  );
}
```

### Step 4.2: Create Dashboard Home Page

Create `nextjs/src/app/recruiter/dashboard/page.tsx`:

```typescript
import { getDashboardMetrics } from '@/lib/recruiting-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default async function DashboardPage() {
  const metrics = await getDashboardMetrics();

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Recruiting Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Candidates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.total_candidates}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.active_jobs}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Applications (This Month)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.applications_this_month}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Avg Time to Hire</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.avg_time_to_hire} days</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Candidate Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(metrics.candidate_sources).map(([source, count]) => (
                <div key={source} className="flex justify-between">
                  <span>{source}</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pipeline Stages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(metrics.pipeline_stages).map(([stage, count]) => (
                <div key={stage} className="flex justify-between">
                  <span className="capitalize">{stage.replace('_', ' ')}</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### Step 4.3: Create Candidates Page

Create `nextjs/src/app/recruiter/dashboard/candidates/page.tsx`:

```typescript
import { getCandidates } from '@/lib/recruiting-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default async function CandidatesPage() {
  const candidates = await getCandidates();

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Candidates</h1>
      
      <div className="grid grid-cols-1 gap-4">
        {candidates.map((candidate) => (
          <Card key={candidate.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{candidate.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">{candidate.email}</p>
                  <p className="text-sm text-muted-foreground">{candidate.location}</p>
                </div>
                <Badge>{candidate.technical_level}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium mb-2">Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {candidate.skills.map((skill) => (
                      <Badge key={skill} variant="outline">{skill}</Badge>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium">Experience</p>
                    <p className="text-sm text-muted-foreground">{candidate.experience_years} years</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Source</p>
                    <p className="text-sm text-muted-foreground">{candidate.source}</p>
                  </div>
                </div>

                {candidate.github_profile && (
                  <div>
                    <p className="text-sm font-medium mb-1">GitHub</p>
                    <div className="text-sm text-muted-foreground">
                      <p>@{candidate.github_profile.username} • {candidate.github_profile.repos} repos • {candidate.github_profile.stars} stars</p>
                      <p>Languages: {candidate.github_profile.top_languages.join(', ')}</p>
                    </div>
                  </div>
                )}

                {candidate.linkedin_profile && (
                  <div>
                    <p className="text-sm font-medium mb-1">LinkedIn</p>
                    <div className="text-sm text-muted-foreground">
                      <p>{candidate.linkedin_profile.headline}</p>
                      <p>{candidate.linkedin_profile.connections} connections</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

### Step 4.4: Create Jobs Page

Create `nextjs/src/app/recruiter/dashboard/jobs/page.tsx`:

```typescript
import { getJobs } from '@/lib/recruiting-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default async function JobsPage() {
  const jobs = await getJobs();

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Open Positions</h1>
      
      <div className="grid grid-cols-1 gap-4">
        {jobs.map((job) => (
          <Card key={job.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{job.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{job.department}</p>
                </div>
                <Badge variant="outline">{job.level}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium">Location</p>
                    <p className="text-sm text-muted-foreground">{job.location}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Remote Policy</p>
                    <p className="text-sm text-muted-foreground capitalize">{job.remote_policy}</p>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-medium mb-2">Required Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {job.required_skills.map((skill) => (
                      <Badge key={skill} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

### Step 4.5: Create Applications Page

Create `nextjs/src/app/recruiter/dashboard/applications/page.tsx`:

```typescript
import { getApplications } from '@/lib/recruiting-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default async function ApplicationsPage() {
  const applications = await getApplications();

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Applications</h1>
      
      <div className="grid grid-cols-1 gap-4">
        {applications.map((application) => (
          <Card key={application.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{application.candidate_name}</CardTitle>
                  <p className="text-sm text-muted-foreground">{application.job_title}</p>
                </div>
                <Badge>{application.stage.replace('_', ' ')}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium">Applied Date</p>
                  <p className="text-sm text-muted-foreground">{application.applied_date}</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Source</p>
                  <p className="text-sm text-muted-foreground">{application.source}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

### Step 4.6: Create Productivity Page

Create `nextjs/src/app/recruiter/dashboard/productivity/page.tsx`:

```typescript
import { getProductivitySummary } from '@/lib/recruiting-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default async function ProductivityPage() {
  const summary = await getProductivitySummary('7d');

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Productivity Analytics</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Time Allocation (Last 7 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Total Hours</span>
                <span className="text-2xl font-bold">{summary.total_hours}</span>
              </div>
              <div className="space-y-2 pt-4">
                {Object.entries(summary.activities).map(([activity, hours]) => (
                  <div key={activity} className="flex justify-between items-center">
                    <span className="capitalize">{activity}</span>
                    <span className="font-semibold">{hours}h</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Efficiency Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(summary.efficiency_metrics).map(([metric, value]) => (
                <div key={metric} className="flex justify-between items-center">
                  <span className="text-sm capitalize">{metric.replace(/_/g, ' ')}</span>
                  <span className="font-semibold">
                    {typeof value === 'number' && value < 1 
                      ? `${(value * 100).toFixed(0)}%` 
                      : value.toFixed(1)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

---

## Phase 5: Navigation Integration

### Step 5.1: Update Global Navigation

**Option A**: Update existing chat header (if applicable)

Edit `nextjs/src/components/chat/ChatHeader.tsx` (or your main header component):

```typescript
// Add this link/button to your header navigation
<Link href="/recruiter" className="...">
  Recruiter Hub
</Link>
```

**Option B**: Create a simple top-level navigation

Edit `nextjs/src/app/layout.tsx`:

```typescript
// Add navigation links in your layout
<nav className="border-b">
  <div className="container mx-auto flex gap-4 p-4">
    <Link href="/" className="hover:underline">Home</Link>
    <Link href="/recruiter" className="hover:underline">Recruiter</Link>
  </div>
</nav>
```

---

## Phase 6: Makefile Updates

### Step 6.1: Add Docker Compose Targets

Edit `Makefile` and add these targets at the end:

```makefile
# Docker Compose targets for recruiting dashboard MVP
dev-docker:
	@echo "🐳 Starting services with Docker Compose..."
	docker compose up --build

down-docker:
	@echo "🛑 Stopping Docker Compose services..."
	docker compose down -v
```

---

## Phase 7: Verification & Testing

### Step 7.1: Test Mock API Standalone

```bash
# Terminal 1
cd services/recruitment_api
pip install -e .
python main.py

# Terminal 2
curl http://localhost:8085/health
curl http://localhost:8085/dashboard/metrics
curl http://localhost:8085/candidates
```

**Expected**: All endpoints return valid JSON data.

### Step 7.2: Test with Docker Compose

```bash
# From repo root
docker compose up --build

# In another terminal:
curl http://localhost:8085/health
curl http://localhost:3000/api/health
```

**Expected**: Both health checks pass, services are running.

### Step 7.3: Test Frontend Pages

Open browser:
1. `http://localhost:3000/` → Existing home page works
2. `http://localhost:3000/recruiter` → Recruiter landing shows cards
3. `http://localhost:3000/recruiter/dashboard` → Dashboard metrics load
4. `http://localhost:3000/recruiter/dashboard/candidates` → Candidate list displays
5. `http://localhost:3000/recruiter/dashboard/jobs` → Jobs list displays
6. `http://localhost:3000/recruiter/dashboard/applications` → Applications list displays
7. `http://localhost:3000/recruiter/dashboard/productivity` → Productivity metrics load

**Expected**: All pages render, data loads from API, no CORS errors in console.

### Step 7.4: Verify Existing Features Unaffected

1. Test existing chat/agent UI at `/`
2. Verify `BACKEND_URL` still points to port 8000
3. Confirm no changes to existing ADK flows

---

## Phase 8: Documentation Updates

### Step 8.1: Update Main README

Add section to `README.md`:

```markdown
## Recruiter Dashboard (MVP)

### Local Development with Docker Compose

```bash
# Start all services
make dev-docker

# Or using docker compose directly
docker compose up --build

# Stop services
make down-docker
```

Access the dashboard at `http://localhost:3000/recruiter`.

### Environment Variables

The recruiter dashboard uses:
- `NEXT_PUBLIC_RECRUITING_API_URL`: Mock recruiting API endpoint (default: `http://127.0.0.1:8085`)

Existing agent features continue using `BACKEND_URL` (port 8000).
```

### Step 8.2: Create Troubleshooting Guide

Create `docs/RECRUITING_DASHBOARD_TROUBLESHOOTING.md`:

```markdown
# Recruiting Dashboard Troubleshooting

## Common Issues

### API Connection Errors

**Symptom**: Frontend shows "Failed to fetch" or CORS errors

**Solutions**:
1. Verify API is running: `curl http://localhost:8085/health`
2. Check Docker logs: `docker compose logs recruitment-api`
3. Verify CORS origins in `services/recruitment_api/.env`
4. Ensure `NEXT_PUBLIC_RECRUITING_API_URL` is set correctly

### Docker Build Failures

**Symptom**: `docker compose up` fails

**Solutions**:
1. Clear Docker cache: `docker compose down -v`
2. Remove old images: `docker system prune -a`
3. Check Dockerfile syntax
4. Verify all files exist

### Port Conflicts

**Symptom**: "Port already in use" errors

**Solutions**:
1. Check what's using ports:
   - Windows: `netstat -ano | findstr :3000`
   - Linux/Mac: `lsof -i :3000`
2. Stop conflicting services
3. Or change ports in `docker-compose.yml`

### Pages Not Loading

**Symptom**: 404 errors on recruiter pages

**Solutions**:
1. Verify files exist in `nextjs/src/app/recruiter/`
2. Clear Next.js cache: `rm -rf nextjs/.next`
3. Rebuild: `docker compose up --build`
```

---

## Rollback Instructions

### Complete Rollback

To remove the recruiting dashboard entirely:

```bash
# 1. Stop Docker services
docker compose down -v

# 2. Remove files
rm docker-compose.yml
rm -rf services/recruitment_api
rm -rf nextjs/src/app/recruiter
rm nextjs/src/lib/recruiting-api.ts
rm nextjs/src/types/recruiting.ts
rm nextjs/Dockerfile

# 3. Remove Makefile targets (manual edit)
# Remove dev-docker and down-docker targets from Makefile

# 4. Remove env var from .env.local
# Delete NEXT_PUBLIC_RECRUITING_API_URL line
```

### Partial Rollback (Keep API, Remove UI)

```bash
# Remove only frontend components
rm -rf nextjs/src/app/recruiter
rm nextjs/src/lib/recruiting-api.ts
rm nextjs/src/types/recruiting.ts
```

---

## Next Steps (Phase 2)

When ready to integrate with real agents:

1. **Deploy Recruiting Agents to Vertex Agent Engine**
   - Follow `docs/ADK_DEPLOYMENT_GUIDE.md`
   - Create 6 recruiting agents (Sourcing, Compensation, Portfolio, Goals, Productivity, Orchestrator)

2. **Wire Agents to MCP Server**
   - MCP server already deployed on Cloud Run (per `mcp_server/mcpdocs/README.md`)
   - Set `MCP_SERVER_URL` env var in agent deployments

3. **Replace Mock API**
   - Create ADK backend endpoints matching mock API schema
   - Update `NEXT_PUBLIC_RECRUITING_API_URL` to point to ADK backend
   - Gradually migrate endpoints from mock to real agents

4. **LinkedIn/GitHub Integration**
   - Add OAuth flows
   - Implement real API calls in agents
   - Store credentials securely

---

## Checklist

Use this checklist to track implementation:

- [ ] Phase 1: Mock API created and tested
- [ ] Phase 2: Docker Compose configured
- [ ] Phase 3: Frontend API client created
- [ ] Phase 4: All recruiter pages created
- [ ] Phase 5: Navigation added
- [ ] Phase 6: Makefile updated
- [ ] Phase 7: Full end-to-end verification passed
- [ ] Phase 8: Documentation updated

---

**Document Version**: 1.0  
**Last Updated**: November 12, 2025  
**Status**: Ready for Implementation

