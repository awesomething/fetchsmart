"use client";

import React, {
  createContext,
  useContext,
  useRef,
  useCallback,
  useEffect,
  useState,
} from "react";
import { flushSync } from "react-dom";

import { useSession } from "@/hooks/useSession";
import { useMessages } from "@/hooks/useMessages";
import { useStreamingManager } from "@/components/chat/StreamingManager";
import { Message } from "@/types";
import { CandidateProfile } from "@/types/recruiting";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { toast } from "sonner";
import { loadSessionHistoryAction } from "@/lib/actions/session-history-actions";
import { parseCandidatesFromMessage } from "@/lib/utils/candidate-parser";

type EmailPipelineStage = "generating" | "reviewing" | "refining" | "presenting";

const EMAIL_STAGE_COPY: Record<EmailPipelineStage, string> = {
  generating: "✉️ Generating personalized email draft...",
  reviewing: "🔍 Reviewing the draft for personalization and tone...",
  refining: "🎯 Refining the copy with GitHub profile insights...",
  presenting: "✨ Preparing the final recruiting email...",
};

type EmployerWorkflowStage = "transferring" | "creating" | "reviewing" | "analyzing" | "assessing" | "preparing";

const EMPLOYER_STAGE_COPY: Record<EmployerWorkflowStage, string> = {
  transferring: "🔄 Transferring to employer review agent...",
  creating: "📝 Creating candidate submission...",
  reviewing: "📋 Reviewing candidate submission and resume...",
  analyzing: "🔍 Analyzing qualifications and skills match...",
  assessing: "⚖️ Assessing experience level and job fit...",
  preparing: "✨ Preparing candidate assessment...",
};

const EMAIL_FINAL_MARKER = "**Recruiting Email Draft**";
const EMAIL_REVIEW_MARKERS = [
  "Email approved.",
  "Ready to send",
  "latest draft produced by the generator/refiner",
  "Email approved. Ready to send.",
];
const EMAIL_JD_MARKERS = [
  "I need a job description",
  "I need the job description",
  "Please provide the job description",
];

const deduplicateParagraphs = (text: string): string => {
  if (!text || text.length < 20) {
    return text;
  }

  const paragraphs = text.split(/\n{2,}/);
  if (paragraphs.length < 2) {
    return text;
  }

  const seen = new Set<string>();
  const result: string[] = [];
  let removedDuplicate = false;

  for (const paragraph of paragraphs) {
    const trimmed = paragraph.trim();
    if (!trimmed) {
      continue;
    }
    if (seen.has(trimmed)) {
      removedDuplicate = true;
      continue;
    }
    seen.add(trimmed);
    result.push(paragraph.trim());
  }

  if (!removedDuplicate) {
    return text;
  }

  return result.join("\n\n");
};

function looksLikeEmailDraft(text: string): boolean {
  const lower = text.toLowerCase();
  // Don't treat the final presenter output as a draft
  if (text.includes(EMAIL_FINAL_MARKER)) {
    return false;
  }
  return (
    lower.includes("dear ") &&
    (lower.includes("best regards") ||
      lower.includes("sincerely") ||
      lower.includes("looking forward to hearing from you"))
  );
}

