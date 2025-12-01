/**
 * Client-safe configuration utilities
 *
 * This module provides configuration functions that can be safely used
 * in both client and server environments without importing server dependencies.
 */

/**
 * Determines if we should use Agent Engine based on environment variables
 * This is safe to use in client-side code (SSE parser, hooks, etc.)
 */
export function shouldUseAgentEngine(): boolean {
  // Check for Agent Engine endpoint or reasoning engine ID
  if (process.env.AGENT_ENGINE_ENDPOINT) {
    return true;
  }

  return Boolean(
    process.env.REASONING_ENGINE_ID && process.env.GOOGLE_CLOUD_PROJECT
  );
}
