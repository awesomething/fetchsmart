# Agent Prompts Reference Guide

This document contains example prompts for each agent in the system. All prompts are based on actual agent capabilities as defined in the codebase.

## Table of Contents

1. [Planning Agent](#planning-agent)
2. [FAQ Agent](#qa-agent)
3. [Recruiter Orchestrator](#recruiter-orchestrator)
4. [Recruiter Email Pipeline](#recruiter-email-pipeline)
5. [Staffing Recruiter Orchestrator](#staffing-recruiter-orchestrator)
6. [Staffing Employer Orchestrator](#staffing-employer-orchestrator)

---

## Planning Agent

**Mode:** `[MODE:PLANNING]`  
**Description:** Specialized agent for recruiter planning, hiring workflows, and daily/weekly task management.

### Hiring Goal Planning
- "Plan my week for filling 3 Senior React Developer positions"
- "Create a daily task list for sourcing DevOps candidates"
- "Break down the hiring process for a Product Manager role"
- "Plan interview coordination for 5 candidates this week"
- "Create a weekly plan to improve my pipeline metrics"
- "Plan my month for hiring 2 Senior Backend Engineers and 1 Frontend Developer"

### Workflow Phase Planning
- "Plan the sourcing phase for a Senior Data Engineer role"
- "Create tasks for the screening and evaluation phase for React developers"
- "Plan outreach activities for 10 shortlisted candidates"
- "Break down interview coordination tasks for this week"
- "Plan the decision and offer phase for 3 final candidates"

### Time-Bound Planning
- "What should I focus on today to fill the Senior Python Developer role?"
- "Create a 2-hour sourcing sprint plan for Frontend Engineers"
- "Plan my afternoon for following up with active pipeline candidates"
- "What weekly tasks should I prioritize for multiple open roles?"

### Pipeline Optimization
- "Plan activities to reduce time-to-fill for my open positions"
- "Create a plan to improve my candidate pipeline conversion rates"
- "Plan weekly activities to maintain a healthy candidate pipeline"
- "Break down tasks to improve my sourcing effectiveness"

---

## FAQ Agent

**Mode:** `[MODE:QA]`  
**Description:** Specialized agent for answering questions by searching and reading Google Docs.

### App Overview & How It Works
- "How does this app work?"
- "What agents are available in this system?"
- "Explain how the multi-agent system works"
- "What can I do with this application?"
- "Tell me about all the agents"
- "How do the different agents work together?"

### Agent-Specific Questions
- "How does the Planning Agent work?"
- "What can the Recruiter Orchestrator do?"
- "Explain the Staffing Recruiter Orchestrator"
- "How does the Staffing Employer Orchestrator work?"
- "What is the Recruiter Email Pipeline?"
- "Tell me about the FAQ Agent"

### Document Search
- "What is our deployment process?"
- "Search documentation for API authentication"
- "Find information about database schema"
- "What does the documentation say about error handling?"
- "Search for information about configuration settings"

### Document Reading
- "Read the deployment guide and summarize the key steps"
- "What are the main points in the architecture document?"
- "Read the onboarding documentation and tell me the requirements"
- "What does the API documentation say about rate limits?"

### Recent Documents
- "What documents have been recently updated?"
- "Show me the most recent documentation"
- "List available documents"
- "What documentation is available in the system?"

### Question Answering
- "How do I deploy the application?"
- "What are the system requirements?"
- "What is the recommended workflow for new features?"
- "How do I configure the database connection?"

---

## Recruiter Orchestrator

**Mode:** `[MODE:RECRUITER]`  
**Description:** Candidate search, GitHub sourcing, pipeline metrics, compensation checks.

### Candidate Search
- "Find senior engineers on GitHub"
- "Search for React developers with 5+ years experience"
- "Find Python developers in San Francisco"
- "Show me candidates with Kubernetes experience"
- "Find full-stack engineers with TypeScript skills"

### GitHub Sourcing
- "Source 10 Senior Backend Engineers from GitHub"
- "Find React developers with active GitHub profiles"
- "Search GitHub for DevOps engineers with Docker experience"
- "Find candidates with strong GitHub activity in Python"
- "Source Frontend Engineers with React and TypeScript"

### Pipeline Metrics
- "Show me candidate pipeline by source"
- "What's my pipeline conversion rate?"
- "Show me sourced vs advanced candidates"
- "What are my pipeline metrics for this month?"
- "How many candidates are in each stage?"

### Compensation Checks
- "What's the market rate for Senior React Developers in San Francisco?"
- "Check compensation for Python Engineers with 8 years experience"
- "What should I offer a Senior DevOps Engineer?"
- "What's the salary range for Full Stack Engineers in Austin?"

### Profile Summaries
- "Give me a summary of candidate Rowens72"
- "Summarize the profile for Mithonmasud"
- "What are the key skills for candidate Marquish?"
- "Show me a profile summary for Ekeneakubue"

---

## Recruiter Email Pipeline

**Mode:** `[MODE:EMAIL]`  
**Description:** Generates, reviews, and refines personalized recruiter outreach emails.

### Email Generation
- "Write an outreach email for Mithonmasud"
- "Generate an email for candidate Rowens72 about a Senior React role"
- "Create a personalized email for Marquish"
- "Write an outreach email for Sarah Chen"
- "Generate an email for Alex Kumar about a Mobile Engineer position"

### Email Refinement
- "Refine the candidate email with GitHub context"
- "Improve the outreach email to be more personal"
- "Make the email shorter and more direct"
- "Add more technical details to the email"
- "Refine the email to highlight the candidate's specific skills"

### Email Review
- "Review this outreach email for quality"
- "Check if this email follows best practices"
- "Review the email for personalization"
- "Does this email need improvement?"

### Email Context Enhancement
- "Write an email for Mithonmasud with their GitHub profile context"
- "Generate an email for Rowens72 including their project contributions"
- "Create an email that references the candidate's specific experience"
- "Write an email that mentions their open source contributions"

---

## Staffing Recruiter Orchestrator

**Mode:** `[MODE:STAFFING_RECRUITER]`  
**Description:** Orchestrates recruiter workflow: job search → candidate matching → submission.

### Job Search
- "Find React developer jobs available now"
- "Search for open DevOps positions"
- "Find jobs for Senior Python Engineers"
- "Show me available Frontend Developer roles"
- "Search for remote Backend Engineer positions"
- "Find jobs matching TypeScript and React skills"

### Candidate Matching
- "Match candidates to job SUB-20250120-123456"
- "Find candidates suitable for the Senior React Developer role"
- "Match candidates to this job opening"
- "Which candidates fit the DevOps Engineer position?"
- "Find the best candidates for this job requirement"

### Candidate Submission
- "Submit candidate John Doe for Senior Frontend position"
- "Submit candidate Sarah Chen for the React Developer role"
- "Create a submission for candidate Alex Kumar"
- "Submit candidate Mithonmasud for the Full Stack Engineer position"

### Full Recruiter Workflow
- "Full recruiter workflow for DevOps positions"
- "Complete the recruiting process for React Developer roles"
- "End-to-end workflow for finding and submitting Python Engineers"
- "Full workflow: find jobs, match candidates, and submit"

---

## Staffing Employer Orchestrator

**Mode:** `[MODE:STAFFING_EMPLOYER]` or `[MODE:EMPLOYER]`  
**Description:** Orchestrates employer workflow: candidate review → interview scheduling → hiring decisions.

### Candidate Review
- "Review candidate Craig with email timothy.lefkowitz@gmail.com"
- "Review candidates for React Developer role"
- "Evaluate candidate submissions for the DevOps position"
- "Review candidate John Doe for Senior Frontend role"
- "Assess candidates for the Python Engineer position"
- "Review all candidates submitted for this role"

### Candidate Assessment
- "Review candidate Craig with email timothy.lefkowitz@gmail.com. Job Qualifications: Excellent Communication Skills, Customer Service Experience, Problem-Solving Abilities"
- "Evaluate candidate skills against job requirements"
- "Compare candidate experience to the job description"
- "Assess if this candidate is a good fit for the role"

### Interview Scheduling
- "Schedule technical interview for John Doe"
- "Schedule interview with candidate Sarah Chen"
- "Coordinate interviews for shortlisted candidates"
- "Set up interview for candidate Alex Kumar"
- "Schedule screening call for candidate Mithonmasud"

### Hiring Pipeline Status
- "Show hiring pipeline status"
- "What's the status of candidates in the pipeline?"
- "Show me candidates at each hiring stage"
- "What's the progress on the React Developer role?"
- "Show pipeline metrics for open positions"

### Hiring Decisions
- "Process new candidate submissions"
- "Update candidate status to interview scheduled"
- "Move candidate to next stage in pipeline"
- "Update hiring pipeline for reviewed candidates"

---

## Usage Notes

### Mode Directives
- Use mode directives to explicitly route to specific agents: `[MODE:PLANNING]`, `[MODE:QA]`, `[MODE:RECRUITER]`, `[MODE:EMAIL]`, `[MODE:STAFFING_RECRUITER]`, `[MODE:STAFFING_EMPLOYER]`
- If no mode directive is provided, the root agent will use smart routing based on the query content

### Best Practices
- Be specific about roles, skills, and requirements
- Include relevant context (candidate names, job IDs, email addresses)
- For candidate reviews, provide job description summary (max 1028 characters)
- For email generation, mention candidate names or GitHub usernames
- For planning, specify timeframes (daily, weekly, monthly)

### Agent Capabilities Summary
- **Planning Agent**: Task breakdown, workflow planning, time estimation
- **FAQ Agent**: Document search, reading, question answering
- **Recruiter Orchestrator**: GitHub sourcing, candidate search, metrics, compensation
- **Recruiter Email Pipeline**: Email generation, review, refinement loop
- **Staffing Recruiter**: Job search, candidate matching, submissions
- **Staffing Employer**: Candidate review, interview scheduling, pipeline management

