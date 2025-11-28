"use client";

import {
  CheckCircle2,
  Users,
  TrendingUp,
  MapPin,
  Code,
  Star,
  GitFork,
  Mail,
  MailCheck,
  MailX,
  Send,
  Briefcase,
  Calendar,
  ExternalLink,
} from "lucide-react";
import { useChatContext } from "@/components/chat/ChatProvider";
import { Button } from "@/components/ui/button";

interface JsonToHtmlRendererProps {
  content: string;
}

interface CandidateSearchResult {
  query?: string;
  job_title?: string;
  total_matches?: number;
  showing_top?: number;
  requirements_detected?: {
    skills?: string[];
    experience_level?: string;
    min_years?: number | null;
    location?: string | null;
    prefers_open_source?: boolean;
  };
  top_candidates: CandidateData[];
}

interface CandidateData {
  id?: string;
  name?: string;
  github_username?: string;
  role?: string;
  experience_level?: string;
  location?: string;
  primary_language?: string;
  match_score?: number;
  github_stats?: {
    repos?: number;
    stars?: number;
    followers?: number;
    commits?: number;
  };
  skills?: string[];
  match_reasons?: string[];
  email?: string | null;
  email_confidence?: number | null;
  email_source?: string | null;
}

interface FunctionResponse {
  result?: string;
}

interface JobSearchResult {
  status?: string;
  total_jobs?: number;
  jobs?: JobData[];
  data_source?: string;
  filters_applied?: {
    job_title?: string;
    location?: string;
    remote_only?: boolean;
    min_salary?: number;
    max_salary?: number;
  };
}

interface JobData {
  id?: string | number;
  job_title?: string;
  job_location?: string | null;
  job_apply_link?: string;
  job_min_salary?: string;
  job_max_salary?: string;
  job_description?: string;
  tech_stack?: string[];
  urgency?: string;
  status?: string;
}

interface CandidateSubmissionResult {
  status?: string;
  message?: string;
  submission?: {
    id?: string | number;
    submission_number?: string;
    job_opening_id?: number;
    name?: string;
    email?: string;
    status?: string;
    match_score?: number;
  };
}

interface HiringPipelineResult {
  status?: string;
  total_candidates?: number;
  pipeline_by_stage?: {
    [stage: string]: PipelineEntry[];
  };
}

interface PipelineEntry {
  id?: string;
  submission_id?: number;
  stage?: string;
  stage_status?: string;
  scheduled_date?: string;
  completed_date?: string;
  interviewer?: string;
  feedback?: string;
  resume_submissions?: {
    name?: string;
    job_opening_id?: number;
  };
}

/**
 * Converts JSON candidate search results to user-friendly HTML
 * Only converts if content is valid candidate search JSON
 */
