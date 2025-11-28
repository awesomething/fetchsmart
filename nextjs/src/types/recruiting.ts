export interface GitHubProfile {
  username: string;
  url: string;
  repos: number;
  stars: number;
  contributions_last_year: number;
  top_languages: string[];
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

// New interfaces for MCP integration
export interface CandidateProfile {
  id: string;
  name: string;
  github_username: string;
  github_profile_url: string;
  role: string;
  experience_level: string;
  location: string;
  primary_language: string;
  skills: string[];
  github_stats: {
    repos: number;
    stars: number;
    followers: number;
    commits?: number;
  };
  match_score?: number;
  match_reasons?: string[];
  matched_skills?: string[];
  status?: string;
  email?: string | null;
  email_confidence?: number | null;
}

export interface PipelineMetrics {
  sourced: number;
  advanced: number;
  interviewed: number;
  offered: number;
}

export interface RecruitingPortalData {
  candidates: CandidateProfile[];
  pipeline: PipelineMetrics;
  total_candidates: number;
}
