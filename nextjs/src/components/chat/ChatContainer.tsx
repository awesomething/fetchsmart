"use client";

import { useState, useEffect } from "react";
import { BackendHealthChecker } from "@/components/chat/BackendHealthChecker";
import { ChatHeader } from "./ChatHeader";
import { ChatContent } from "./ChatContent";
import { ChatInput } from "./ChatInput";
import { CandidateGrid } from "@/components/recruiting/CandidateGrid";
import { ResizableSplitPane } from "./ResizableSplitPane";
import { useChatContext } from "./ChatProvider";
import { CandidateProfile } from "@/types/recruiting";
import { Users, X } from "lucide-react";
import { WalkthroughOverlay } from "./WalkthroughOverlay";

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
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [showWelcomeVideo, setShowWelcomeVideo] = useState(false);
  const [showWalkthrough, setShowWalkthrough] = useState(false);

  // Check if user has seen the welcome video before
  useEffect(() => {
    const hasSeenWelcome = localStorage.getItem('hasSeenWelcomeVideo');
    if (!hasSeenWelcome) {
      // Delay slightly to ensure page is fully loaded
      const timer = setTimeout(() => setShowWelcomeVideo(true), 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  // Mark as seen when user closes the video and start walkthrough
  const handleCloseWelcomeVideo = () => {
    setShowWelcomeVideo(false);
    localStorage.setItem('hasSeenWelcomeVideo', 'true');

    // Start walkthrough after video closes
    const hasSeenWalkthrough = localStorage.getItem('hasSeenWalkthrough');
    if (!hasSeenWalkthrough) {
      setTimeout(() => setShowWalkthrough(true), 500);
    }
  };

  const handleCompleteWalkthrough = () => {
    setShowWalkthrough(false);
    localStorage.setItem('hasSeenWalkthrough', 'true');
  };

  const handleSkipWalkthrough = () => {
    setShowWalkthrough(false);
    localStorage.setItem('hasSeenWalkthrough', 'true');
  };

  // Use dynamic candidates if available, otherwise show mock candidates
  const displayCandidates = candidates && candidates.length > 0 ? candidates : mockCandidates;

  // Left Panel Content
  const leftPanel = (
    <div className="h-full flex flex-col bg-slate-900">
      <div className="flex-shrink-0 bg-slate-800/50 border-b border-slate-700 px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold text-slate-200 truncate">
              Enrich Candidate Profiles
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              {displayCandidates.length} profiles
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Feedback Button */}
            <button
              onClick={() => setIsFeedbackOpen(true)}
              className="bg-yellow-400 hover:bg-yellow-300 text-blue-900 font-bold py-2 px-3 sm:px-4 rounded-lg transition-colors duration-200 text-xs sm:text-sm whitespace-nowrap"
            >
              Feedback
            </button>
            {/* Mobile close button */}
            <button
              onClick={() => setIsMobileDrawerOpen(false)}
              className="md:hidden p-2 hover:bg-slate-700/50 rounded-lg transition-colors flex-shrink-0"
              aria-label="Close candidates"
            >
              <X className="h-5 w-5 text-slate-400" />
            </button>
          </div>
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

      {/* Feedback Modal */}
      {isFeedbackOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[200] flex items-center justify-center p-4"
          onClick={() => setIsFeedbackOpen(false)}
        >
          <div
            className="bg-slate-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <h2 className="text-lg font-semibold text-slate-100">Send Feedback</h2>
              <button
                onClick={() => setIsFeedbackOpen(false)}
                className="text-slate-400 hover:text-slate-100 transition-colors"
                aria-label="Close"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <iframe
                src="https://videobook-u42797.vm.elestio.app/form/3f84eff0-3703-4ac9-a703-84668c808179"
                className="w-full h-[70vh] border-0"
                title="Feedback Form"
              />
            </div>
          </div>
        </div>
      )}

      {/* Welcome Video Modal - First Time Visitors */}
      {showWelcomeVideo && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[250] flex items-center justify-center p-4"
          onClick={handleCloseWelcomeVideo}
        >
          <div
            className="bg-slate-800 rounded-lg shadow-2xl w-full max-w-4xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-gradient-to-r from-emerald-600 to-emerald-700">
              <div>
                <h2 className="text-xl font-bold text-white">Welcome to FetchSmart!</h2>
                <p className="text-sm text-emerald-100 mt-1">Watch this quick tutorial to get started</p>
              </div>
              <button
                onClick={handleCloseWelcomeVideo}
                className="text-white hover:text-emerald-100 transition-colors p-1 hover:bg-white/10 rounded-lg"
                aria-label="Close"
              >
                <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Video Content */}
            <div className="relative bg-black" style={{ paddingBottom: '56.25%' }}>
              <iframe
                className="absolute inset-0 w-full h-full"
                src="https://www.youtube.com/embed/Upr7zqxOOnU?autoplay=1&rel=0"
                title="FetchSmart Welcome Tutorial"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>

            {/* Footer */}
            <div className="p-4 bg-slate-800/50 border-t border-slate-700">
              <button
                onClick={handleCloseWelcomeVideo}
                className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
              >
                Got it! Let&apos;s get started
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Walkthrough Overlay - Step-by-step guide */}
      {showWalkthrough && (
        <WalkthroughOverlay
          onComplete={handleCompleteWalkthrough}
          onSkip={handleSkipWalkthrough}
        />
      )}
    </div>
  );
}
