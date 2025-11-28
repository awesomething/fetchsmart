/**
 * Candidate Parser Utility
 * 
 * Extracts candidate profile data from agent message responses.
 * Uses multiple parsing strategies to handle various response formats.
 * 
 * Based on industry best practices for JSON extraction from LLM responses.
 */

import { CandidateProfile } from "@/types/recruiting";

/**
 * Parse candidate profiles from message content
 * 
 * Uses multiple extraction strategies in order of reliability:
 * 1. Direct JSON parsing
 * 2. Brace-balanced JSON extraction
 * 3. Function response format
 * 4. Markdown code blocks
 * 5. Regex-based extraction
 * 
 * @param content - The message content to parse
 * @returns Array of candidate profiles or null if no valid candidates found
 */
export function parseCandidatesFromMessage(content: string): CandidateProfile[] | null {
  if (!content || typeof content !== 'string') {
    return null;
  }

  // Quick check - if no candidate indicators, skip parsing
  if (!hasCandidateData(content)) {
    return null;
  }

  try {
    // Strategy 1: Try to parse the entire content as JSON
    try {
      const parsed = JSON.parse(content.trim());
      const candidates = extractCandidatesFromObject(parsed);
      if (candidates && candidates.length > 0) {
        console.log('✅ [PARSER] Strategy 1 succeeded: Direct JSON parse');
        return candidates;
      }
    } catch {
      // Not direct JSON, continue
    }

    // Strategy 2: Extract complete JSON object using brace balancing
    // This handles plain JSON text (most common case)
    const jsonMatch = extractCompleteJsonObject(content);
    if (jsonMatch) {
      try {
        const parsed = JSON.parse(jsonMatch);
        const candidates = extractCandidatesFromObject(parsed);
        if (candidates && candidates.length > 0) {
          console.log('✅ [PARSER] Strategy 2 succeeded: Brace-balanced extraction');
          return candidates;
        }
      } catch (error) {
        console.warn('⚠️ [PARSER] Strategy 2 failed to parse extracted JSON:', error);
      }
    }

    // Strategy 3: Look for escaped JSON in result fields (function response format)
    const escapedJsonMatch = extractEscapedJson(content);
    if (escapedJsonMatch) {
      try {
        const parsed = JSON.parse(escapedJsonMatch);
        const candidates = extractCandidatesFromObject(parsed);
        if (candidates && candidates.length > 0) {
          console.log('✅ [PARSER] Strategy 3 succeeded: Escaped JSON extraction');
          return candidates;
        }
      } catch (error) {
        console.warn('⚠️ [PARSER] Strategy 3 failed:', error);
      }
    }

    // Strategy 4: Look for JSON in markdown code blocks
    const codeBlockMatch = extractJsonFromCodeBlock(content);
    if (codeBlockMatch) {
      try {
        const parsed = JSON.parse(codeBlockMatch);
        const candidates = extractCandidatesFromObject(parsed);
        if (candidates && candidates.length > 0) {
          console.log('✅ [PARSER] Strategy 4 succeeded: Code block extraction');
          return candidates;
        }
      } catch (error) {
        console.warn('⚠️ [PARSER] Strategy 4 failed:', error);
      }
    }

    // Strategy 5: Aggressive regex-based extraction (fallback)
    const regexMatch = extractJsonWithRegex(content);
    if (regexMatch) {
      try {
        const parsed = JSON.parse(regexMatch);
        const candidates = extractCandidatesFromObject(parsed);
        if (candidates && candidates.length > 0) {
          console.log('✅ [PARSER] Strategy 5 succeeded: Regex extraction');
          return candidates;
        }
      } catch (error) {
        console.warn('⚠️ [PARSER] Strategy 5 failed:', error);
      }
    }

    console.warn('⚠️ [PARSER] All strategies failed to extract candidates');
    return null;
  } catch (error) {
    console.error('❌ [PARSER] Error parsing candidates from message:', error);
    return null;
  }
}

/**
 * Extract complete JSON object using brace balancing algorithm
 * Handles nested objects and arrays correctly
 */