export function JsonToHtmlRenderer({ content }: JsonToHtmlRendererProps) {
  const { handleSubmit, setAgentMode, setIsLoadingCandidates } = useChatContext();

  // Handler for generating personalized emails
  const handleGenerateEmail = (candidate: CandidateData) => {
    // Switch to email mode
    setAgentMode("email");
    
    // Create personalized email generation prompt with candidate context
    const prompt = `Generate a personalized recruiting outreach email for this candidate:

Name: ${candidate.name || candidate.github_username || 'Candidate'}
GitHub: @${candidate.github_username || 'unknown'}
Email: ${candidate.email || 'Not available'}
Role: ${candidate.role || 'Software Engineer'}
Experience: ${candidate.experience_level || 'Not specified'}
Location: ${candidate.location || 'Not specified'}
Primary Language: ${candidate.primary_language || 'Not specified'}
${candidate.skills && candidate.skills.length > 0 ? `Skills: ${candidate.skills.join(', ')}` : ''}
${candidate.github_stats ? `GitHub Stats: ${candidate.github_stats.repos || 0} repos, ${candidate.github_stats.stars || 0} stars, ${candidate.github_stats.followers || 0} followers` : ''}

Please generate a professional recruiting email that highlights their specific skills and experience.`;

    // Submit with email mode
    handleSubmit(prompt, undefined, undefined, "email");
  };

  const handleRequestCandidateEmails = (result: CandidateSearchResult) => {
    setAgentMode("recruiter");
    setIsLoadingCandidates(true);

    const contextLabel = result.job_title && result.query
      ? `${result.job_title} (${result.query})`
      : result.job_title || result.query || "this role";

    const prompt = `Please provide the email addresses for the candidates you just returned for ${contextLabel}. Use the find_candidate_emails_tool immediately so I can contact them.`;

    handleSubmit(prompt, undefined, undefined, "recruiter");
  };

  // Try to extract JSON from various formats
  let jsonString = content.trim();
  
  // Remove markdown code blocks if present
  const codeBlockMatch = jsonString.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
  if (codeBlockMatch) {
    jsonString = codeBlockMatch[1].trim();
  }
  
  // Try to parse as JSON
  let jsonData: unknown = null;
  try {
    jsonData = JSON.parse(jsonString);
  } catch {
    // Not JSON, return null to use default markdown renderer
    return null;
  }

  // Handle function response format: { "result": "{...json...}" }
  if (jsonData && typeof jsonData === 'object' && jsonData !== null) {
    const functionResponse = jsonData as FunctionResponse;
    if (functionResponse.result && typeof functionResponse.result === 'string') {
      try {
        jsonData = JSON.parse(functionResponse.result);
      } catch {
        // Can't parse nested JSON, continue with original
      }
    }
  }

  // Check if this is a job search result
  if (jsonData && typeof jsonData === 'object' && jsonData !== null) {
    const jobResult = jsonData as JobSearchResult;
    if (jobResult.jobs && Array.isArray(jobResult.jobs)) {
      return renderJobSearchResults(jobResult, handleSubmit, setAgentMode);
    }
  }

  // Check if this is a candidate submission result
  if (jsonData && typeof jsonData === 'object' && jsonData !== null) {
    const submissionResult = jsonData as CandidateSubmissionResult;
    if (submissionResult.submission && submissionResult.status === "success") {
      return renderCandidateSubmissions(submissionResult);
    }
  }

  // Check if this is a hiring pipeline result
  if (jsonData && typeof jsonData === 'object' && jsonData !== null) {
    const pipelineResult = jsonData as HiringPipelineResult;
    if (pipelineResult.pipeline_by_stage && typeof pipelineResult.pipeline_by_stage === 'object') {
      return renderHiringPipeline(pipelineResult);
    }
  }

  // Check if this is a candidate search result
  if (!jsonData || typeof jsonData !== 'object' || jsonData === null) {
    return null;
  }

  const searchResult = jsonData as CandidateSearchResult;
  if (!searchResult.top_candidates || !Array.isArray(searchResult.top_candidates)) {
    return null;
  }

  // Check if this is an email lookup result (has email fields)
  const hasEmailData = searchResult.top_candidates.some(
    (candidate: CandidateData) => candidate.email !== undefined && candidate.email !== null
  );

  // If this is an email lookup result, show email-focused view
  if (hasEmailData) {
    return renderEmailLookupResults(searchResult, handleGenerateEmail);
  }

  const { job_title, total_matches, showing_top, requirements_detected, top_candidates } = searchResult;

  return (
    <div className="space-y-4">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle2 className="h-5 w-5 text-green-400" />
          <h3 className="text-lg font-semibold text-slate-100">
            Search Results
          </h3>
        </div>
        <p className="text-slate-300 text-sm">
          Found <span className="font-semibold text-blue-400">{total_matches}</span> matching candidates
          {job_title && (
            <> for <span className="font-semibold text-blue-400">{job_title}</span></>
          )}
        </p>
        {showing_top && (
          <p className="text-slate-400 text-xs mt-1">
            Showing top {showing_top} candidates
          </p>
        )}
      </div>

      {/* Requirements Detected */}
      {requirements_detected && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3">
          <h4 className="text-sm font-medium text-slate-200 mb-2 flex items-center gap-2">
            <Code className="h-4 w-4" />
            Requirements Detected
          </h4>
          <div className="space-y-2">
            {requirements_detected.skills && requirements_detected.skills.length > 0 && (
              <div>
                <span className="text-xs text-slate-400">Skills: </span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {requirements_detected.skills.map((skill: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded text-xs border border-blue-500/30"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {requirements_detected.experience_level && (
              <div className="text-xs text-slate-400">
                Experience Level: <span className="text-slate-200">{requirements_detected.experience_level}</span>
              </div>
            )}
            {requirements_detected.min_years && (
              <div className="text-xs text-slate-400">
                Minimum Years: <span className="text-slate-200">{requirements_detected.min_years} years</span>
              </div>
            )}
            {requirements_detected.location && (
              <div className="text-xs text-slate-400 flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                <span className="text-slate-200">{requirements_detected.location}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Candidates Summary */}
      <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Users className="h-5 w-5 text-cyan-400" />
          <h4 className="text-base font-semibold text-slate-100">
            Top Candidates
          </h4>
        </div>
        <div className="space-y-3">
          {top_candidates.slice(0, 5).map((candidate: CandidateData, idx: number) => (
            <div
              key={candidate.id || idx}
              className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-3 hover:border-slate-600/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h5 className="font-semibold text-slate-100">
                    {candidate.name || candidate.github_username || 'Unknown'}
                  </h5>
                  {candidate.github_username && (
                    <p className="text-xs text-slate-400">@{candidate.github_username}</p>
                  )}
                </div>
                {candidate.match_score && (
                  <div className="flex items-center gap-1 px-2 py-1 bg-green-500/20 border border-green-500/30 rounded text-xs text-green-300">
                    <TrendingUp className="h-3 w-3" />
                    {candidate.match_score.toFixed(0)}% match
                  </div>
                )}
              </div>

              <div className="space-y-2 text-sm">
                {candidate.role && (
                  <div className="text-slate-300">
                    <span className="text-slate-400">Role: </span>
                    {candidate.role}
                  </div>
                )}
                {candidate.experience_level && (
                  <div className="text-slate-300">
                    <span className="text-slate-400">Experience: </span>
                    {candidate.experience_level}
                  </div>
                )}
                {candidate.location && (
                  <div className="text-slate-300 flex items-center gap-1">
                    <MapPin className="h-3 w-3 text-slate-400" />
                    <span>{candidate.location}</span>
                  </div>
                )}
                {candidate.primary_language && (
                  <div className="text-slate-300">
                    <span className="text-slate-400">Primary Language: </span>
                    <span className="text-cyan-400">{candidate.primary_language}</span>
                  </div>
                )}

                {/* GitHub Stats */}
                {candidate.github_stats && (
                  <div className="flex items-center gap-4 pt-2 border-t border-slate-700/30">
                    {candidate.github_stats.repos !== undefined && (
                      <div className="flex items-center gap-1 text-xs text-slate-400">
                        <GitFork className="h-3 w-3" />
                        <span>{candidate.github_stats.repos} repos</span>
                      </div>
                    )}
                    {candidate.github_stats.stars !== undefined && (
                      <div className="flex items-center gap-1 text-xs text-slate-400">
                        <Star className="h-3 w-3" />
                        <span>{candidate.github_stats.stars} stars</span>
                      </div>
                    )}
                    {candidate.github_stats.followers !== undefined && (
                      <div className="flex items-center gap-1 text-xs text-slate-400">
                        <Users className="h-3 w-3" />
                        <span>{candidate.github_stats.followers} followers</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Skills */}
                {candidate.skills && candidate.skills.length > 0 && (
                  <div className="pt-2">
                    <div className="flex flex-wrap gap-1.5">
                      {candidate.skills.slice(0, 5).map((skill: string, skillIdx: number) => (
                        <span
                          key={skillIdx}
                          className="px-2 py-0.5 bg-slate-700/50 text-slate-300 rounded text-xs border border-slate-600/50"
                        >
                          {skill}
                        </span>
                      ))}
                      {candidate.skills.length > 5 && (
                        <span className="px-2 py-0.5 bg-slate-700/30 text-slate-400 rounded text-xs">
                          +{candidate.skills.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Match Reasons */}
                {candidate.match_reasons && candidate.match_reasons.length > 0 && (
                  <div className="pt-2 space-y-1">
                    <p className="text-xs text-slate-400 mb-1">Why they match:</p>
                    <ul className="space-y-0.5">
                      {candidate.match_reasons.slice(0, 3).map((reason: string, reasonIdx: number) => (
                        <li key={reasonIdx} className="text-xs text-slate-300 flex items-start gap-1.5">
                          <span className="text-green-400 mt-0.5">✓</span>
                          <span>{reason.replace(/\\u2713/g, '✓').replace(/\\u2714/g, '✓')}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        {top_candidates.length > 5 && (
          <p className="text-xs text-slate-400 mt-3 text-center">
            ... and {top_candidates.length - 5} more candidates (see left panel for full list)
          </p>
        )}
      </div>

      <div className="bg-slate-900/40 border border-slate-700/60 rounded-xl p-4 space-y-3">
        <p className="text-sm text-slate-200">
          Would you like me to provide the email addresses of these candidates?
        </p>
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={() => handleRequestCandidateEmails(searchResult)}
            className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white shadow-lg"
          >
            Yes, provide the emails
          </Button>
          <Button
            variant="ghost"
            className="text-slate-300 hover:text-white border border-transparent hover:border-slate-600/60"
          >
            Not right now
          </Button>
        </div>
      </div>
    </div>
  );
}

/**
 * Renders email lookup results in a clean, email-focused format
 */
function renderEmailLookupResults(
  searchResult: CandidateSearchResult,
  onGenerateEmail: (candidate: CandidateData) => void
): React.JSX.Element {
  const { top_candidates, total_matches } = searchResult;
  
  const candidatesWithEmails = top_candidates.filter((c: CandidateData) => c.email);
  const candidatesWithoutEmails = top_candidates.filter((c: CandidateData) => !c.email || c.email === null);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <MailCheck className="h-5 w-5 text-green-400" />
          <h3 className="text-lg font-semibold text-slate-100">
            Email Lookup Results
          </h3>
        </div>
        <p className="text-slate-300 text-sm">
          Found emails for <span className="font-semibold text-green-400">{candidatesWithEmails.length}</span> out of <span className="font-semibold text-blue-400">{total_matches}</span> candidates
        </p>
      </div>

      {/* Candidates with Emails */}
      {candidatesWithEmails.length > 0 && (
        <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Mail className="h-5 w-5 text-green-400" />
            <h4 className="text-base font-semibold text-slate-100">
              Email Addresses Found
            </h4>
          </div>
          <div className="space-y-2">
            {candidatesWithEmails.map((candidate: CandidateData, idx: number) => (
              <div
                key={candidate.id || idx}
                className="bg-slate-900/50 border border-green-500/20 rounded-lg p-3 hover:border-green-500/40 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h5 className="font-semibold text-slate-100">
                        {candidate.name || candidate.github_username || 'Unknown'}
                      </h5>
                      {candidate.github_username && (
                        <span className="text-xs text-slate-400">@{candidate.github_username}</span>
                      )}
                    </div>
                    <a
                      href={`mailto:${candidate.email}`}
                      className="text-green-400 hover:text-green-300 hover:underline text-sm font-mono flex items-center gap-2"
                    >
                      <Mail className="h-4 w-4" />
                      {candidate.email}
                    </a>
                    {candidate.email_confidence && (
                      <p className="text-xs text-slate-400 mt-1">
                        Confidence: {candidate.email_confidence}%
                      </p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    onClick={() => onGenerateEmail(candidate)}
                    className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg flex items-center gap-2 shrink-0"
                  >
                    <Send className="h-3 w-3" />
                    <span className="text-xs">Generate Email</span>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Candidates without Emails */}
      {candidatesWithoutEmails.length > 0 && (
        <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <MailX className="h-5 w-5 text-slate-400" />
            <h4 className="text-base font-semibold text-slate-100">
              No Email Found
            </h4>
          </div>
          <div className="space-y-2">
            {candidatesWithoutEmails.map((candidate: CandidateData, idx: number) => (
              <div
                key={candidate.id || idx}
                className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-3"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium text-slate-300">
                    {candidate.name || candidate.github_username || 'Unknown'}
                  </span>
                  {candidate.github_username && (
                    <span className="text-xs text-slate-400">@{candidate.github_username}</span>
                  )}
                  <span className="text-xs text-slate-500 ml-auto">No email found</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Renders job search results from Supabase/JSearch API
 */
function renderJobSearchResults(
  result: JobSearchResult,
  handleSubmit: (
    query: string,
    requestUserId?: string,
    requestSessionId?: string,
    modeOverride?: "auto" | "planning" | "qa" | "recruiter" | "email" | "staffing_recruiter" | "staffing_employer"
  ) => Promise<void>,
  setAgentMode: (mode: "auto" | "planning" | "qa" | "recruiter" | "email" | "staffing_recruiter" | "staffing_employer") => void
): React.JSX.Element {
  const { jobs = [], total_jobs = 0, data_source, filters_applied } = result;

  const handleMatchCandidates = (jobId: string | number | undefined) => {
    if (!jobId) return;
    setAgentMode("staffing_recruiter");
    handleSubmit(`Match candidates to job opening ID ${jobId}`, undefined, undefined, "staffing_recruiter");
  };

  const handleViewJobDetails = (jobId: string | number | undefined) => {
    if (!jobId) return;
    setAgentMode("staffing_recruiter");
    handleSubmit(`Show details for job opening ID ${jobId}`, undefined, undefined, "staffing_recruiter");
  };

  const getUrgencyBadgeColor = (urgency?: string) => {
    switch (urgency?.toLowerCase()) {
      case "critical":
        return "bg-red-500/20 text-red-300 border-red-500/30";
      case "high":
        return "bg-orange-500/20 text-orange-300 border-orange-500/30";
      case "medium":
        return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
      default:
        return "bg-slate-500/20 text-slate-300 border-slate-500/30";
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Briefcase className="h-5 w-5 text-blue-400" />
            <h3 className="text-lg font-semibold text-slate-100">
              {total_jobs} Job Openings Found
            </h3>
          </div>
          {data_source && (
            <span className="text-xs px-2 py-1 bg-slate-700/50 text-slate-300 rounded border border-slate-600/50">
              Source: {data_source === "supabase" ? "Supabase" : "JSearch API"}
            </span>
          )}
        </div>
        {filters_applied && (
          <div className="text-xs text-slate-400 mt-2">
            {filters_applied.job_title && <span>Title: {filters_applied.job_title}</span>}
            {filters_applied.location && <span className="ml-3">Location: {filters_applied.location}</span>}
            {filters_applied.remote_only && <span className="ml-3">Remote only</span>}
          </div>
        )}
      </div>

      <div className="space-y-3">
        {jobs.map((job: JobData, idx: number) => (
          <div
            key={job.id || idx}
            className="border border-slate-700/50 rounded-lg p-4 bg-slate-800/30 hover:bg-slate-800/50 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h4 className="text-lg font-bold text-slate-100 mb-1">{job.job_title || "Untitled Position"}</h4>
                <div className="flex items-center gap-3 text-sm text-slate-400">
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {job.job_location || "Remote"}
                  </span>
                  {job.urgency && (
                    <span className={`px-2 py-0.5 rounded text-xs border ${getUrgencyBadgeColor(job.urgency)}`}>
                      {job.urgency}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {job.tech_stack && job.tech_stack.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2 mb-3">
                {job.tech_stack.map((tech: string) => (
                  <span
                    key={tech}
                    className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded border border-blue-500/30"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            )}

            <div className="mt-3 text-sm space-y-1">
              {job.job_location && (
                <p className="text-slate-300">
                  <strong className="text-slate-400">Location:</strong> {job.job_location}
                </p>
              )}
              {job.job_min_salary && job.job_max_salary && (
                <p className="text-slate-300">
                  <strong className="text-slate-400">Salary:</strong> ${parseFloat(job.job_min_salary).toLocaleString()} - ${parseFloat(job.job_max_salary).toLocaleString()}
                </p>
              )}
              {job.job_apply_link && (
                <p className="text-slate-300">
                  <strong className="text-slate-400">Apply:</strong>{" "}
                  <a
                    href={job.job_apply_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 hover:underline inline-flex items-center gap-1"
                  >
                    View Application <ExternalLink className="h-3 w-3" />
                  </a>
                </p>
              )}
            </div>

            <div className="mt-4 flex gap-2">
              <Button
                size="sm"
                onClick={() => handleMatchCandidates(job.id)}
                className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white"
              >
                Find Candidates
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleViewJobDetails(job.id)}
                className="border-slate-600 text-slate-300 hover:bg-slate-700/50"
              >
                View Details
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Renders candidate submission results
 */
function renderCandidateSubmissions(result: CandidateSubmissionResult): React.JSX.Element {
  const { submission, message } = result;

  if (!submission) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
        <p className="text-red-300">{message || "Submission failed"}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle2 className="h-5 w-5 text-green-400" />
          <h3 className="text-lg font-semibold text-slate-100">
            Candidate Submission Created
          </h3>
        </div>
        <p className="text-slate-300 text-sm">{message || "Submission created successfully"}</p>
      </div>

      <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4">
        <div className="space-y-2">
          {submission.submission_number && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Submission Number:</span>
              <span className="text-sm font-mono text-slate-200">{submission.submission_number}</span>
            </div>
          )}
          {submission.name && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Candidate:</span>
              <span className="text-sm text-slate-200">{submission.name}</span>
            </div>
          )}
          {submission.email && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Email:</span>
              <span className="text-sm text-slate-200">{submission.email}</span>
            </div>
          )}
          {submission.job_opening_id && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Job Opening ID:</span>
              <span className="text-sm text-slate-200">{submission.job_opening_id}</span>
            </div>
          )}
          {submission.status && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Status:</span>
              <span className="text-sm px-2 py-1 bg-green-500/20 text-green-300 rounded border border-green-500/30">
                {submission.status}
              </span>
            </div>
          )}
          {submission.match_score !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Match Score:</span>
              <span className="text-sm text-slate-200">{(submission.match_score * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Renders hiring pipeline status
 */
function renderHiringPipeline(result: HiringPipelineResult): React.JSX.Element {
  const { pipeline_by_stage = {}, total_candidates = 0 } = result;

  const stageLabels: { [key: string]: string } = {
    screening: "Screening",
    "technical-interview": "Technical Interview",
    "cultural-fit": "Cultural Fit",
    offer: "Offer",
    hired: "Hired",
  };

  const stageColors: { [key: string]: string } = {
    screening: "bg-blue-500/20 border-blue-500/30 text-blue-300",
    "technical-interview": "bg-purple-500/20 border-purple-500/30 text-purple-300",
    "cultural-fit": "bg-yellow-500/20 border-yellow-500/30 text-yellow-300",
    offer: "bg-green-500/20 border-green-500/30 text-green-300",
    hired: "bg-emerald-500/20 border-emerald-500/30 text-emerald-300",
  };

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <Calendar className="h-5 w-5 text-purple-400" />
          <h3 className="text-lg font-semibold text-slate-100">
            Hiring Pipeline Status
          </h3>
        </div>
        <p className="text-slate-300 text-sm">
          Total candidates in pipeline: <span className="font-semibold text-purple-400">{total_candidates}</span>
        </p>
      </div>

      <div className="space-y-3">
        {Object.entries(pipeline_by_stage).map(([stage, entries]) => (
          <div
            key={stage}
            className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <div className={`px-3 py-1 rounded text-sm font-medium border ${stageColors[stage] || "bg-slate-500/20 border-slate-500/30 text-slate-300"}`}>
                {stageLabels[stage] || stage}
              </div>
              <span className="text-sm text-slate-400">({entries.length} candidates)</span>
            </div>

            <div className="space-y-2">
              {entries.map((entry: PipelineEntry, idx: number) => (
                <div
                  key={entry.id || idx}
                  className="bg-slate-900/50 border border-slate-700/30 rounded-lg p-3"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h5 className="font-semibold text-slate-100">
                        {entry.resume_submissions?.name || `Submission #${entry.submission_id}`}
                      </h5>
                      {entry.stage_status && (
                        <span className="text-xs text-slate-400 capitalize">{entry.stage_status}</span>
                      )}
                    </div>
                  </div>

                  {entry.scheduled_date && (
                    <div className="text-xs text-slate-400 mb-1">
                      Scheduled: {new Date(entry.scheduled_date).toLocaleDateString()}
                    </div>
                  )}
                  {entry.interviewer && (
                    <div className="text-xs text-slate-400 mb-1">
                      Interviewer: {entry.interviewer}
                    </div>
                  )}
                  {entry.feedback && (
                    <div className="text-xs text-slate-300 mt-2 p-2 bg-slate-800/50 rounded border border-slate-700/30">
                      {entry.feedback}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

