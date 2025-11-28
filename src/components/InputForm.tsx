"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Loader2,
  Send,
  Plus,
  Route,
  BookOpenText,
  ClipboardList,
  Users,
  Mail,
  Briefcase,
  DollarSign,
} from "lucide-react";
import { useChatContext } from "@/components/chat/ChatProvider";

interface InputFormProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
  context?: "homepage" | "chat"; // Add context prop for different placeholder text
}

export function InputForm({
  onSubmit,
  isLoading,
  context = "homepage",
}: InputFormProps): React.JSX.Element {
  const [inputValue, setInputValue] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [showModeMenu, setShowModeMenu] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { agentMode, setAgentMode } = useChatContext();

  useEffect(() => {
    if (textareaRef.current && context === "homepage") {
      textareaRef.current.focus();
    }
  }, [context]);

  const handleSubmit = (e: React.FormEvent): void => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSubmit(inputValue.trim());
      setInputValue("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const placeholderText =
    context === "chat"
      ? "Ask a follow-up, plan something, or search docs..."
      : "Ask me to plan a goal or search your docs... e.g., Plan a marketing campaign, What is our deployment process?";

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div
          className={`
          relative flex items-end gap-3 p-3 rounded-2xl border transition-all duration-200
          ${
            isFocused
              ? "border-emerald-400/50 bg-slate-800/80 shadow-lg shadow-emerald-500/10"
              : "border-slate-700/50 bg-slate-800/50 hover:border-slate-600/50"
          }
          backdrop-blur-sm
        `}
        >
          {/* Input Area */}
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholderText}
              rows={1}
              className="
                resize-none border-0 bg-transparent text-slate-200 placeholder-slate-400
                focus:ring-0 focus:outline-none focus:border-0 focus:shadow-none
                min-h-[80px] max-h-48
                scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-600
                px-0 py-3
              "
              style={{
                fontSize: "16px",
                lineHeight: "1.6",
                border: "none",
                outline: "none",
                boxShadow: "none",
              }}
            />

            {/* Character count for long messages */}
            {inputValue.length > 500 && (
              <div className="absolute bottom-1 right-1 text-xs text-slate-500 bg-slate-800/80 rounded px-1">
                {inputValue.length}/2000
              </div>
            )}
          </div>

          {/* Quick Mode Toggle */}
          <div className="relative">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => setShowModeMenu((v) => !v)}
              className="h-9 w-9 text-slate-300 hover:text-white"
              title="Select agent mode"
            >
              <Plus className="h-4 w-4" />
            </Button>

            {showModeMenu && (
              <div className="absolute bottom-11 right-0 w-48 rounded-lg border border-slate-700 bg-slate-800/95 shadow-xl shadow-black/40 z-20">
                <div className="px-3 py-2 text-[10px] uppercase tracking-wide text-slate-400 border-b border-slate-700">
                  Agent Mode
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setAgentMode("auto");
                    setShowModeMenu(false);
                  }}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-700/60 ${
                    agentMode === "auto" ? "text-emerald-400" : "text-slate-200"
                  }`}
                >
                  <Route className="h-4 w-4" /> Smart Routing
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAgentMode("qa");
                    setShowModeMenu(false);
                  }}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-700/60 ${
                    agentMode === "qa" ? "text-emerald-400" : "text-slate-200"
                  }`}
                >
                  <BookOpenText className="h-4 w-4" /> FAQ
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAgentMode("planning");
                    setShowModeMenu(false);
                  }}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-700/60 ${
                    agentMode === "planning" ? "text-emerald-400" : "text-slate-200"
                  }`}
                >
                  <ClipboardList className="h-4 w-4" /> Planning
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAgentMode("recruiter");
                    setShowModeMenu(false);
                  }}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-700/60 ${
                    agentMode === "recruiter" ? "text-emerald-400" : "text-slate-200"
                  }`}
                >
                  <Users className="h-4 w-4" /> Recruiter
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAgentMode("email");
                    setShowModeMenu(false);
                  }}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-700/60 ${
                    agentMode === "email" ? "text-emerald-400" : "text-slate-200"
                  }`}
                >
                  <Mail className="h-4 w-4" /> Email Draft
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAgentMode("staffing_recruiter");
                    setShowModeMenu(false);
                  }}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-700/60 ${
                    agentMode === "staffing_recruiter" ? "text-emerald-400" : "text-slate-200"
                  }`}
                >
                  <DollarSign className="h-4 w-4" /> Job Listing
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAgentMode("staffing_employer");
                    setShowModeMenu(false);
                  }}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-700/60 ${
                    agentMode === "staffing_employer" ? "text-emerald-400" : "text-slate-200"
                  }`}
                >
                  <Briefcase className="h-4 w-4" /> Employers Only
                </button>
              </div>
            )}
          </div>

          {/* Send Button */}
          <Button
            type="submit"
            size="sm"
            disabled={!inputValue.trim() || isLoading}
            className="
              h-9 px-4 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700
              text-white border-0 shadow-lg transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
              disabled:bg-slate-600 disabled:from-slate-600 disabled:to-slate-600
              flex items-center gap-2
            "
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="hidden sm:inline">Planning...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {context === "chat" ? "Send" : "Plan Goal"}
                </span>
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