function extractCompleteJsonObject(content: string): string | null {
  // Find the first opening brace that's likely the start of our JSON
  const startPatterns = [
    /\{\s*"query"/,
    /\{\s*"top_candidates"/,
    /\{\s*"total_matches"/,
  ];

  let jsonStart = -1;
  for (const pattern of startPatterns) {
    const match = content.match(pattern);
    if (match && match.index !== undefined) {
      jsonStart = match.index;
      break;
    }
  }

  if (jsonStart === -1) {
    // Try finding any opening brace
    jsonStart = content.indexOf('{');
  }

  if (jsonStart === -1) {
    return null;
  }

  // Use brace balancing to find the complete JSON object
  let braceCount = 0;
  let inString = false;
  let escapeNext = false;
  let jsonEnd = -1;

  for (let i = jsonStart; i < content.length; i++) {
    const char = content[i];

    if (escapeNext) {
      escapeNext = false;
      continue;
    }

    if (char === '\\') {
      escapeNext = true;
      continue;
    }

    if (char === '"') {
      inString = !inString;
      continue;
    }

    if (inString) {
      continue;
    }

    if (char === '{') {
      braceCount++;
    } else if (char === '}') {
      braceCount--;
      if (braceCount === 0) {
        jsonEnd = i + 1;
        break;
      }
    }
  }

  if (jsonEnd > jsonStart) {
    return content.substring(jsonStart, jsonEnd);
  }

  return null;
}

/**
 * Extract escaped JSON from function response format
 */
function extractEscapedJson(content: string): string | null {
  // Pattern: "result": "{\n  \"query\": ..."
  const patterns = [
    /"result"\s*:\s*"([^"]*(?:\\.[^"]*)*)"/,
    /result\s*:\s*"([^"]*(?:\\.[^"]*)*)"/,
  ];

  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match && match[1]) {
      try {
        // Unescape the JSON string
        const unescaped = match[1]
          .replace(/\\n/g, '\n')
          .replace(/\\"/g, '"')
          .replace(/\\\\/g, '\\')
          .replace(/\\t/g, '\t')
          .replace(/\\r/g, '\r');
        return unescaped;
      } catch {
        continue;
      }
    }
  }

  return null;
}

/**
 * Extract JSON from markdown code blocks
 */
function extractJsonFromCodeBlock(content: string): string | null {
  const patterns = [
    /```(?:json)?\s*(\{[\s\S]*?\})\s*```/,
    /```\s*(\{[\s\S]*?\})\s*```/,
  ];

  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }

  return null;
}

/**
 * Aggressive regex-based extraction (fallback)
 */
function extractJsonWithRegex(content: string): string | null {
  // Try to find JSON object with top_candidates
  const pattern = /\{[^{}]*(?:"top_candidates"\s*:\s*\[[^\]]*\])[^{}]*\}/;
  const match = content.match(pattern);
  if (match) {
    return match[0];
  }

  return null;
}

/**
 * Extract candidate profiles from a parsed JSON object
 * 
 * Handles various response structures from the MCP server
 * 
 * @param obj - Parsed JSON object
 * @returns Array of validated candidate profiles or null
 */
function extractCandidatesFromObject(obj: unknown): CandidateProfile[] | null {
  if (!obj || typeof obj !== 'object') {
    return null;
  }

  // Type guard for object with potential candidate arrays
  const objWithCandidates = obj as Record<string, unknown>;
  
  // Look for top_candidates array
  const candidatesArray = objWithCandidates.top_candidates || 
                          objWithCandidates.candidates || 
                          objWithCandidates.results;
  
  if (!Array.isArray(candidatesArray) || candidatesArray.length === 0) {
    return null;
  }

  console.log(`📊 [PARSER] Found ${candidatesArray.length} candidates in array`);

  // Map and validate each candidate
  const validCandidates: CandidateProfile[] = [];
  
  for (const candidate of candidatesArray) {
    const validated = validateAndMapCandidate(candidate);
    if (validated) {
      validCandidates.push(validated);
    }
  }

  console.log(`✅ [PARSER] Validated ${validCandidates.length} candidates`);

  return validCandidates.length > 0 ? validCandidates : null;
}

/**
 * Validate and map a candidate object to CandidateProfile interface
 * 
 * @param candidate - Raw candidate data from MCP server
 * @returns Validated CandidateProfile or null if invalid
 */
function validateAndMapCandidate(candidate: unknown): CandidateProfile | null {
  if (!candidate || typeof candidate !== 'object') {
    return null;
  }

  // Type guard for candidate object
  const candidateObj = candidate as Record<string, unknown>;

  // Required fields
  if (!candidateObj.github_username && !candidateObj.name) {
    return null;
  }

  try {
    // Handle unicode escape sequences in strings (like \u2713)
    const cleanString = (str: unknown): string => {
      if (typeof str !== 'string') return '';
      try {
        // Replace unicode escapes
        return str.replace(/\\u([0-9a-fA-F]{4})/g, (match, code) => {
          return String.fromCharCode(parseInt(code, 16));
        });
      } catch {
        return str;
      }
    };

    // Map to CandidateProfile interface
    const profile: CandidateProfile = {
      id: cleanString(candidateObj.id) || cleanString(candidateObj.github_username) || `candidate-${Date.now()}-${Math.random()}`,
      name: cleanString(candidateObj.name) || cleanString(candidateObj.github_username) || 'Unknown',
      github_username: cleanString(candidateObj.github_username) || '',
      github_profile_url: cleanString(candidateObj.github_profile_url) || 
                         (candidateObj.github_username ? `https://github.com/${cleanString(candidateObj.github_username)}` : ''),
      role: cleanString(candidateObj.role) || cleanString(candidateObj.likely_role) || 'Software Engineer',
      experience_level: cleanString(candidateObj.experience_level) || cleanString(candidateObj.estimated_experience_level) || 'Mid',
      location: cleanString(candidateObj.location) || '',
      primary_language: cleanString(candidateObj.primary_language) || '',
      skills: Array.isArray(candidateObj.skills) 
        ? (candidateObj.skills as unknown[]).map(s => cleanString(s)).filter(Boolean) as string[]
        : [],
      github_stats: {
        repos: ((candidateObj.github_stats as Record<string, unknown>)?.repos as number) || 
               (candidateObj.public_repos as number) || 0,
        stars: ((candidateObj.github_stats as Record<string, unknown>)?.stars as number) || 
               (candidateObj.total_stars as number) || 0,
        followers: ((candidateObj.github_stats as Record<string, unknown>)?.followers as number) || 
                  (candidateObj.followers as number) || 0,
        commits: ((candidateObj.github_stats as Record<string, unknown>)?.commits as number) || 0,
      },
      match_score: (candidateObj.match_score as number) || 0,
      match_reasons: Array.isArray(candidateObj.match_reasons) 
        ? (candidateObj.match_reasons as unknown[]).map(r => cleanString(r)).filter(Boolean) as string[]
        : [],
      matched_skills: Array.isArray(candidateObj.matched_skills) 
        ? (candidateObj.matched_skills as unknown[]).map(s => cleanString(s)).filter(Boolean) as string[]
        : [],
      status: cleanString(candidateObj.status) || 'new',
      email: candidateObj.email ? cleanString(candidateObj.email) : null,
      email_confidence: typeof candidateObj.email_confidence === 'number' ? candidateObj.email_confidence : null,
    };

    return profile;
  } catch (error) {
    console.error('❌ [PARSER] Error mapping candidate:', error, candidate);
    return null;
  }
}

/**
 * Check if content contains candidate data
 * 
 * Quick check without full parsing - useful for performance
 * 
 * @param content - Message content to check
 * @returns true if content likely contains candidate data
 */
export function hasCandidateData(content: string): boolean {
  if (!content || typeof content !== 'string') {
    return false;
  }

  // Look for key indicators of candidate data
  return (
    content.includes('top_candidates') ||
    content.includes('"candidates"') ||
    (content.includes('github_username') && content.includes('match_score')) ||
    (content.includes('github_profile_url') && content.includes('skills')) ||
    (content.includes('"query"') && content.includes('"total_matches"'))
  );
}
