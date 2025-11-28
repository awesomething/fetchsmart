# Build Recruitment Frontend Interface in nextjs/

## Target Directory

All changes in `nextjs/` folder (NOT in `refs/ai_agent_rocket/frontend/`)

## Route Specification

Create at `/recruiting` route (NOT `/recruiter/portal`)

## Current State Analysis

- Target: `nextjs/src/app/recruiting/page.tsx` (new file)
- Existing: `nextjs/src/types/recruiting.ts` (needs update for MCP structure)
- Existing: `nextjs/src/lib/recruiting-api.ts` (update to connect to port 8100)
- Missing: Split-view page, candidate cards, chat integration, API routes

## Implementation Steps

### 1. Update Type Definitions

**File**: `nextjs/src/types/recruiting.ts`

Add types matching recruitment_backend MCP server response structure (keep existing types):

```typescript
// Add these interfaces to existing file
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
  };
  match_score?: number;
  match_reasons?: string[];
  matched_skills?: string[];
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
```

### 2. Create API Route for Initial Candidates

**File**: `nextjs/src/app/api/recruitment/candidates/route.ts`

Connect directly to recruitment_backend MCP server at port 8100:

```typescript
import { NextRequest, NextResponse } from 'next/server';

const RECRUITMENT_BACKEND_URL = process.env.RECRUITMENT_BACKEND_URL || 'http://localhost:8100';

export async function POST(request: NextRequest) {
  try {
    const { userId, query, limit = 10 } = await request.json();
    
    // Create A2A session with recruitment_backend
    const sessionResponse = await fetch(`${RECRUITMENT_BACKEND_URL}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_name: 'recruitment_system',
        user_id: userId || 'recruiter_1',
        state: { topic: 'recruiting' }
      })
    });
    
    if (!sessionResponse.ok) {
      throw new Error('Failed to create session');
    }
    
    const session = await sessionResponse.json();
    
    // Send query to agent (or default to show first candidates)
    const message = query || `Show me the first ${limit} candidates from the database`;
    
    const agentResponse = await fetch(`${RECRUITMENT_BACKEND_URL}/agent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_name: 'recruitment_system',
        user_id: userId || 'recruiter_1',
        session_id: session.id,
        new_message: {
          role: 'user',
          parts: [{ text: message }]
        },
        streaming: false
      })
    });
    
    if (!agentResponse.ok) {
      throw new Error('Failed to get agent response');
    }
    
    const agentData = await agentResponse.json();
    
    // Extract response text and parse candidate data
    const responseText = agentData.events?.[0]?.parts?.[0]?.text || '';
    
    return NextResponse.json({
      success: true,
      data: agentData,
      response_text: responseText,
      session_id: session.id
    });
    
  } catch (error) {
    console.error('Recruitment API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### 3. Create API Route for Chat

**File**: `nextjs/src/app/api/recruitment/chat/route.ts`

Chat endpoint for AI interactions with recruitment_backend:

```typescript
import { NextRequest, NextResponse } from 'next/server';

const RECRUITMENT_BACKEND_URL = process.env.RECRUITMENT_BACKEND_URL || 'http://localhost:8100';

export async function POST(request: NextRequest) {
  try {
    const { userId, message, sessionId } = await request.json();
    
    let currentSessionId = sessionId;
    
    // Create session if needed
    if (!currentSessionId) {
      const sessionResponse = await fetch(`${RECRUITMENT_BACKEND_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: 'recruitment_system',
          user_id: userId || 'recruiter_1',
          state: { topic: 'recruiting' }
        })
      });
      
      const session = await sessionResponse.json();
      currentSessionId = session.id;
    }
    
    // Send message to agent
    const agentResponse = await fetch(`${RECRUITMENT_BACKEND_URL}/agent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_name: 'recruitment_system',
        user_id: userId || 'recruiter_1',
        session_id: currentSessionId,
        new_message: {
          role: 'user',
          parts: [{ text: message }]
        },
        streaming: false
      })
    });
    
    const agentData = await agentResponse.json();
    
    // Extract text response from agent
    const responseText = agentData.events?.[0]?.parts?.[0]?.text || 'No response';
    
    return NextResponse.json({
      response: responseText,
      session_id: currentSessionId
    });
    
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### 4. Create Candidate Card Component

**File**: `nextjs/src/components/recruiting/CandidateCard.tsx`

Display GitHub profile cards matching the reference image:

```typescript
"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CandidateProfile } from "@/types/recruiting";
import { Github, Star, GitFork, Users } from "lucide-react";

export function CandidateCard({ candidate }: { candidate: CandidateProfile }) {
  return (
    <Card className="transition-all duration-300 hover:scale-[1.02] hover:shadow-lg border-border/50">
      <CardContent className="p-6">
        {/* Header with Avatar */}
        <div className="flex items-start gap-4 mb-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-cyan-500 flex items-center justify-center text-white font-bold text-xl flex-shrink-0">
            {candidate.name?.split(' ').map(n => n[0]).join('').slice(0, 2) || '??'}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-lg truncate">{candidate.name}</h3>
            <p className="text-sm text-muted-foreground truncate">
              @{candidate.github_username}
            </p>
          </div>
        </div>
        
        {/* Role and Experience */}
        <div className="mb-3">
          <p className="font-semibold text-sm">{candidate.role}</p>
          <p className="text-xs text-muted-foreground">
            {candidate.experience_level} • {candidate.location}
          </p>
        </div>
        
        {/* GitHub Stats */}
        <div className="flex gap-4 mb-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <GitFork className="h-4 w-4" />
            <span className="font-medium">{candidate.github_stats.repos}</span>
            <span className="text-xs">Repos</span>
          </div>
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4" />
            <span className="font-medium">{candidate.github_stats.stars}</span>
            <span className="text-xs">Stars</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            <span className="font-medium">{candidate.github_stats.followers}</span>
            <span className="text-xs">Followers</span>
          </div>
        </div>
        
        {/* Skills */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          <Badge variant="secondary" className="text-xs px-2 py-0.5">
            {candidate.primary_language}
          </Badge>
          {candidate.skills.slice(0, 4).map((skill) => (
            <Badge key={skill} variant="outline" className="text-xs px-2 py-0.5">
              {skill}
            </Badge>
          ))}
          {candidate.skills.length > 4 && (
            <Badge variant="outline" className="text-xs px-2 py-0.5">
              +{candidate.skills.length - 4}
            </Badge>
          )}
        </div>
        
        {/* Match Score */}
        {candidate.match_score !== undefined && (
          <div className="mb-4">
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-muted-foreground">Assessment</span>
              <span className="font-semibold text-primary">{candidate.match_score}/100</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-primary to-cyan-500 h-2 rounded-full transition-all"
                style={{ width: `${candidate.match_score}%` }}
              />
            </div>
          </div>
        )}
        
        {/* View Profile Button */}
        <Button variant="outline" size="sm" className="w-full" asChild>
          <a 
            href={candidate.github_profile_url} 
            target="_blank" 
            rel="noopener noreferrer"
          >
            <Github className="h-4 w-4 mr-2" />
            View Profile
          </a>
        </Button>
      </CardContent>
    </Card>
  );
}
```

### 5. Create Pipeline Metrics Component

**File**: `nextjs/src/components/recruiting/PipelineMetrics.tsx`

Display SOURCED/ADVANCED metrics matching the reference image:

```typescript
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import { PipelineMetrics } from "@/types/recruiting";

export function PipelineMetricsCard({ metrics }: { metrics: PipelineMetrics }) {
  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <Card className="border-green-500/20 bg-card/90 backdrop-blur-sm">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
                SOURCED
              </p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                {metrics.sourced}
              </p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card className="border-red-500/20 bg-card/90 backdrop-blur-sm">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
                ADVANCED
              </p>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                {metrics.advanced}
              </p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center">
              <TrendingDown className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

### 6. Create Main Recruiting Page at /recruiting

**File**: `nextjs/src/app/recruiting/page.tsx`

Split-view interface matching the reference image exactly:

```typescript
"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CandidateCard } from "@/components/recruiting/CandidateCard";
import { PipelineMetricsCard } from "@/components/recruiting/PipelineMetrics";
import { CandidateProfile, PipelineMetrics } from "@/types/recruiting";
import { Loader2, MessageSquare, Users, Send } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export default function RecruitingPage() {
  const [candidates, setCandidates] = useState<CandidateProfile[]>([]);
  const [pipeline, setPipeline] = useState<PipelineMetrics>({
    sourced: 0,
    advanced: 0,
    interviewed: 0,
    offered: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  // Load initial candidates on mount
  useEffect(() => {
    loadInitialCandidates();
  }, []);
  
  const loadInitialCandidates = async () => {
    try {
      setIsLoading(true);
      
      // For MVP, use mock data initially
      // Later: Parse actual response from MCP server
      setCandidates(mockCandidates);
      setPipeline({
        sourced: mockCandidates.length,
        advanced: 0,
        interviewed: 0,
        offered: 0
      });
      
      /* TODO: Connect to actual API
      const response = await fetch('/api/recruitment/candidates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: 'recruiter_1', limit: 10 })
      });
      const data = await response.json();
      // Parse and set candidates
      */
      
    } catch (error) {
      console.error('Failed to load candidates:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const sendChatMessage = async () => {
    if (!chatInput.trim() || isChatLoading) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: chatInput
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsChatLoading(true);
    
    try {
      const response = await fetch('/api/recruitment/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 'recruiter_1',
          message: chatInput,
          sessionId
        })
      });
      
      const data = await response.json();
      
      if (data.session_id) {
        setSessionId(data.session_id);
      }
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'No response'
      };
      
      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsChatLoading(false);
    }
  };
  
  return (
    <div className="flex h-screen bg-background">
      {/* Left Panel - Candidates Grid */}
      <div className="flex-1 border-r border-border/50 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border/50 bg-gradient-to-r from-background to-muted/20">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-primary to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
              <MessageSquare className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Let's talk about your hiring pipeline</h1>
              <p className="text-sm text-muted-foreground">
                I'm here to help you understand your candidate pipeline, improve GitHub sourcing, and make smarter recruiting decisions.
              </p>
            </div>
          </div>
          
          {/* Suggested Actions */}
          <div className="flex flex-col gap-2 text-sm">
            <p className="text-muted-foreground mb-1">Try asking me:</p>
            <button 
              onClick={() => setChatInput("Find senior engineers on GitHub")}
              className="text-left px-3 py-1.5 rounded-md hover:bg-accent/50 transition-colors flex items-center gap-2"
            >
              <span className="text-lg">🔍</span>
              <span>Find senior engineers on GitHub</span>
            </button>
            <button 
              onClick={() => setChatInput("Show me candidate pipeline by source")}
              className="text-left px-3 py-1.5 rounded-md hover:bg-accent/50 transition-colors flex items-center gap-2"
            >
              <span className="text-lg">📊</span>
              <span>Show me candidate pipeline by source</span>
            </button>
            <button 
              onClick={() => setChatInput("Where should we focus sourcing this week?")}
              className="text-left px-3 py-1.5 rounded-md hover:bg-accent/50 transition-colors flex items-center gap-2"
            >
              <span className="text-lg">📈</span>
              <span>Where should we focus sourcing this week?</span>
            </button>
            <button 
              onClick={() => setChatInput("Give me a weekly sourcing summary")}
              className="text-left px-3 py-1.5 rounded-md hover:bg-accent/50 transition-colors flex items-center gap-2"
            >
              <span className="text-lg">📋</span>
              <span>Give me a weekly sourcing summary</span>
            </button>
          </div>
        </div>
        
        {/* Scrollable Content */}
        <ScrollArea className="flex-1 p-6">
          <PipelineMetricsCard metrics={pipeline} />
          
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {candidates.map((candidate) => (
                <CandidateCard key={candidate.id} candidate={candidate} />
              ))}
            </div>
          )}
        </ScrollArea>
      </div>
      
      {/* Right Panel - AI Chat */}
      <div className="w-[500px] flex flex-col bg-muted/20">
        {/* Chat Header */}
        <div className="p-6 border-b border-border/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-cyan-500 rounded-lg flex items-center justify-center shadow-lg">
              <Users className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold">AI Recruiting Assistant</h2>
              <p className="text-xs text-muted-foreground">
                Ask me about candidates, sourcing, or analytics
              </p>
            </div>
          </div>
        </div>
        
        {/* Chat Messages */}
        <ScrollArea className="flex-1 p-6">
          {chatMessages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center text-muted-foreground">
              <div>
                <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-20" />
                <p className="text-sm">Start a conversation to search candidates</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-card border border-border'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isChatLoading && (
                <div className="flex justify-start">
                  <div className="bg-card border border-border rounded-lg p-3">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>
        
        {/* Chat Input */}
        <div className="p-4 border-t border-border/50">
          <div className="flex gap-2">
            <Input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendChatMessage()}
              placeholder="Ask me about candidates, GitHub sourcing, or recruiting metrics..."
              className="flex-1"
              disabled={isChatLoading}
            />
            <Button 
              onClick={sendChatMessage} 
              disabled={!chatInput.trim() || isChatLoading}
              size="icon"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}

