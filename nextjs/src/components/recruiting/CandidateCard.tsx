"use client";

import { useState } from "react";
import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CandidateProfile } from "@/types/recruiting";
import { Github, Star, GitFork } from "lucide-react";

export function CandidateCard({ candidate }: { candidate: CandidateProfile }) {
  const [imageError, setImageError] = useState(false);

  // Get experience years from experience_level or default
  // Handle formats like "8 years", "Senior", "8 years exp", etc.
  const experienceYears = candidate.experience_level?.match(/\d+/)?.[0] || 
    (candidate.experience_level?.toLowerCase().includes("senior") ? "8" : 
     candidate.experience_level?.toLowerCase().includes("mid") ? "5" : "5");
  
  // Get avatar URL - try to use GitHub avatar if available
  const avatarUrl = candidate.github_username 
    ? `https://avatars.githubusercontent.com/${candidate.github_username}`
    : null;

  // Get initials for fallback
  const initials = candidate.name?.split(' ').map(n => n[0]).join('').slice(0, 2) || '??';

  return (
    <Card className="transition-all duration-300 hover:scale-[1.02] hover:shadow-lg border-border/50 bg-white dark:bg-slate-900 w-full">
      <CardContent className="p-6">
        {/* Header with Avatar */}
        <div className="flex items-start gap-4 mb-4">
          {avatarUrl && !imageError ? (
            <div className="w-16 h-16 rounded-full overflow-hidden flex-shrink-0 border-2 border-border relative">
              <Image
                src={avatarUrl}
                alt={candidate.name}
                width={64}
                height={64}
                className="w-full h-full object-cover"
                onError={() => setImageError(true)}
              />
            </div>
          ) : (
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-cyan-500 flex items-center justify-center text-white font-bold text-xl flex-shrink-0">
              {initials}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-lg truncate text-slate-900 dark:text-slate-100">{candidate.name}</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 truncate">
              @{candidate.github_username}
            </p>
          </div>
        </div>
        
        {/* Role and Experience */}
        <div className="mb-3">
          <p className="font-semibold text-sm text-slate-900 dark:text-slate-100">{candidate.role}</p>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            {experienceYears} years exp • {candidate.location}
          </p>
        </div>

        {/* Email Display (replaces status badge) */}
        <div className="mb-3">
          {candidate.email ? (
            <a
              href={`mailto:${candidate.email}`}
              className="text-xs px-2 py-0.5 border rounded-md bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border-blue-300 dark:border-blue-700 hover:underline inline-block"
            >
              {candidate.email}
            </a>
          ) : (
            <span className="text-xs px-2 py-0.5 text-slate-600 dark:text-slate-400">
              No email found
            </span>
          )}
        </div>
        
        {/* GitHub Stats */}
        <div className="flex gap-4 mb-3 text-sm text-slate-600 dark:text-slate-400">
          <div className="flex items-center gap-1">
            <GitFork className="h-4 w-4" />
            <span className="font-medium text-slate-900 dark:text-slate-100">{candidate.github_stats.repos}</span>
            <span className="text-xs">Repos</span>
          </div>
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4" />
            <span className="font-medium text-slate-900 dark:text-slate-100">{candidate.github_stats.stars}</span>
            <span className="text-xs">Stars</span>
          </div>
          {/* <div className="flex items-center gap-1">
            <GitCommit className="h-4 w-4" />
            <span className="font-medium">{commits}</span>
            <span className="text-xs">Commits</span>
          </div> */}
        </div>
        
        {/* Skills */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {candidate.skills.slice(0, 3).map((skill) => (
            <Badge key={skill} variant="outline" className="text-xs px-2 py-0.5">
              {skill}
            </Badge>
          ))}
          {candidate.skills.length > 3 && (
            <Badge variant="outline" className="text-xs px-2 py-0.5">
              +{candidate.skills.length - 3}
            </Badge>
          )}
        </div>
        
        {/* Match Score */}
        {candidate.match_score !== undefined && (
          <div className="mb-4">
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-600 dark:text-slate-400">Assessment</span>
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

