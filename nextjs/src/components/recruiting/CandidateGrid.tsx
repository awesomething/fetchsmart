"use client";

import { CandidateProfile } from "@/types/recruiting";
import { CandidateCard } from "./CandidateCard";
import { CandidateCardSkeleton } from "./CandidateCardSkeleton";
import { useContainerWidth } from "@/hooks/useContainerWidth";

interface CandidateGridProps {
  candidates: CandidateProfile[];
  isLoading?: boolean;
}

/**
 * CandidateGrid - Responsive grid layout for candidate profile cards
 * 
 * Displays candidate cards in a responsive grid that adapts to container width.
 * Stacks cards vertically (1 column) when container is narrow (< 400px).
 * Uses 2 columns when container is wider.
 * Handles empty states and provides a consistent layout for recruitment data.
 */
export function CandidateGrid({ candidates, isLoading = false }: CandidateGridProps) {
  const [containerRef, containerWidth] = useContainerWidth<HTMLDivElement>();
  
  // Determine if we should stack cards (1 column) based on container width
  // Stack when width is less than 380px (when left pane is dragged to minimum or near minimum)
  // This threshold ensures cards stack when pane is at ~20% of 1920px screen (384px)
  const shouldStack = containerWidth > 0 && containerWidth < 380;

  // Show skeleton loaders while loading
  if (isLoading) {
    return (
      <div 
        ref={containerRef}
        className="h-full overflow-y-auto p-4 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
      >
        <div className={`grid ${shouldStack ? 'grid-cols-1' : 'grid-cols-2'} gap-4 transition-all duration-300`}>
          {[...Array(8)].map((_, index) => (
            <CandidateCardSkeleton key={`skeleton-${index}`} />
          ))}
        </div>
        <div className="h-4"></div>
      </div>
    );
  }

  if (!candidates || candidates.length === 0) {
    return (
      <div 
        ref={containerRef}
        className="flex items-center justify-center h-full p-8"
      >
        <div className="text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-slate-700 dark:text-slate-300 mb-2">
            No Candidates Found
          </h3>
          <p className="text-slate-500 dark:text-slate-400">
            Try searching for candidates using the Recruiter agent mode
          </p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="h-full overflow-y-auto p-4 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
    >
      {/* Dynamic Grid: 1 column when narrow, 2 columns when wide */}
      <div 
        className={`grid ${shouldStack ? 'grid-cols-1' : 'grid-cols-2'} gap-3 sm:gap-4 transition-all duration-300 ease-out`}
        style={{ 
          gridTemplateColumns: shouldStack ? '1fr' : 'repeat(2, minmax(0, 1fr))'
        }}
      >
        {candidates.map((candidate) => (
          <CandidateCard key={candidate.id} candidate={candidate} />
        ))}
      </div>

      {/* Footer spacing */}
      <div className="h-4"></div>
    </div>
  );
}

