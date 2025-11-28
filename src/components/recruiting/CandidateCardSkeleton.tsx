"use client";

/**
 * CandidateCardSkeleton - Professional skeleton loader for candidate cards
 * Matches the exact layout of CandidateCard for seamless loading experience
 */
export function CandidateCardSkeleton() {
  return (
    <div className="transition-all duration-300 border-border/50 bg-white dark:bg-slate-900 rounded-xl shadow-md overflow-hidden animate-pulse">
      <div className="p-6">
        {/* Header with Avatar */}
        <div className="flex items-start gap-4 mb-4">
          <div className="w-16 h-16 rounded-full bg-slate-700/50 flex-shrink-0"></div>
          <div className="flex-1 min-w-0">
            <div className="h-5 bg-slate-700/50 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-slate-700/30 rounded w-1/2"></div>
          </div>
        </div>

        {/* Role and Experience */}
        <div className="space-y-2 mb-3">
          <div className="h-4 bg-slate-700/50 rounded w-2/3"></div>
          <div className="h-3 bg-slate-700/30 rounded w-1/2"></div>
        </div>

        {/* Status Badge */}
        <div className="mb-4">
          <div className="h-6 bg-slate-700/30 rounded-full w-24"></div>
        </div>

        {/* GitHub Stats */}
        <div className="flex justify-between items-center mb-4 pb-4 border-b border-slate-700/30">
          <div className="space-y-2 flex-1">
            <div className="h-3 bg-slate-700/30 rounded w-16"></div>
            <div className="h-4 bg-slate-700/50 rounded w-12"></div>
          </div>
          <div className="space-y-2 flex-1">
            <div className="h-3 bg-slate-700/30 rounded w-16"></div>
            <div className="h-4 bg-slate-700/50 rounded w-12"></div>
          </div>
        </div>

        {/* Skills */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            <div className="h-6 bg-slate-700/30 rounded-full w-16"></div>
            <div className="h-6 bg-slate-700/30 rounded-full w-20"></div>
            <div className="h-6 bg-slate-700/30 rounded-full w-14"></div>
            <div className="h-6 bg-slate-700/30 rounded-full w-12"></div>
          </div>
        </div>

        {/* Assessment Bar */}
        <div className="mb-3">
          <div className="flex justify-between items-center mb-1">
            <div className="h-3 bg-slate-700/30 rounded w-20"></div>
            <div className="h-3 bg-slate-700/30 rounded w-12"></div>
          </div>
          <div className="w-full h-2 bg-slate-700/20 rounded-full"></div>
        </div>

        {/* View Profile Button */}
        <div className="h-10 bg-slate-700/20 rounded-lg"></div>
      </div>
    </div>
  );
}