// Mock data for initial MVP (8 candidates)
const mockCandidates: CandidateProfile[] = [
  {
    id: "GITHUB-001",
    name: "Rowens72",
    github_username: "Rowens72",
    github_profile_url: "https://github.com/Rowens72",
    role: "Senior Software Engineer",
    experience_level: "Senior",
    location: "Remote - US",
    primary_language: "Python",
    skills: ["Python", "JavaScript", "React", "TypeScript", "Node.js"],
    github_stats: { repos: 42, stars: 285, followers: 180 },
    match_score: 92
  },
  {
    id: "GITHUB-002",
    name: "Mithonmasud",
    github_username: "Mithonmasud",
    github_profile_url: "https://github.com/Mithonmasud",
    role: "Full Stack Engineer",
    experience_level: "Senior",
    location: "San Francisco, CA",
    primary_language: "TypeScript",
    skills: ["TypeScript", "React", "Node.js", "GraphQL", "Next.js"],
    github_stats: { repos: 38, stars: 156, followers: 124 },
    match_score: 88
  },
  {
    id: "GITHUB-003",
    name: "Sarah Chen",
    github_username: "sarahc",
    github_profile_url: "https://github.com/sarahc",
    role: "Backend Engineer",
    experience_level: "Mid",
    location: "Austin, TX",
    primary_language: "Go",
    skills: ["Go", "Kubernetes", "Docker", "PostgreSQL", "Redis"],
    github_stats: { repos: 29, stars: 412, followers: 203 },
    match_score: 85
  },
  {
    id: "GITHUB-004",
    name: "DevOps Dave",
    github_username: "ddave",
    github_profile_url: "https://github.com/ddave",
    role: "DevOps Engineer",
    experience_level: "Senior",
    location: "Remote - Global",
    primary_language: "Python",
    skills: ["AWS", "Kubernetes", "Terraform", "Python", "CI/CD"],
    github_stats: { repos: 31, stars: 198, followers: 145 },
    match_score: 90
  },
  {
    id: "GITHUB-005",
    name: "Frontend Fiona",
    github_username: "ffiona",
    github_profile_url: "https://github.com/ffiona",
    role: "Frontend Engineer",
    experience_level: "Mid",
    location: "New York, NY",
    primary_language: "JavaScript",
    skills: ["React", "Vue.js", "CSS", "TypeScript", "Tailwind"],
    github_stats: { repos: 45, stars: 321, followers: 289 },
    match_score: 87
  },
  {
    id: "GITHUB-006",
    name: "Security Sam",
    github_username: "securesam",
    github_profile_url: "https://github.com/securesam",
    role: "Security Engineer",
    experience_level: "Senior",
    location: "Seattle, WA",
    primary_language: "Rust",
    skills: ["Rust", "Security", "Cryptography", "C++", "Penetration Testing"],
    github_stats: { repos: 22, stars: 567, followers: 401 },
    match_score: 94
  },
  {
    id: "GITHUB-007",
    name: "Mobile Mike",
    github_username: "mmike",
    github_profile_url: "https://github.com/mmike",
    role: "Mobile Engineer",
    experience_level: "Mid",
    location: "Boston, MA",
    primary_language: "Swift",
    skills: ["Swift", "Kotlin", "React Native", "iOS", "Android"],
    github_stats: { repos: 33, stars: 245, followers: 178 },
    match_score: 82
  },
  {
    id: "GITHUB-008",
    name: "Data Diana",
    github_username: "datadiana",
    github_profile_url: "https://github.com/datadiana",
    role: "Data Engineer",
    experience_level: "Senior",
    location: "Remote - US",
    primary_language: "Python",
    skills: ["Python", "Spark", "Airflow", "SQL", "AWS"],
    github_stats: { repos: 27, stars: 189, followers: 156 },
    match_score: 86
  }
];
```

### 7. Environment Variables

**File**: `nextjs/.env.local` (create if doesn't exist)

```bash
RECRUITMENT_BACKEND_URL=http://localhost:8100
NEXT_PUBLIC_RECRUITING_API_URL=http://localhost:8100
```

### 8. Add Navigation Link (Optional)

If you want to add this to an existing sidebar/navigation:

- Update the relevant layout or navigation component
- Add link to `/recruiting` route
- Use Users or Briefcase icon from lucide-react

## Key Implementation Details

1. **Route**: Located at `/recruiting` (NOT `/recruiter/portal`)
2. **Backend**: Direct connection to recruitment_backend at port 8100 using A2A protocol
3. **Initial Data**: Mock data (8 candidates) shown on page load for MVP
4. **Pipeline Metrics**: Dynamically calculated from current results (Phase 1), will connect to actual API later (Phase 2)
5. **Split View**: Left panel (fluid) + Right panel (fixed 500px) matching reference image exactly
6. **Chat**: Full AI assistant integration with session management
7. **Responsive**: Cards grid adapts (1 col mobile, 2 cols desktop)

## Testing Checklist

1. Start recruitment_backend: `cd mcp_server/recruitment_backend && python server.py`
2. Start Next.js: `cd nextjs && npm run dev`
3. Navigate to `http://localhost:3000/recruiting`
4. Verify 8 mock candidates display with proper styling
5. Test pipeline metrics show correct counts
6. Test chat input and message display
7. Click suggested action buttons
8. Test GitHub profile links open correctly
9. Test responsive layout at different screen sizes