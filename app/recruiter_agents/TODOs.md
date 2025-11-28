Breakdown of the recruiter process from sourcing to interview scheduling, mapped to your agent architecture:

## Complete recruiter workflow

### Phase 1: Job requirement & planning
1. Job requirement gathering
   - Role definition (title, level, team)
   - Skills/tech stack
   - Experience level (junior/mid/senior)
   - Location/remote preferences
   - Compensation range
   - Timeline/urgency

2. Job posting creation
   - Write job description
   - Post to job boards (LinkedIn, Indeed, etc.)
   - Internal referrals
   - Social media promotion

---

### Phase 2: Candidate sourcing
3. Active sourcing
   - GitHub profile search
   - LinkedIn search
   - Stack Overflow profiles
   - Tech community forums
   - Open source contributions
   - Conference speakers
   - Portfolio sites

4. Passive sourcing
   - Applicant tracking system (ATS) review
   - Resume database search
   - Previous applicant pipeline
   - Employee referrals

Your agent: Candidate Sourcing Agent (Port 8103)
- Uses: `search_candidates_tool`, `scrape_github_profiles_tool`

---

### Phase 3: Initial screening
5. Resume/CV review
   - Skills match
   - Experience level
   - Education
   - Career progression
   - Red flags (gaps, job hopping)

6. AI-powered matching
   - Score candidates (0-100%)
   - Match reasons
   - Skill overlap
   - Experience alignment

Your agent: Resume Screening Agent (Port 8104)
- Uses: `search_candidates_tool`, `get_pipeline_metrics_tool`

---

### Phase 4: Deep evaluation
7. Portfolio analysis
   - GitHub profile review
   - Code quality assessment
   - Project complexity
   - Contribution patterns
   - Open source activity
   - Technical depth

8. Social/online presence
   - LinkedIn profile
   - Personal website/blog
   - Tech blog posts
   - Conference talks
   - Community involvement

Your agent: Candidate Portfolio Agent (Port 8105)
- Uses: `analyze_portfolio_tool`

---

### Phase 5: Compensation & market research
9. Salary benchmarking
   - Market rate research
   - Location adjustments
   - Experience level pricing
   - Equity/benefits comparison
   - Competitive analysis

10. Budget alignment
    - Internal budget check
    - Approval process
    - Offer range determination

Your agent: Compensation Agent (Port 8107)
- Uses: `get_compensation_data_tool`

---

### Phase 6: Outreach & initial contact
11. Candidate outreach
    - Personalized message
    - Job description
    - Company overview
    - Next steps

12. Response management
    - Track responses
    - Follow-ups
    - Interest level assessment
    - Availability check

Your agent: Could use `send_recruitment_email_tool`

---

### Phase 7: Phone/initial screen
13. Phone screen scheduling
    - Calendar coordination
    - Time zone alignment
    - Interviewer availability
    - Duration (30-45 min)

14. Phone screen execution
    - Basic qualifications
    - Communication skills
    - Cultural fit
    - Salary expectations
    - Availability/timeline
    - Interest level

15. Post-screen evaluation
    - Pass/fail decision
    - Notes documentation
    - Next steps determination

---

### Phase 8: Technical assessment
16. Technical evaluation
    - Coding challenge
    - Take-home project
    - Live coding session
    - System design discussion

17. Assessment review
    - Technical skills evaluation
    - Problem-solving ability
    - Code quality
    - Communication during technical discussion

---

### Phase 9: Interview scheduling
18. Interview coordination
    - Multiple interviewer schedules
    - Time zone coordination
    - Interview format (onsite/remote)
    - Duration (1-2 hours per round)
    - Panel vs. 1-on-1

19. Calendar management
    - Send calendar invites
    - Confirm attendance
    - Reschedule if needed
    - Send prep materials
    - Video link setup (if remote)

20. Interview logistics
    - Interviewer briefings
    - Question sets
    - Evaluation forms
    - Feedback collection

Your agent: Recruiter Productivity Agent (Port 8108)
- Uses: `get_time_tracking_tool` (tracks time spent on each phase)

---

### Phase 10: Interview execution
21. Interview day
    - Welcome candidate
    - Introduce interviewers
    - Conduct interviews
    - Collect feedback
    - Answer candidate questions

22. Post-interview
    - Feedback collection
    - Debrief meeting
    - Decision making
    - Next steps communication

---

## Mapping to your agent architecture

```
┌─────────────────────────────────────────────────────────┐
│ Root Recruiter Orchestrator (Port 8101)                  │
│ - Routes queries to appropriate sub-orchestrators        │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────────────────────┐      ┌──────────────────────────┐
│ Candidate Operations  │      │ Talent Analytics          │
│ Orchestrator (8102)   │      │ Orchestrator (8106)      │
└───────────────────────┘      └──────────────────────────┘
        │                                   │
   ┌────┴────┬────────────┐         ┌──────┴──────┐
   │         │            │         │             │
┌──┴──┐  ┌──┴──┐     ┌───┴───┐  ┌──┴──┐    ┌───┴───┐
│8103 │  │8104 │     │ 8105  │  │8107 │    │ 8108  │
│Sourc│  │Screen│     │Portfol│  │Comp │    │Product│
└─────┘  └─────┘     └───────┘  └─────┘    └───────┘
```

### Workflow mapping

| Recruiter Step | Agent(s) Responsible | MCP Tools Used |
|----------------|---------------------|----------------|
| **Sourcing** | Candidate Sourcing Agent (8103) | `search_candidates_tool`, `scrape_github_profiles_tool` |
| **Screening** | Resume Screening Agent (8104) | `search_candidates_tool`, `get_pipeline_metrics_tool` |
| **Portfolio Analysis** | Candidate Portfolio Agent (8105) | `analyze_portfolio_tool` |
| **Compensation Research** | Compensation Agent (8107) | `get_compensation_data_tool` |
| **Time Tracking** | Recruiter Productivity Agent (8108) | `get_time_tracking_tool` |
| **Outreach** | (Not yet implemented) | `send_recruitment_email_tool` |
| **Scheduling** | (Not yet implemented) | Could add calendar integration |

---

## Missing capabilities to add

1. Interview scheduling tool
   - Calendar integration (Google Calendar, Outlook)
   - Time zone handling
   - Multi-interviewer coordination
   - Automated invite sending

2. Candidate communication tool
   - Email templates
   - SMS/WhatsApp integration
   - Response tracking
   - Follow-up automation

3. ATS integration tool
   - Candidate status updates
   - Pipeline stage management
   - Notes/documentation
   - Interview feedback collection

4. Interview feedback tool
   - Structured feedback forms
   - Score aggregation
   - Decision recommendation
   - Candidate comparison

---

## Current status

- Working: Candidate search and matching (Phases 2-3)
- Built but not active: Portfolio analysis, compensation, productivity tracking (Phases 4-5, 10)
- Missing: Outreach, scheduling, interview coordination (Phases 6-9)

Should I prioritize adding interview scheduling, candidate communication, or ATS integration next?