function extractEmailFromPresenterOutput(presenterOutput: string): string {
  // Extract the actual email content from the presenter's formatted output
  // The presenter wraps the email in markdown formatting
  const markerIndex = presenterOutput.indexOf(EMAIL_FINAL_MARKER);
  if (markerIndex === -1) {
    // No marker found, might be a direct email - check if it looks like an email
    if (looksLikeEmailDraft(presenterOutput)) {
      return presenterOutput;
    }
    return presenterOutput;
  }
  
  // Find the email content between the marker and the "Next Steps" section
  const afterMarker = presenterOutput.substring(markerIndex + EMAIL_FINAL_MARKER.length);
  const nextStepsIndex = afterMarker.indexOf("**Next Steps:**");
  
  if (nextStepsIndex === -1) {
    // No "Next Steps" section, extract everything after the marker
    const emailContent = afterMarker
      .replace(/^[\s\n]*Here's your personalized outreach email:[\s\n]*/i, "")
      .replace(/^---[\s\n]*/, "")
      .replace(/[\s\n]*---[\s\n]*$/, "")
      .trim();
    
    // If the extracted content is truncated (ends mid-sentence), try to find complete version
    if (emailContent && !emailContent.match(/(Best regards|Sincerely|Thank you).*$/i)) {
      // Email appears incomplete - this shouldn't happen, but return what we have
      console.warn("⚠️ [EMAIL EXTRACT] Email appears incomplete:", emailContent.substring(emailContent.length - 50));
    }
    
    return emailContent || presenterOutput;
  }
  
  // Extract content between marker and "Next Steps"
  const emailContent = afterMarker.substring(0, nextStepsIndex)
    .replace(/^[\s\n]*Here's your personalized outreach email:[\s\n]*/i, "")
    .replace(/^---[\s\n]*/, "")
    .replace(/[\s\n]*---[\s\n]*$/, "")
    .trim();
  
  // Validate email is complete
  if (emailContent && !emailContent.match(/(Best regards|Sincerely|Thank you).*$/i)) {
    console.warn("⚠️ [EMAIL EXTRACT] Email appears incomplete:", emailContent.substring(emailContent.length - 50));
  }
  
  return emailContent || presenterOutput;
}

function containsReviewFeedback(text: string): boolean {
  return EMAIL_REVIEW_MARKERS.some(marker => text.includes(marker));
}

function containsJobDescriptionRequest(text: string): boolean {
  return EMAIL_JD_MARKERS.some(marker => text.includes(marker));
}

/**
 * Smart routing: Infers the appropriate agent mode from user query
 * 
 * Priority order:
 * 1. Email generation requests
 * 2. Recruiter/candidate search requests (GitHub, candidates, engineers, developers)
 * 3. Planning requests
 * 4. Staffing recruiter requests (job search, match candidates)
 * 5. Staffing employer requests (review candidate, schedule interview)
 * 
 * Returns the inferred mode or undefined if no match
 */
function inferModeFromPrompt(
  text: string,
): "email" | "recruiter" | "planning" | "staffing_recruiter" | "staffing_employer" | undefined {
  const lower = text.toLowerCase().trim();
  
  // Priority 1: Email generation requests
  if (
    lower.startsWith("generate a personalized recruiting outreach email") ||
    lower.includes("personalized recruiting outreach email") ||
    lower.includes("professional recruiting email") ||
    lower.includes("write an outreach email") ||
    lower.includes("draft an email") ||
    (lower.includes("email") && (lower.includes("candidate") || lower.includes("outreach")))
  ) {
    return "email";
  }
  
  // Priority 2: Recruiter/candidate search requests
  // Keywords that indicate candidate sourcing/searching
  const recruiterKeywords = [
    // Search/find patterns
    "find", "search", "show me", "get", "list", "look for", "source",
    // Candidate-related
    "candidates", "candidate", "engineers", "engineer", "developers", "developer",
    "talent", "profiles", "github users", "github profiles",
    // Role-specific
    "senior", "junior", "mid-level", "full stack", "backend", "frontend",
    "devops", "sre", "data engineer", "ml engineer", "ai engineer",
    // Technology-specific
    "react", "python", "javascript", "typescript", "node", "java", "go", "rust",
    "kubernetes", "docker", "aws", "azure", "gcp",
    // GitHub-specific
    "github", "git hub", "on github", "from github",
    // Sourcing patterns
    "sourcing", "source candidates", "find candidates", "search for candidates"
  ];
  
  const hasRecruiterKeyword = recruiterKeywords.some(keyword => {
    // Check for word boundaries to avoid false positives
    const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    return regex.test(lower);
  });
  
  // Additional patterns that strongly indicate recruiter mode
  const recruiterPatterns = [
    /find\s+(senior|junior|mid|full|backend|frontend|devops|react|python|javascript|typescript|node|java|go|rust)\s+(engineer|developer|engineers|developers)/i,
    /search\s+for\s+(candidates|engineers|developers|talent)/i,
    /show\s+me\s+(candidates|engineers|developers)/i,
    /find\s+(candidates|engineers|developers)\s+on\s+github/i,
    /github\s+(users|profiles|engineers|developers|candidates)/i,
    /(senior|junior|mid|full|backend|frontend|devops)\s+(engineer|developer|engineers|developers)\s+on\s+github/i,
    /find\s+email\s+addresses\s+(for|of)\s+(these\s+)?github\s+users/i,
  ];
  
  const hasRecruiterPattern = recruiterPatterns.some(pattern => pattern.test(lower));
  
  if (hasRecruiterKeyword || hasRecruiterPattern) {
    // Exclude if it's clearly a staffing request
    if (lower.includes("job search") || lower.includes("match candidates to job")) {
      return "staffing_recruiter";
    }
    return "recruiter";
  }
  
  // Priority 3: Planning requests
  if (
    lower.startsWith("plan") ||
    lower.includes("plan my") ||
    lower.includes("create a plan") ||
    lower.includes("breakdown") ||
    lower.includes("task list") ||
    (lower.includes("plan") && (lower.includes("week") || lower.includes("schedule")))
  ) {
    return "planning";
  }
  
  // Priority 4: Staffing recruiter requests
  if (
    lower.includes("job search") ||
    lower.includes("find jobs") ||
    lower.includes("available jobs") ||
    lower.includes("match candidates to job") ||
    lower.includes("submit candidate") ||
    (lower.includes("staffing") && lower.includes("recruiter"))
  ) {
    return "staffing_recruiter";
  }
  
  // Priority 5: Staffing employer requests
  if (
    lower.includes("review candidate") ||
    lower.includes("schedule interview") ||
    lower.includes("hiring pipeline") ||
    lower.includes("candidate review") ||
    (lower.includes("employer") && (lower.includes("review") || lower.includes("candidate")))
  ) {
    return "staffing_employer";
  }
  
  return undefined;
}

// Context value interface - consolidates all chat state and actions
export interface ChatContextValue {
  // Session state
  userId: string;
  sessionId: string;

  // Message state
  messages: Message[];
  messageEvents: Map<string, ProcessedEvent[]>;
  websiteCount: number;

  // Loading state
  isLoading: boolean;
  isLoadingHistory: boolean; // New loading state for session history
  currentAgent: string;
  agentMode: "auto" | "planning" | "qa" | "recruiter" | "email" | "staffing_recruiter" | "staffing_employer";
  setAgentMode: (
    mode: "auto" | "planning" | "qa" | "recruiter" | "email" | "staffing_recruiter" | "staffing_employer"
  ) => void;

  // Recruitment state
  candidates: CandidateProfile[] | null;
  setCandidates: (candidates: CandidateProfile[] | null) => void;
  isLoadingCandidates: boolean;
  setIsLoadingCandidates: (loading: boolean) => void;

  // Session actions
  handleUserIdChange: (newUserId: string) => void;
  handleUserIdConfirm: (confirmedUserId: string) => void;
  handleCreateNewSession: (sessionUserId: string) => Promise<void>;
  handleSessionSwitch: (newSessionId: string) => void;

  // Message actions
  handleSubmit: (
    query: string,
    requestUserId?: string,
    requestSessionId?: string,
    modeOverride?: "auto" | "planning" | "qa" | "recruiter" | "email" | "staffing_recruiter" | "staffing_employer"
  ) => Promise<void>;
  addMessage: (message: Message) => void;

  // Refs for external access
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
}

interface ChatProviderProps {
  children: React.ReactNode;
}

// Create context
const ChatContext = createContext<ChatContextValue | null>(null);

/**
 * ChatProvider - Consolidated context provider for all chat state management
 * Combines useSession, useMessages, and useStreamingManager into single provider
 */
export function ChatProvider({
  children,
}: ChatProviderProps): React.JSX.Element {
  const scrollAreaRef = useRef<HTMLDivElement | null>(null);

  // Session history loading state
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Agent routing mode state
  const [agentMode, setAgentMode] = useState<
    "auto" | "planning" | "qa" | "recruiter" | "email" | "staffing_recruiter" | "staffing_employer"
  >("auto");

  // Recruitment candidates state
  const [candidates, setCandidates] = useState<CandidateProfile[] | null>(null);
  const [isLoadingCandidates, setIsLoadingCandidates] = useState(false);

  // Consolidate all hooks
  const {
    userId,
    sessionId,
    handleUserIdChange,
    handleUserIdConfirm,
    handleCreateNewSession,
    handleSessionSwitch,
  } = useSession();

  const {
    messages,
    messageEvents,
    websiteCount,
    addMessage,
    setMessages,
    setMessageEvents,
    updateWebsiteCount,
  } = useMessages();

  const emailProgressMessageIdRef = useRef<string | null>(null);
  const employerProgressMessageIdRef = useRef<string | null>(null);
  const employerTransferDetectedRef = useRef<boolean>(false);
  const lastProcessedMessageIdRef = useRef<string | null>(null);

  const startEmailProgressMessage = useCallback(() => {
    const placeholderId = `email-progress-${Date.now()}-${Math.random()
      .toString(36)
      .slice(2, 11)}`;
    emailProgressMessageIdRef.current = placeholderId;
    const placeholderMessage: Message = {
      type: "ai",
      content: EMAIL_STAGE_COPY.generating,
      id: placeholderId,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, placeholderMessage]);
  }, [setMessages]);

  const updateEmailProgressMessage = useCallback(
    (stage: EmailPipelineStage) => {
      const placeholderId = emailProgressMessageIdRef.current;
      if (!placeholderId) {
        return;
      }

      setMessages(prev =>
        prev.map(msg =>
          msg.id === placeholderId
            ? { ...msg, content: EMAIL_STAGE_COPY[stage] }
            : msg,
        ),
      );
    },
    [setMessages],
  );

  const completeEmailProgressMessage = useCallback(() => {
    const placeholderId = emailProgressMessageIdRef.current;
    if (!placeholderId) {
      return;
    }

    emailProgressMessageIdRef.current = null;
    setMessages(prev => prev.filter(msg => msg.id !== placeholderId));
  }, [setMessages]);

  const finalizeEmailProgressMessage = useCallback(
    (finalText: string) => {
      const placeholderId = emailProgressMessageIdRef.current;
      if (!placeholderId) {
        return;
      }

      setMessages(prev =>
        prev.map(msg =>
          msg.id === placeholderId
            ? {
                ...msg,
                content: finalText,
              }
            : msg,
        ),
      );

      emailProgressMessageIdRef.current = null;
    },
    [setMessages],
  );

  // Employer workflow progress messages
  const startEmployerProgressMessage = useCallback(() => {
    const placeholderId = `employer-progress-${Date.now()}-${Math.random()
      .toString(36)
      .slice(2, 11)}`;
    employerProgressMessageIdRef.current = placeholderId;
    // Use a special marker so MessageItem can detect and render progress bar
    const placeholderMessage: Message = {
      type: "ai",
      content: `**EMPLOYER_PROGRESS:transferring**\n${EMPLOYER_STAGE_COPY.transferring}`,
      id: placeholderId,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, placeholderMessage]);
  }, [setMessages]);

  const updateEmployerProgressMessage = useCallback(
    (stage: EmployerWorkflowStage) => {
      const placeholderId = employerProgressMessageIdRef.current;
      if (!placeholderId) {
        return;
      }

      setMessages(prev =>
        prev.map(msg =>
          msg.id === placeholderId
            ? { ...msg, content: `**EMPLOYER_PROGRESS:${stage}**\n${EMPLOYER_STAGE_COPY[stage]}` }
            : msg,
        ),
      );
    },
    [setMessages],
  );

  const completeEmployerProgressMessage = useCallback(() => {
    const placeholderId = employerProgressMessageIdRef.current;
    if (!placeholderId) {
      return;
    }

    // Mark as complete before removing
    setMessages(prev =>
      prev.map(msg =>
        msg.id === placeholderId
          ? { ...msg, content: `**EMPLOYER_PROGRESS:complete**\n✅ Review complete!` }
          : msg,
      ),
    );

    // Remove after a brief delay to show completion
    setTimeout(() => {
      employerProgressMessageIdRef.current = null;
      setMessages(prev => prev.filter(msg => msg.id !== placeholderId));
    }, 1000);
  }, [setMessages]);

  // Streaming management
  const streamingManager = useStreamingManager({
    userId,
    sessionId,
    onMessageUpdate: (message: Message) => {
      console.log("🔄 [CHAT_PROVIDER] onMessageUpdate called:", {
        messageId: message.id,
        messageType: message.type,
        contentLength: message.content.length,
        hasContent: !!message.content,
      });

      const cleanedMessage: Message = {
        ...message,
        content: deduplicateParagraphs(message.content || ""),
      };

      const content = cleanedMessage.content || "";
      const isFinalEmail = content.includes(EMAIL_FINAL_MARKER);
      const needsJobDescription = containsJobDescriptionRequest(content);
      const isReviewFeedback = containsReviewFeedback(content);
      const draftLike = looksLikeEmailDraft(content);
      const isError = /\b(error|failed|unable|cannot|missing)\b/i.test(content);
      let shouldHideEmailMessage = false;

      // Start employer progress bar AFTER the initial AI response
      // BUT only if the agent is NOT requesting JD summary
      const isRequestingJDSummary = 
        content.toLowerCase().includes("job description") ||
        content.toLowerCase().includes("jd summary") ||
        content.toLowerCase().includes("need the job description") ||
        content.toLowerCase().includes("please provide") && content.toLowerCase().includes("job") ||
        content.toLowerCase().includes("first, i need");
      
      if (
        message.type === "ai" &&
        employerTransferDetectedRef.current &&
        !employerProgressMessageIdRef.current &&
        content.length > 50 &&
        !isRequestingJDSummary &&
        (content.toLowerCase().includes("i will review") ||
         content.toLowerCase().includes("i will assess") ||
         content.toLowerCase().includes("okay, i will") ||
         content.toLowerCase().includes("i'll review") ||
         content.toLowerCase().includes("reviewing candidate") ||
         content.toLowerCase().includes("assessing candidate"))
      ) {
        console.log("🔄 [CHAT_PROVIDER] Initial employer response detected (with JD summary), starting progress bar");
        employerTransferDetectedRef.current = false; // Reset flag
        // Start progress bar after a brief delay to let the message render first
        setTimeout(() => {
          startEmployerProgressMessage();
          updateEmployerProgressMessage("reviewing");
        }, 300);
      } else if (isRequestingJDSummary && employerTransferDetectedRef.current) {
        // Agent is requesting JD summary - don't start progress bar yet
        console.log("🔄 [CHAT_PROVIDER] Agent requesting JD summary - progress bar will start after JD is provided");
        employerTransferDetectedRef.current = false; // Reset flag, will be set again when JD is provided
      }

      // Start progress bar when JD summary is provided (user response after agent request)
      // Check if this is a user message that might contain JD summary
      if (
        message.type === "human" &&
        !employerProgressMessageIdRef.current &&
        content.length > 20 &&
        (content.toLowerCase().includes("jd summary") ||
         content.toLowerCase().includes("job description") ||
         content.toLowerCase().includes("must have") ||
         content.toLowerCase().includes("nice to have") ||
         content.toLowerCase().includes("responsibilities"))
      ) {
        // User likely provided JD summary - set flag to start progress on next AI response
        console.log("🔄 [CHAT_PROVIDER] User message likely contains JD summary, will start progress on next AI response");
        employerTransferDetectedRef.current = true;
      }

      // Handle employer workflow progress completion
      if (
        message.type === "ai" &&
        employerProgressMessageIdRef.current &&
        content.length > 50 &&
        !content.includes(EMPLOYER_STAGE_COPY.transferring) &&
        !content.includes(EMPLOYER_STAGE_COPY.creating) &&
        !content.includes(EMPLOYER_STAGE_COPY.reviewing) &&
        !content.includes(EMPLOYER_STAGE_COPY.analyzing) &&
        !content.includes(EMPLOYER_STAGE_COPY.assessing) &&
        !content.includes(EMPLOYER_STAGE_COPY.preparing) &&
        !content.includes("**EMPLOYER_PROGRESS:")
      ) {
        // Check if this looks like a final assessment/recommendation
        const looksLikeFinalResponse = 
          content.toLowerCase().includes("recommendation") ||
          content.toLowerCase().includes("assessment") ||
          content.toLowerCase().includes("proceed to interview") ||
          content.toLowerCase().includes("reject the candidate") ||
          content.toLowerCase().includes("request more information");
        
        if (looksLikeFinalResponse) {
          // Final response arrived, complete progress message
          completeEmployerProgressMessage();
        }
      }

      // Parse candidates from AI messages when in recruiter mode
      // Check both agentMode and message content to handle smart routing
      const isRecruiterMode = agentMode === "recruiter";
      const hasCandidateData = message.content && (
        message.content.includes('top_candidates') ||
        message.content.includes('"candidates"') ||
        (message.content.includes('github_username') && message.content.includes('match_score')) ||
        (message.content.includes('"query"') && message.content.includes('"total_matches"'))
      );
      
      if (
        message.type === "ai" &&
        (isRecruiterMode || hasCandidateData) &&
        message.content
      ) {
        console.log("🔍 [CHAT_PROVIDER] Attempting to parse candidates from message:", {
          messageId: message.id,
          contentLength: message.content.length,
          contentPreview: message.content.substring(0, 200),
          isRecruiterMode,
          hasCandidateData,
        });
        
        const parsedCandidates = parseCandidatesFromMessage(message.content);
        
        if (parsedCandidates && parsedCandidates.length > 0) {
          console.log("✅ [CHAT_PROVIDER] Successfully parsed candidates:", {
            count: parsedCandidates.length,
            messageId: message.id,
            firstCandidate: parsedCandidates[0]?.name,
          });
          setCandidates(parsedCandidates);
          setIsLoadingCandidates(false); // Stop loading when candidates are found
        } else {
          console.log("⚠️ [CHAT_PROVIDER] No candidates found in message:", {
            messageId: message.id,
            hasTopCandidates: message.content.includes('top_candidates'),
            hasQuery: message.content.includes('"query"'),
          });
          // Don't stop loading here - let the re-parsing effect handle it
          // This allows for partial JSON that might complete later
        }
      }

      if (message.type === "ai") {
        if (isFinalEmail && emailProgressMessageIdRef.current) {
          // Extract just the email content from the presenter output
          const emailContent = extractEmailFromPresenterOutput(message.content);
          finalizeEmailProgressMessage(emailContent);
          return;
        }

        const pipelineActive = emailProgressMessageIdRef.current !== null;
        if (pipelineActive) {
          if (needsJobDescription || isError) {
            completeEmailProgressMessage();
          } else if (isReviewFeedback) {
            updateEmailProgressMessage("reviewing");
            shouldHideEmailMessage = true;
          } else if (draftLike && !isFinalEmail) {
            // Hide draft emails UNLESS it's the final presenter output
            updateEmailProgressMessage("refining");
            shouldHideEmailMessage = true;
          }
        } else if ((draftLike && !isFinalEmail) || isReviewFeedback) {
          // Hide drafts and review feedback when pipeline is not active
          shouldHideEmailMessage = true;
        }
      }

      if (shouldHideEmailMessage) {
        return;
      }

      // 🔑 CRITICAL: Use flushSync to force immediate UI update for real-time streaming
      // This prevents React from batching updates and ensures text appears as it streams
      flushSync(() => {
        setMessages(prev => {
          const existingMessage = prev.find((msg) => msg.id === cleanedMessage.id);
          console.log("🔍 [CHAT_PROVIDER] Message state check:", {
            messageId: cleanedMessage.id,
            existingMessage: !!existingMessage,
            totalMessages: prev.length,
            lastMessageType:
              prev.length > 0 ? prev[prev.length - 1].type : "none",
          });

          if (existingMessage) {
            console.log("🔄 [CHAT_PROVIDER] Updating existing message");
            return prev.map((msg) =>
              msg.id === cleanedMessage.id
                ? {
                    ...existingMessage,
                    ...cleanedMessage,
                  }
                : msg
            );
          } else {
            const newMessage: Message = {
              ...cleanedMessage,
              timestamp: cleanedMessage.timestamp || new Date(),
            };
            console.log("✅ [CHAT_PROVIDER] Creating new message:", {
              id: newMessage.id,
              type: newMessage.type,
              contentLength: newMessage.content.length,
            });
            const newMessages = [...prev, newMessage];
            console.log("📊 [CHAT_PROVIDER] Updated messages array:", {
              totalMessages: newMessages.length,
              lastMessageType: newMessages[newMessages.length - 1].type,
            });
            return newMessages;
          }
        });
      });
    },
    onEventUpdate: (messageId, event) => {
      console.log("📅 [CHAT_PROVIDER] onEventUpdate called:", {
        messageId,
        eventTitle: event.title,
        eventType:
          typeof event.data === "object" && event.data && "type" in event.data
            ? event.data.type
            : undefined,
        isThought: event.title.startsWith("🤔"),
      });

      // Detect employer agent transfer - flag it but don't start progress yet
      // Progress will only start if agent is NOT requesting JD summary
      if (
        event.title === "Function Call: transfer_to_agent" &&
        event.data &&
        typeof event.data === "object" &&
        "args" in event.data &&
        event.data.args &&
        typeof event.data.args === "object" &&
        "agent_name" in event.data.args &&
        event.data.args.agent_name === "StaffingEmployerOrchestrator"
      ) {
        console.log("🔄 [CHAT_PROVIDER] Detected employer agent transfer, will start progress after JD summary is provided");
        employerTransferDetectedRef.current = true;
      }

      // Update employer progress based on function calls
      if (
        employerProgressMessageIdRef.current &&
        event.title.startsWith("Function Call:")
      ) {
        const functionName = event.title.replace("Function Call: ", "");
        if (functionName === "create_candidate_submission") {
          updateEmployerProgressMessage("creating");
        } else if (functionName === "get_candidate_resume" || functionName === "get_pipeline_status") {
          updateEmployerProgressMessage("reviewing");
        } else if (functionName === "search_jobs") {
          updateEmployerProgressMessage("analyzing");
        } else if (functionName === "update_pipeline_stage") {
          updateEmployerProgressMessage("preparing");
        }
      }

      // Update progress when function response is received (resume data retrieved)
      if (
        employerProgressMessageIdRef.current &&
        event.title.startsWith("Function Response:")
      ) {
        const functionName = event.title.replace("Function Response: ", "");
        if (functionName === "get_candidate_resume") {
          // Resume was retrieved, agent will now analyze it
          updateEmployerProgressMessage("analyzing");
        }
      }

      // Update progress when thoughts appear (agent is analyzing)
      if (
        employerProgressMessageIdRef.current &&
        event.title.startsWith("🤔")
      ) {
        updateEmployerProgressMessage("analyzing");
      }

      setMessageEvents((prev) => {
        const newMap = new Map(prev);
        const existingEvents = newMap.get(messageId) || [];
        console.log("🔍 [CHAT_PROVIDER] Event state check:", {
          messageId,
          existingEventsCount: existingEvents.length,
          eventTitle: event.title,
        });

        // Handle thinking activities with progressive content accumulation
        if (event.title.startsWith("🤔")) {
          const existingThinkingIndex = existingEvents.findIndex(
            (existingEvent) => existingEvent.title === event.title
          );

          if (existingThinkingIndex >= 0) {
            // Accumulate content progressively instead of replacing
            const updatedEvents = [...existingEvents];
            const existingEvent = updatedEvents[existingThinkingIndex];
            const existingData =
              existingEvent.data && typeof existingEvent.data === "object"
                ? existingEvent.data
                : {};
            const existingContent =
              "content" in existingData ? String(existingData.content) : "";
            const newContent =
              event.data &&
              typeof event.data === "object" &&
              "content" in event.data
                ? String(event.data.content)
                : "";

            // Accumulate content (don't replace - add new content)
            const accumulatedContent = existingContent
              ? `${existingContent}\n\n${newContent}`
              : newContent;

            updatedEvents[existingThinkingIndex] = {
              ...existingEvent,
              data: {
                ...existingData,
                content: accumulatedContent,
              },
            };
            newMap.set(messageId, updatedEvents);
          } else {
            // Add new thinking activity (each distinct thought title)
            newMap.set(messageId, [...existingEvents, event]);
          }
        } else {
          // For non-thinking activities, add normally (no deduplication needed)
          newMap.set(messageId, [...existingEvents, event]);
        }

        return newMap;
      });
    },
    onWebsiteCountUpdate: updateWebsiteCount,
  });

  // Load session history when session changes
  useEffect(() => {
    if (userId && sessionId) {
      // Function to load session history
      const loadSessionHistory = async () => {
        try {
          console.log("🔄 [CHAT_PROVIDER] Loading session history:", {
            userId,
            sessionId,
          });

          setIsLoadingHistory(true);

          // Clear current state
          setMessages([]);
          setMessageEvents(new Map());
          updateWebsiteCount(0);

          // Load session history using Server Action (keeps Google Auth on server)
          const result = await loadSessionHistoryAction(userId, sessionId);

          if (result.success) {
            console.log(
              "✅ [CHAT_PROVIDER] Session history loaded successfully:",
              {
                messagesCount: result.messages.length,
                eventsCount: result.messageEvents.size,
              }
            );

            // Set historical messages
            if (result.messages.length > 0) {
              setMessages(result.messages);
            }

            // Set timeline events
            if (result.messageEvents.size > 0) {
              setMessageEvents(result.messageEvents);
            }

            console.log("✅ [CHAT_PROVIDER] Session history applied to state");
          } else {
            console.warn(
              "⚠️ [CHAT_PROVIDER] Session history loading failed:",
              result.error
            );

            // Show error toast to user
            toast.error("Failed to load chat history", {
              description:
                result.error ||
                "Could not load previous messages for this session.",
            });
          }
        } catch (error) {
          console.error(
            "❌ [CHAT_PROVIDER] Error loading session history:",
            error
          );

          // Show error toast to user
          toast.error("Network error", {
            description:
              "Could not connect to load chat history. Please check your connection.",
          });

          // On error, just clear state and continue (graceful degradation)
          setMessages([]);
          setMessageEvents(new Map());
          updateWebsiteCount(0);
        } finally {
          setIsLoadingHistory(false);
        }
      };

      // Load session history
      loadSessionHistory();
    }
  }, [userId, sessionId, setMessages, setMessageEvents, updateWebsiteCount]);

  // Clear candidates when switching away from recruiter mode
  // BUT: Don't clear if we have candidate data in the latest message (smart routing case)
  useEffect(() => {
    if (agentMode !== "recruiter" && agentMode !== "email" && candidates !== null) {
      // Check if the latest message contains candidate data (smart routing scenario)
      const latestAiMessage = [...messages]
        .reverse()
        .find(msg => msg.type === "ai");
      
      const hasCandidateDataInLatestMessage = latestAiMessage?.content && (
        latestAiMessage.content.includes('top_candidates') ||
        latestAiMessage.content.includes('"candidates"') ||
        (latestAiMessage.content.includes('github_username') && latestAiMessage.content.includes('match_score'))
      );
      
      // Only clear if there's no candidate data in the latest message
      // This prevents clearing candidates when smart routing is used
      if (!hasCandidateDataInLatestMessage) {
        console.log("🧹 [CHAT_PROVIDER] Clearing candidates (mode changed from recruiter)");
        setCandidates(null);
      } else {
        console.log("ℹ️ [CHAT_PROVIDER] Keeping candidates (smart routing detected candidate data)");
      }
    }
  }, [agentMode, candidates, messages]);

  // Reset email progress indicator when leaving email mode
  useEffect(() => {
    if (agentMode !== "email") {
      completeEmailProgressMessage();
    }
  }, [agentMode, completeEmailProgressMessage]);

  useEffect(() => {
    return () => {
      completeEmailProgressMessage();
    };
  }, [completeEmailProgressMessage]);

  // Re-parse candidates from latest AI message when messages change
  // This ensures we catch candidates even if parsing failed during streaming
  // Also handles smart routing where agentMode might be "auto" but response is recruiter
  useEffect(() => {
    if (messages.length > 0) {
      // Find the latest AI message
      const latestAiMessage = [...messages]
        .reverse()
        .find(msg => msg.type === "ai");

      if (latestAiMessage && latestAiMessage.content) {
        // Skip if we've already processed this message
        if (lastProcessedMessageIdRef.current === latestAiMessage.id) {
          return;
        }

        // Check if message contains candidate data (handles smart routing)
        const hasCandidateData = 
          latestAiMessage.content.includes('top_candidates') ||
          latestAiMessage.content.includes('"candidates"') ||
          (latestAiMessage.content.includes('github_username') && latestAiMessage.content.includes('match_score')) ||
          (latestAiMessage.content.includes('"query"') && latestAiMessage.content.includes('"total_matches"'));
        
        // Only parse if in recruiter mode OR if message contains candidate data (smart routing)
        if (agentMode === "recruiter" || hasCandidateData) {
          // Always try to parse - update candidates if new ones are found
          // This allows updating candidates when new search results arrive
          console.log("🔄 [CHAT_PROVIDER] Re-parsing latest AI message for candidates", {
            agentMode,
            hasCandidateData,
            messageId: latestAiMessage.id,
          });
          const parsedCandidates = parseCandidatesFromMessage(latestAiMessage.content);
          
          // Mark this message as processed
          lastProcessedMessageIdRef.current = latestAiMessage.id;
          
          if (parsedCandidates && parsedCandidates.length > 0) {
            console.log("✅ [CHAT_PROVIDER] Re-parse successful:", {
              count: parsedCandidates.length,
              messageId: latestAiMessage.id,
            });
            setCandidates(parsedCandidates);
            setIsLoadingCandidates(false);
          } else if (hasCandidateData) {
            // If message has candidate indicators but parsing failed,
            // it might be incomplete JSON - wait a bit then stop loading
            const timeout = setTimeout(() => {
              console.log("⏱️ [CHAT_PROVIDER] Stopping loading after timeout (no candidates parsed)");
              setIsLoadingCandidates(false);
            }, 3000);
            return () => clearTimeout(timeout);
          } else {
            // If we're loading but message doesn't have candidate data, stop loading immediately
            // This handles cases where the response doesn't contain candidates
            console.log("🛑 [CHAT_PROVIDER] Stopping loading (no candidate data in message)");
            setIsLoadingCandidates(false);
          }
        }
      }
    }
  }, [messages, agentMode]); // Removed candidates and isLoadingCandidates from dependencies to prevent infinite loop

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        // Request animation frame ensures smooth scrolling during rapid updates
        requestAnimationFrame(() => {
          scrollViewport.scrollTop = scrollViewport.scrollHeight;
        });
      }
    }
  }, [messages]);

  // Handle message submission
  const handleSubmit = useCallback(
    async (
      query: string,
      requestUserId?: string,
      requestSessionId?: string,
      modeOverride?: "auto" | "planning" | "qa" | "recruiter" | "email" | "staffing_recruiter" | "staffing_employer"
    ): Promise<void> => {
      if (!query.trim()) return;

      // Use provided userId or current state
      const currentUserId = requestUserId || userId;
      if (!currentUserId) {
        throw new Error("User ID is required to send messages");
      }

      const inferredMode = inferModeFromPrompt(query);
      const effectiveMode =
        modeOverride ??
        inferredMode ??
        agentMode;
      
      // Log routing decision for debugging
      if (inferredMode) {
        console.log("🎯 [SMART_ROUTING] Detected mode from query:", {
          query: query.substring(0, 100),
          inferredMode,
          modeOverride: modeOverride || "none",
          currentAgentMode: agentMode,
          effectiveMode,
        });
      }
      
      // CRITICAL: Update agentMode state when smart routing detects a mode
      // This ensures the UI displays correctly (e.g., candidate cards show up)
      if (inferredMode && inferredMode !== agentMode && !modeOverride) {
        console.log("🔄 [SMART_ROUTING] Updating agentMode state to match inferred mode:", inferredMode);
        setAgentMode(inferredMode);
      }

      try {
        // Use provided session ID or current state, or create a new one if needed
        let currentSessionId = requestSessionId || sessionId;

        if (!currentSessionId) {
          console.log("No session ID found, creating new session...");
          await handleCreateNewSession(currentUserId);
          currentSessionId = sessionId; // Use the newly created session

        if (!currentSessionId) {
          throw new Error(
              "Failed to create session. Please try again."
          );
          }
        }

        // Add user message to chat immediately
        const userMessage: Message = {
          type: "human",
          content: query,
          id: `user-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
          timestamp: new Date(),
        };
        addMessage(userMessage);

        if (effectiveMode === "email") {
          completeEmailProgressMessage();
          startEmailProgressMessage();
        }

        // If recruiter mode, show loading and clear old candidates
        if (effectiveMode === "recruiter") {
          setIsLoadingCandidates(true);
          setCandidates(null); // Clear old candidates when starting new search
          lastProcessedMessageIdRef.current = null; // Reset processed message tracking
        }

        // Apply routing directive prefix based on selected agent mode
        const directivePrefix =
          effectiveMode === "planning"
            ? "[MODE:PLANNING] "
            : effectiveMode === "qa"
            ? "[MODE:QA] "
            : effectiveMode === "recruiter"
            ? "[MODE:RECRUITER] "
            : effectiveMode === "email"
            ? "[MODE:EMAIL] "
            : effectiveMode === "staffing_recruiter"
            ? "[MODE:STAFFING_RECRUITER] "
            : effectiveMode === "staffing_employer"
            ? "[MODE:STAFFING_EMPLOYER] "
            : "";

        // Submit message for streaming - the backend will provide AI response
        await streamingManager.submitMessage(directivePrefix + query);
      } catch (error) {
        console.error("Error submitting message:", error);
        // Don't create fake error messages - let the UI handle the error state
        throw error;
      }
    },
    [
      userId,
      sessionId,
      addMessage,
      streamingManager,
      agentMode,
      handleCreateNewSession,
      completeEmailProgressMessage,
      startEmailProgressMessage,
    ]
  );

  // Context value
  const contextValue: ChatContextValue = {
    // Session state
    userId,
    sessionId,

    // Message state
    messages,
    messageEvents,
    websiteCount,

    // Loading state
    isLoading: streamingManager.isLoading,
    isLoadingHistory,
    currentAgent: streamingManager.currentAgent,
    agentMode,
    setAgentMode,

    // Recruitment state
    candidates,
    setCandidates,
    isLoadingCandidates,
    setIsLoadingCandidates,

    // Session actions
    handleUserIdChange,
    handleUserIdConfirm,
    handleCreateNewSession,
    handleSessionSwitch,

    // Message actions
    handleSubmit,
    addMessage,

    // Refs
    scrollAreaRef,
  };

  return (
    <ChatContext.Provider value={contextValue}>{children}</ChatContext.Provider>
  );
}

/**
 * Custom hook for consuming chat context
 * Provides error handling when used outside provider
 */
export function useChatContext(): ChatContextValue {
  const context = useContext(ChatContext);

  if (!context) {
    throw new Error(
      "useChatContext must be used within a ChatProvider. " +
        "Make sure your component is wrapped with <ChatProvider>."
    );
  }

  return context;
}
