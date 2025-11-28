"use client";

import { Dog } from "lucide-react";
import { UserIdInput } from "@/components/chat/UserIdInput";
import { SessionSelector } from "@/components/chat/SessionSelector";
import { useChatContext } from "@/components/chat/ChatProvider";
import { FloatingWindowMenu } from "@/components/chat/FloatingWindowMenu";
import { useContainerWidth } from "@/hooks/useContainerWidth";

/**
 * ChatHeader - User and session management interface
 * Extracted from ChatMessagesView header section
 * Handles user ID input and session selection
 * Stacks vertically when container is narrow (< 600px)
 */
export function ChatHeader(): React.JSX.Element {
  const {
    userId,
    sessionId,
    handleUserIdChange,
    handleUserIdConfirm,
    handleSessionSwitch,
    handleCreateNewSession,
  } = useChatContext();

  const [containerRef, containerWidth] = useContainerWidth<HTMLDivElement>();
  
  // Stack when container width is less than 600px (when right pane is dragged narrow)
  const shouldStack = containerWidth > 0 && containerWidth < 600;

  return (
    <div 
      ref={containerRef}
      className="relative z-10 flex-shrink-0 border-b border-slate-700/50 bg-slate-800/80 backdrop-blur-sm"
    >
      <div className={`max-w-5xl mx-auto w-full flex transition-all duration-300 ease-out ${
        shouldStack 
          ? 'flex-col gap-2.5 p-2.5' 
          : 'flex-row justify-between items-center gap-0 p-3 sm:p-4'
      }`}>
        {/* App branding - stacks above controls when narrow */}
        <div className={`flex items-center gap-2 sm:gap-3 min-w-0 ${shouldStack ? 'w-full pb-1' : 'flex-shrink'}`}>
          <div className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center shadow-md flex-shrink-0">
          <Dog className="h-3 w-3 sm:h-4 sm:w-4 text-white" />
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="text-sm sm:text-lg font-semibold text-slate-100 truncate">
              FetchSmart
            </h1>
            <p className={`text-xs text-slate-400 ${shouldStack ? 'hidden' : 'hidden sm:block'}`}>
              
            </p>
          </div>
        </div>

        {/* User controls - stacks below branding when narrow */}
        <div className={`flex items-center transition-all duration-300 ease-out ${
          shouldStack
            ? 'gap-2 flex-wrap w-full justify-start'
            : 'gap-2 sm:gap-4 flex-wrap sm:flex-nowrap w-full sm:w-auto justify-end'
        }`}>
          {/* Recruiter Hub Link */}
          {/* <Link
            href="/recruiter"
            className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-slate-100 hover:bg-slate-700/50 rounded-md transition-colors"
          >
            <Briefcase className="h-4 w-4" />
            <span>Recruiter Hub</span>
          </Link> */}

          {!shouldStack && (
            <div className="hidden sm:block sm:mr-3">
              <FloatingWindowMenu />
            </div>
          )}

          {/* FloatingWindowMenu - Mobile */}
          {shouldStack && (
            <div className="mr-2">
              <FloatingWindowMenu />
            </div>
          )}

          {/* User ID Management */}
          <UserIdInput
            currentUserId={userId}
            onUserIdChange={handleUserIdChange}
            onUserIdConfirm={handleUserIdConfirm}
            className="text-xs"
          />

          {/* Session Management */}
          {userId && (
            <SessionSelector
              currentUserId={userId}
              currentSessionId={sessionId}
              onSessionSelect={handleSessionSwitch}
              onCreateSession={handleCreateNewSession}
              className="text-xs"
            />
          )}
        </div>
      </div>
    </div>
  );
}
