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

