"use client";

import { useState } from "react";
import { BackendHealthChecker } from "@/components/chat/BackendHealthChecker";
import { ChatHeader } from "./ChatHeader";
import { ChatContent } from "./ChatContent";
import { ChatInput } from "./ChatInput";
import { CandidateGrid } from "@/components/recruiting/CandidateGrid";
import { ResizableSplitPane } from "./ResizableSplitPane";
import { useChatContext } from "./ChatProvider";
import { CandidateProfile } from "@/types/recruiting";
import { Users, X } from "lucide-react";

// Mock candidates for default display
const mockCandidates: CandidateProfile[] = [
  {
    id: "1",
    name: "awesomething",
    github_username: "awesomething",
    github_profile_url: "https://github.com/awesomething",
    role: "Senior Software Engineer",
    experience_level: "8 years exp",
    location: "Remote - US",
    primary_language: "Python",
    skills: ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "MCP"],
    github_stats: { repos: 342, stars: 285, followers: 27, commits: 3421 },
    match_score: 92,
    status: "Screening"
  },
  {
    id: "2",
    name: "Mithonmasud",
    github_username: "Mithonmasud",
    github_profile_url: "https://github.com/Mithonmasud",
    role: "Full Stack Engineer",
    experience_level: "6 years exp",
    location: "San Francisco, CA",
    primary_language: "TypeScript",
    skills: ["TypeScript", "React", "Node.js", "GraphQL", "PostgreSQL"],
    github_stats: { repos: 38, stars: 156, followers: 892, commits: 2156 },
    match_score: 88,
    status: "Technical Interview"
  },
  {
    id: "3",
    name: "Marquish",
    github_username: "Marquish",
    github_profile_url: "https://github.com/Marquish",
    role: "Backend Engineer",
    experience_level: "7 years exp",
    location: "Austin, TX",
    primary_language: "Go",
    skills: ["Go", "Rust", "Kubernetes", "Docker", "Microservices"],
    github_stats: { repos: 29, stars: 412, followers: 1589, commits: 4123 },
    match_score: 95,
    status: "System Design"
  },
  {
    id: "4",
    name: "Ekeneakubue",
    github_username: "Ekeneakubue",
    github_profile_url: "https://github.com/Ekeneakubue",
    role: "DevOps Engineer",
    experience_level: "5 years exp",
    location: "Remote - Global",
    primary_language: "AWS",
    skills: ["AWS", "Kubernetes", "Docker", "Terraform", "Python"],
    github_stats: { repos: 31, stars: 198, followers: 743, commits: 1876 },
    match_score: 86,
    status: "Applied"
  },
  {
    id: "5",
    name: "Sarah Chen",
    github_username: "sarahchen",
    github_profile_url: "https://github.com/sarahchen",
    role: "Frontend Engineer",
    experience_level: "4 years exp",
    location: "Seattle, WA",
    primary_language: "JavaScript",
    skills: ["React", "Vue.js", "TypeScript", "CSS", "Webpack"],
    github_stats: { repos: 52, stars: 324, followers: 567, commits: 2890 },
    match_score: 84,
    status: "Screening"
  },
  {
    id: "6",
    name: "Michael Kerr",
    github_username: "Olafaloofian",
    github_profile_url: "https://github.com/Olafaloofian",
    role: "Senior Full Stack Engineer",
    experience_level: "10 years exp",
    location: "Remote - US",
    primary_language: "Python",
    skills: ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes"],
    github_stats: { repos: 106, stars: 285, followers: 58, commits: 3421 },
    match_score: 87,
    status: "Technical Interview"
  },
  {
    id: "7",
    name: "xiiiiiiiiii",
    github_username: "xiiiiiiiiii",
    github_profile_url: "https://github.com/xiiiiiiiiii",
    role: "Data Engineer",
    experience_level: "10 years exp",
    location: "San Francisco, CA",
    primary_language: "Python",
    skills: ["Python", "Spark", "Airflow", "SQL", "Data Pipelines", "MCP"],
    github_stats: { repos: 27, stars: 178, followers: 312, commits: 1654 },
    match_score: 81,
    status: "Applied"
  },
  {
    id: "8",
    name: "Rowens72",
    github_username: "Rowens72",
    github_profile_url: "https://github.com/Rowens72",
    role: "Security Engineer",
    experience_level: "8 years exp",
    location: "London, UK",
    primary_language: "Rust",
    skills: ["Rust", "Security", "Dotnet", "C#", "Network Security", "Penetration Testing"],
    github_stats: { repos: 19, stars: 456, followers: 892, commits: 1432 },
    match_score: 93,
    status: "System Design"
  }
];

