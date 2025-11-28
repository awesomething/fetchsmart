# 🚀 Quick Start: 24-Hour MVP - GitHub Talent Sourcing

## What We're Building
A powerful AI recruiting assistant that lets you search 100 real GitHub profiles using natural language. Simply describe the role and get the top 8 matching candidates instantly.

---

## ⚡ Quick Setup (15 minutes)

### Step 1: Get GitHub Token (2 min)
1. Visit: https://github.com/settings/tokens/new
2. Name: "Recruitment Scraper"
3. Select scopes: `public_repo`, `read:user`
4. Click "Generate token"
5. **Copy the token** (you won't see it again!)

### Step 2: Scrape 100 Real Profiles (10-15 min)

```bash
cd mcp_server/recruitment_backend

# Set your GitHub token
export GITHUB_TOKEN='ghp_your_token_here'  # Replace with your actual token

# Run the scraper
python github_scraper.py
```

**What happens:**
- Searches for diverse developers across 20+ tech stacks
- Collects 100 profiles with full stats, skills, repos
- Saves to `github_profiles_100.json`
- Shows statistics (languages, experience levels, locations)

**Sample output:**
```
🚀 Starting GitHub profile scraping...
🎯 Target: 100 diverse profiles

[1/22] Searching: language:javascript followers:>100 repos:>10
   Found 15 users. Total unique: 15
[2/22] Searching: language:typescript followers:>50 repos:>10
   Found 15 users. Total unique: 28
...
📥 Fetching detailed profiles...

[1/100] Fetching Rowens72... ✓ (JavaScript, 285 followers)
[2/100] Fetching Mithonmasud... ✓ (TypeScript, 156 followers)
...

🎉 Successfully scraped 100 profiles!

📊 Profile Statistics:
==================================================

🔤 Top Languages:
  JavaScript: 28
  Python: 22
  TypeScript: 18
  Go: 12
  Rust: 8
  ...

👔 Experience Levels:
  Senior: 45
  Mid: 38
  Junior: 17

💾 Saved 100 profiles to github_profiles_100.json
```

### Step 3: Restart Backend (1 min)

```bash
# In agents/recruitment_backend directory
# Stop the current backend (Ctrl+C if running)

# Restart with new profiles
cd ..  # Back to mcp_server/ directory
make ????
```

You'll see:
```
✅ Loaded 100 real GitHub profiles from github_profiles_100.json
✅ Intelligent candidate matcher initialized
```

### Step 4: Test It! (2 min)

Open your app at http://localhost:3000/recruiter

Try these queries in the chat:

**Query 1: Specific Role**
```
Find Senior React Engineers with TypeScript experience
```

**Expected Result:** Top 8 React developers with match scores and reasons

**Query 2: Tech Stack**
```
Looking for Python developers with machine learning experience
```

**Expected Result:** ML engineers ranked by GitHub activity and skills


**Expected Result:** Full stack developers with detailed match analysis

---

## 🎯 How It Works

### 1. You Ask (Natural Language)
```
"Find Senior DevOps Engineers with Kubernetes experience"
```

### 2. AI Extracts Requirements
- **Skills**: Kubernetes, DevOps, Docker, CI/CD
- **Experience Level**: Senior
- **Preferences**: Open source, high GitHub activity

### 3. Intelligent Matching (Multi-Factor Scoring)
Each candidate gets scored on:
- **Skill Match (50%)**: Do they have the required technologies?
- **Experience Match (30%)**: Is their level appropriate?
- **GitHub Activity (20%)**: Repos, stars, contributions, followers

### 4. Top 8 Results Returned
Each with:
- ✓ Match score (0-100)
- ✓ Match reasons ("Expert in React with 8 years experience")
- ✓ GitHub stats (repos, stars, followers)
- ✓ Notable projects
- ✓ Skills and languages
- ✓ Direct link to GitHub profile

---

## 📊 What Data Is Collected

For each of 100 profiles:

```json
{
  "name": "Rowens72",
  "github_username": "Rowens72",
  "github_profile_url": "https://github.com/Rowens72",
  "avatar_url": "https://avatars.githubusercontent.com/Rowens72",
  
  "primary_language": "JavaScript",
  "languages": ["JavaScript", "TypeScript", "Python"],
  "skills": ["react", "nodejs", "docker", "kubernetes"],
  
  "public_repos": 42,
  "total_stars": 285,
  "followers": 180,
  
  "estimated_experience_level": "Senior",
  "account_age_years": 8.2,
  
  "notable_repos": [
    {
      "name": "awesome-react-app",
      "stars": 150,
      "language": "JavaScript",
      "topics": ["react", "typescript", "nextjs"]
    }
  ],
  
  "likely_roles": ["Senior Frontend Engineer", "Full Stack Engineer"],
  "open_source_contributor": true,
  "has_popular_repos": true,
  
  "bio": "Full stack developer passionate about React",
  "location": "San Francisco, CA"
}
```

---

## 🧪 Test Queries

### By Role
- "Find Backend Engineers"
- "Show me Mobile Developers"
- "Looking for ML Engineers"

### By Tech Stack
- "React + TypeScript + Next.js developers"
- "Python engineers with Django or FastAPI"
- "Go developers with microservices experience"

### By Experience
- "Senior Frontend Engineers"
- "Junior Python Developers"
- "Staff-level Backend Engineers"

### By Activity
- "Developers with popular open source projects"
- "Engineers with 500+ GitHub stars"
- "Active open source contributors"

### Complex Queries
```
"We're hiring a Senior Full Stack Engineer for our fintech startup.
Requirements:
- 5+ years experience with React and Node.js
- Strong TypeScript skills
- Experience with PostgreSQL and Redis
- Kubernetes/Docker for deployment
- Active on GitHub with contributions to open source
- Located in US time zones (remote OK)"
```


---

## 🎨 Frontend Integration (Next Steps)

The chat already works! But to make it beautiful:

### Current State
- ✅ Backend returns top 8 matches
- ✅ Chat agent processes queries
- ✅ Results returned as JSON

### Next: Display as Profile Cards

**Option 1: Show in Chat** (Easiest)
Update `RecruiterChat.tsx` to parse results and render profile cards inline.

**Option 2: Update Main Grid** (Most Visual)
When user searches, update the main `GitHubProfilesGrid` component to show results.

**Option 3: Split View** (Best UX)
Chat on left, results grid on right, updates in real-time.

---

## 🔥 Example Interaction

**Recruiter:** "Find Senior React Engineers"

**AI Response:**
```
Found 24 matching candidates. Here are the top 8:

1. Rowens72 (Match: 95%)
   ✓ Expert in React with 8 years GitHub history
   ✓ 285 stars, 1247 contributions
   ✓ Strong TypeScript and Node.js background
   ✓ Active open source contributor
   📊 42 repos | 285 stars | 180 followers
   🔗 github.com/Rowens72

2. Mithonmasud (Match: 88%)
   ✓ Full stack engineer with React specialization
   ✓ TypeScript expert (primary language)
   ✓ 156 stars across 38 repositories
   ✓ Next.js and GraphQL experience
   📊 38 repos | 156 stars | 124 followers
   🔗 github.com/Mithonmasud

[... 6 more candidates]
```

---

## 📈 Success Metrics

After 24 hours, you should have:

- ✅ **100 real profiles** loaded and searchable
- ✅ **Intelligent matching** working (<3 sec response time)
- ✅ **90%+ accurate** results for common tech roles
- ✅ **Beautiful UI** showing profile cards
- ✅ **Demo-ready** for recruiting team

---

## 🚀 Next Steps (Post-MVP)

### Hour 6-12: Enhance Chat UI
- Parse search results
- Render profile cards
- Add "View on GitHub" buttons
- Show match reasoning

### Hour 12-18: Add Filters
- "Show only Senior level"
- "Filter by location"
- "Must have >500 stars"

### Hour 18-24: Polish & Demo
- Add loading animations
- Test 20 real queries
- Record demo video
- Deploy to production

---

## 💡 Pro Tips

### Rate Limiting
GitHub API allows 5000 requests/hour with authentication. The scraper respects this with built-in delays.

### Profile Diversity
The scraper intentionally searches across 20+ tech stacks to give you diverse candidates (React, Python, Go, ML, DevOps, Mobile, etc.)

### Matching Algorithm
For MVP, we use weighted scoring:
- 50% skill match
- 30% experience level
- 20% GitHub activity

You can adjust these weights in `candidate_matcher.py`.

### Real-time Scraping
For production, consider scraping profiles on-demand using the GitHub API, or integrate with Firecrawl for deeper insights.

# Recruiter AI Agents - Multi-Agent Hiring System

This project reimagines recruiting through intelligent multi-agent systems powered by Google's Agent Development Kit (ADK), the Agent-to-Agent (A2A) Protocol, and the Gemini API.

## 🎯 What This Project Does

This multi-agent hiring system transforms the traditional hiring experience by providing proactive, intelligent talent placement guidance through specialized AI agents. Instead of static chatbots, users interact with a sophisticated orchestrator that routes queries to domain-specific agents, each equipped to handle different aspects of talent acquisition.

### The Agents

The system consists of six specialized agents working together, designed specifically for **tech recruiting**:

- **Recruiter Orchestrator** - Intelligently routes user queries to the appropriate specialist agent using reflection and planning patterns
- **Candidate Sourcing Agent** - Actively reaches out to GitHub for tech talent, analyzes candidate pipelines, sourcing channels, and recruitment metrics. Integrates with external APIs for proactive talent discovery
- **Compensation Agent** - Manages tech salary benchmarking, equity packages, and competitive offer negotiations for engineering roles
- **Candidate Portfolio Agent** - Reviews technical resumes, GitHub portfolios, coding samples, and candidate qualifications for tech positions
- **Resume screening Agent** - Tracks tech hiring targets and handles resume screening o and job matching
- **Recruiter Productivity Agent** - Tracks time management for recruiters including hours spent on various activities (sourcing, screening, interviews, admin), identifies bottlenecks, and provides productivity analytics comparing time allocation across activities

Each agent connects to the recruitment backend services through the A2A protocol, enabling seamless communication and data exchange between agents. The architecture follows **Agentic Design Patterns** including:
- **Reflection**: Agents self-evaluate and improve their responses
- **Tool Use**: Integration with external tools (LinkedIn API, GitHub API, MCP Tools)
- **Planning**: Multi-step task decomposition and execution
- **Multi-agent Collaboration**: Coordinated workflows across specialized agents

**MCP (Model Context Protocol) Ready**: The system is designed to integrate with MCP tools for extended capabilities, including custom data sources, specialized APIs, and enterprise integrations.


### Agent Ports
- Recruiter Orchestrator: Sub-Root agent (Like the buyer agent)
- Candidate Sourcing/Orchestrator Agent (GitHub)
- Compensation Agent (Tech Salary Data)
- Resume Screening Agent (Like the supplier agent)
- Candidate Portfolio Agent (Code Review)
- Recruiter Productivity Agent (Time Tracking)
- SUGGEST ONE MORE AGENT TO MAKE RECRUITMENT SUCCESSFUL - maybe handoff agent: Prints a report and emails recuiter about findings etc

## 🚀 Getting Started

### Prerequisites

### Setup Instructions

#### 1. Configure Environment Variables

You need to add your `GOOGLE_API_KEY` to the `.env` file in each agent directory:


Each `.env` file should contain:
```
GOOGLE_API_KEY=your_api_key_here
```

#### 2. Start the Agents

Open a terminal and navigate to the agents directory:

```bash
```

This will start all agents simultaneously on their respective ports.

#### 3. Start the Frontend

Open a **second terminal** and start the Next.js development server:


The frontend will be available at `http://localhost:3000`

## 💡 How It Works

1. **User Interaction**: Recruiters interact with the frontend interface, which provides a modern recruiting dashboard
2. **Query Routing**: The Chat Orchestrator receives user queries and intelligently routes them to the appropriate specialist agent
3. **Agent Processing**: Each specialist agent uses the recruitment data wrapper to communicate with backend services via A2A protocol
4. **Data Retrieval**: Agents fetch relevant data (candidate profiles, job postings, pipeline metrics, etc.) from the recruitment API
5. **Response Generation**: Agents analyze the data and generate intelligent, context-aware responses using Gemini
6. **User Response**: The orchestrator returns the response to the user through the frontend

## 🛠️ Technologies Used

- **[Google Agent Development Kit (ADK)](https://github.com/google/adk)** - Framework for building multi-agent systems
- **[Agent-to-Agent (A2A) Protocol](https://github.com/a2aproject/a2a)** - Standardized protocol for agent communication
- **[Gemini API](https://ai.google.dev/)** - Google's advanced AI model for natural language understanding
- **Next.js** - React framework for production-grade applications
- **Python** - Backend agent implementation
- **TypeScript** - Type-safe frontend development


## 🎯 Use Cases

This multi-agent hiring system is designed specifically for **tech recruiting teams**:

- **Tech Recruiters** - Automate sourcing from LinkedIn and GitHub, track time spent on activities, and optimize productivity
- **Engineering Hiring Managers** - Get AI-powered insights on technical candidate qualifications, code portfolios, and cultural fit
- **Tech Compensation Analysts** - Benchmark engineering salaries, equity packages, and design competitive offers for developers
- **Recruitment Operations** - Track hiring goals, monitor tech pipeline health, and identify time management bottlenecks
- **Technical Talent Leaders** - Analyze recruiter productivity, optimize sourcing channels, and improve tech hiring velocity


## Questions

**Default assumptions (if you don't answer):**
- 1a: All 7 agents for complete system
- 2a: Single MCP server with all tools
- 3a: Move to mcp_server as utilities
- 4a: Ports 8101-8107
