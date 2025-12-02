"use client";

import { useChatContext } from "./ChatProvider";
import { Search, CheckSquare, Target, BarChart3, MessageCircle, Mail } from "lucide-react";

/**
 * EmptyState - Recruitment prompt templates
 * Displays when no messages exist in the current session
 */
export function EmptyState(): React.JSX.Element {
  const { handleSubmit } = useChatContext();

  // Prompt templates for recruitment
  type PromptTemplate = {
    icon: React.ComponentType<{ className?: string }>;
    text: string;
    query: string;
    mode?: "planning" | "staffing_recruiter" | "staffing_employer";
    variant?: "secondary";
  };

  const promptTemplates: PromptTemplate[] = [
    {
      icon: Search,
      text: "Find senior engineers on GitHub",
      query: "Find senior engineers on GitHub"
      // No mode specified - will use smart routing to detect "recruiter"
    },
    {
      icon: CheckSquare,
      text: "Plan my week for filling 3 Senior React Developer positions",
      query: "Plan my week for filling 3 Senior React Developer positions",
      mode: "planning" as const
    },
    // {
    //   icon: Target,
    //   text: "Find software engineer jobs in U.S",
    //   query: "Find software engineer jobs in U.S",
    //   mode: "staffing_recruiter" as const
    // },
    {
      icon: BarChart3,
      text: "Review candidate Craig with email info@videobook.ai",
      query: "Review candidate Craig with email timothy.lefkowitz@gmail.com",
      mode: "staffing_employer" as const
    },
    {
      icon: Mail,
      text: "How does this app work?",
      query: "How does this app work?",
      variant: "secondary" as const
    }
  ];

  const handlePromptClick = (query: string, mode?: "planning" | "recruiter" | "staffing_recruiter" | "staffing_employer" | "email") => {
    // If no mode specified, smart routing will automatically detect the correct agent
    // This allows users to click prompts without manually selecting an agent
    handleSubmit(query, undefined, undefined, mode);
  };

  return (
    <div className="flex-1 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      <div className="max-w-lg w-full mx-auto space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="text-center space-y-4 sm:space-y-6">
          <div className="flex justify-center">
            <div className="w-16 h-16 sm:w-20 sm:h-20 bg-blue-500/20 rounded-2xl flex items-center justify-center">
              <MessageCircle className="h-8 w-8 sm:h-10 sm:w-10 text-blue-400" />
            </div>
          </div>

          <div className="space-y-2 sm:space-y-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 px-2">
              Let&apos;s reduce your candidate sourcing time
          </h1>
            <p className="text-sm sm:text-base text-slate-400 px-2">
              I&apos;m here to help you save time on finding candidates, improve GitHub sourcing, and make smarter tech recruiting decisions.
            </p>
          </div>
        </div>

        {/* Prompt Templates */}
        <div className="space-y-3 sm:space-y-4">
          <p className="text-xs sm:text-sm text-slate-400 text-center px-2">Try asking me:</p>
          <div className="space-y-2 sm:space-y-3">
            {promptTemplates.map((template, index) => {
              const Icon = template.icon;
              const isSecondary = template.variant === "secondary";
              return (
                <button
                  key={index}
                  onClick={() => handlePromptClick(template.query, template.mode)}
                  className={`w-full flex items-center gap-2 sm:gap-3 px-3 sm:px-5 py-2.5 sm:py-3.5 rounded-xl transition-all duration-200 text-left group active:scale-[0.98] ${
                    isSecondary
                      ? "bg-amber-500/10 hover:bg-amber-500/20 active:bg-amber-500/25 border border-amber-500/30 hover:border-amber-500/50"
                      : "bg-slate-800/50 hover:bg-slate-700/50 active:bg-slate-700/70 border border-slate-700/50 hover:border-slate-600"
                  }`}
                >
                  <Icon className={`h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0 ${
                    isSecondary
                      ? "text-amber-400 group-hover:text-amber-300"
                      : "text-slate-400 group-hover:text-slate-300"
                  }`} />
                  <span className={`group-hover:text-slate-100 text-xs sm:text-sm leading-relaxed ${
                    isSecondary
                      ? "text-amber-300"
                      : "text-slate-300"
                  }`}>
                    {template.text}
            </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Footer Note */}
        <div className="text-center pt-2 px-2">
          <p className="text-xs text-slate-500">
            Or type your own question in the chat below
          </p>
        </div>
      </div>
    </div>
  );
}