/**
 * ChatLayout - Professional split-screen layout with draggable divider
 * Left: Candidate profiles (resizable)
 * Right: Chat interface (resizable)
 * Mobile: Drawer-based candidate grid with toggle
 */
export function ChatContainer(): React.JSX.Element {
  const { candidates, isLoadingCandidates } = useChatContext();
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);
  
  // Use dynamic candidates if available, otherwise show mock candidates
  const displayCandidates = candidates && candidates.length > 0 ? candidates : mockCandidates;

  // Left Panel Content
  const leftPanel = (
    <div className="h-full flex flex-col bg-slate-900">
      <div className="flex-shrink-0 bg-slate-800/50 border-b border-slate-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-200">
              Enrich Candidate Profiles
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              {displayCandidates.length} profiles
            </p>
          </div>
          {/* Mobile close button */}
          <button
            onClick={() => setIsMobileDrawerOpen(false)}
            className="md:hidden p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
            aria-label="Close candidates"
          >
            <X className="h-5 w-5 text-slate-400" />
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-hidden min-h-0">
        <CandidateGrid 
          candidates={displayCandidates} 
          isLoading={isLoadingCandidates}
        />
      </div>
    </div>
  );

  // Right Panel Content
  const rightPanel = (
    <div className="h-full flex flex-col bg-slate-900">
      {/* Fixed Header - stays at top */}
      <div className="flex-shrink-0">
        <ChatHeader />
      </div>

      {/* Scrollable Messages Area - takes remaining space */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <ChatContent />
      </div>

      {/* Fixed Input Area - always at bottom */}
      <div className="flex-shrink-0">
        <ChatInput />
      </div>
    </div>
  );

  return (
    <div className="h-screen w-full bg-slate-900 relative overflow-hidden">
      <BackendHealthChecker>
        {/* Fixed background */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 pointer-events-none"></div>

        {/* Desktop: Resizable Split Pane */}
        <div className="hidden md:block h-full relative z-10">
          <ResizableSplitPane
            leftPanel={leftPanel}
            rightPanel={rightPanel}
            defaultLeftWidth={40}
            minLeftWidth={20}
            maxLeftWidth={70}
            storageKey="chat-split-pane-width"
          />
        </div>

        {/* Mobile: Full-width chat with drawer toggle */}
        <div className="md:hidden h-full relative z-10 flex flex-col">
          {/* Mobile Chat Interface */}
          <div className="h-full flex flex-col relative">
            {/* Mobile Candidates Toggle Button */}
            <button
              onClick={() => setIsMobileDrawerOpen(true)}
              className="absolute top-16 left-4 z-20 p-2 bg-slate-800/90 hover:bg-slate-700/90 rounded-lg shadow-lg border border-slate-700 transition-all"
              aria-label="View candidates"
            >
              <Users className="h-5 w-5 text-slate-300" />
            </button>

            {rightPanel}
          </div>

          {/* Mobile Drawer Overlay */}
          {isMobileDrawerOpen && (
            <>
              <div
                className="fixed inset-0 bg-black/60 z-30 backdrop-blur-sm"
                onClick={() => setIsMobileDrawerOpen(false)}
                aria-hidden="true"
              />
              <div className="fixed inset-y-0 left-0 w-[85%] max-w-sm z-40 transform transition-transform duration-300 ease-out">
                <div className="h-full bg-slate-900 shadow-2xl border-r border-slate-700">
                  {leftPanel}
                </div>
              </div>
            </>
          )}
        </div>
      </BackendHealthChecker>
    </div>
  );
}
