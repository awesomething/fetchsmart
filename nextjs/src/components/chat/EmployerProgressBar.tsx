"use client";

import React from "react";
import { Loader2, CheckCircle2 } from "lucide-react";

type EmployerWorkflowStage = "transferring" | "creating" | "reviewing" | "analyzing" | "assessing" | "preparing" | "complete";

interface EmployerProgressBarProps {
  currentStage: EmployerWorkflowStage;
  message?: string;
}

const STAGES: EmployerWorkflowStage[] = [
  "transferring",
  "creating",
  "reviewing",
  "analyzing",
  "assessing",
  "preparing",
];

const STAGE_LABELS: Record<EmployerWorkflowStage, string> = {
  transferring: "Transferring",
  creating: "Creating",
  reviewing: "Reviewing",
  analyzing: "Analyzing",
  assessing: "Assessing",
  preparing: "Preparing",
  complete: "Complete",
};

const STAGE_DESCRIPTIONS: Record<EmployerWorkflowStage, string> = {
  transferring: "Transferring to employer review agent...",
  creating: "Creating candidate submission...",
  reviewing: "Reviewing candidate submission and resume...",
  analyzing: "Analyzing qualifications and skills match...",
  assessing: "Assessing experience level and job fit...",
  preparing: "Preparing candidate assessment...",
  complete: "Review complete!",
};

export function EmployerProgressBar({
  currentStage,
  message,
}: EmployerProgressBarProps): React.JSX.Element {
  const currentIndex = STAGES.indexOf(currentStage);
  const isComplete = currentStage === "complete";
  const progressPercentage = isComplete
    ? 100
    : ((currentIndex + 1) / STAGES.length) * 100;

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/50 rounded-2xl rounded-tl-sm p-4 shadow-lg">
      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-200">
            {isComplete ? "✅ Review Complete" : "Reviewing Candidate"}
          </span>
          <span className="text-xs text-slate-400">
            {Math.round(progressPercentage)}%
          </span>
        </div>
        <div className="w-full bg-slate-700/50 rounded-full h-2 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-500 ease-out rounded-full"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Stage Indicators */}
      <div className="flex items-center justify-between mb-3">
        {STAGES.map((stage, index) => {
          const isActive = index === currentIndex && !isComplete;
          const isCompleted = index < currentIndex || isComplete;

          return (
            <div
              key={stage}
              className="flex flex-col items-center flex-1"
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all ${
                  isCompleted
                    ? "bg-emerald-500 border-emerald-400"
                    : isActive
                    ? "bg-emerald-500/50 border-emerald-400 animate-pulse"
                    : "bg-slate-700 border-slate-600"
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-white" />
                ) : isActive ? (
                  <Loader2 className="h-4 w-4 text-emerald-300 animate-spin" />
                ) : (
                  <div className="w-2 h-2 rounded-full bg-slate-500" />
                )}
              </div>
              <span
                className={`text-xs mt-1 text-center ${
                  isActive || isCompleted
                    ? "text-emerald-400 font-medium"
                    : "text-slate-500"
                }`}
              >
                {STAGE_LABELS[stage]}
              </span>
            </div>
          );
        })}
      </div>

      {/* Current Stage Description */}
      <div className="flex items-center gap-2 bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2">
        {isComplete ? (
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
        ) : (
          <Loader2 className="h-4 w-4 animate-spin text-emerald-400" />
        )}
        <span className="text-sm text-slate-300">
          {message || STAGE_DESCRIPTIONS[currentStage]}
        </span>
      </div>
    </div>
  );
}

