"use client";

import { useBackendHealth } from "@/hooks/useBackendHealth";

interface BackendHealthCheckerProps {
  onHealthStatusChange?: (isHealthy: boolean, isChecking: boolean) => void;
  children?: React.ReactNode;
}

/**
 * Backend health monitoring component that displays appropriate states
 * Uses the useBackendHealth hook for monitoring and retry logic
 */
export function BackendHealthChecker({
  onHealthStatusChange,
  children,
}: BackendHealthCheckerProps) {
  const { isBackendReady, isCheckingBackend, checkBackendHealth } =
    useBackendHealth();

  // Notify parent of health status changes
  React.useEffect(() => {
    if (onHealthStatusChange) {
      onHealthStatusChange(isBackendReady, isCheckingBackend);
    }
  }, [isBackendReady, isCheckingBackend, onHealthStatusChange]);

  // Show loading screen while checking backend
  if (isCheckingBackend) {
    return <BackendLoadingScreen />;
  }

  // Show error screen if backend is not ready
  if (!isBackendReady) {
    return <BackendErrorScreen onRetry={checkBackendHealth} />;
  }

  // Render children if backend is ready
  return <>{children}</>;
}

/**
 * Loading screen component - Modern, recruiter-focused design
 * Designed to impress and engage talent acquisition professionals
 */
function BackendLoadingScreen() {
  // Fix hydration error by generating particles only on client
  const [particles, setParticles] = React.useState<Array<{ left: number; top: number; duration: number; delay: number }>>([]);

  React.useEffect(() => {
    // Generate particles only on client side to avoid hydration mismatch
    setParticles(
      Array.from({ length: 12 }, () => ({
        left: Math.random() * 100,
        top: Math.random() * 100,
        duration: 3 + Math.random() * 2,
        delay: Math.random() * 2,
      }))
    );
  }, []);

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 overflow-hidden relative bg-black">
      {/* Pure black background */}
      <div className="absolute inset-0 bg-black"></div>

      {/* Floating particles - only render on client */}
      {particles.length > 0 && (
        <div className="absolute inset-0 overflow-hidden">
          {particles.map((particle, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-blue-400/40 rounded-full"
                style={{
                left: `${particle.left}%`,
                top: `${particle.top}%`,
                animation: `float ${particle.duration}s ease-in-out infinite`,
                animationDelay: `${particle.delay}s`,
              }}
            />
          ))}
        </div>
      )}

      {/* Main content card */}
      <div className="relative z-10 w-full max-w-lg">
        <div className="bg-gradient-to-br from-slate-800/90 via-slate-800/80 to-slate-900/90 backdrop-blur-xl p-10 rounded-3xl border border-slate-700/50 shadow-2xl shadow-black/50">
          <div className="text-center space-y-8">
            {/* Logo/Brand area */}
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="relative">
                  {/* Main spinner - multi-layered */}
                  <div className="relative w-20 h-20">
                    {/* Outer glow ring */}
                    <div className="absolute inset-0 w-20 h-20 border-2 border-blue-500/20 rounded-full"></div>
                    
                    {/* Rotating rings */}
                    <div 
                      className="absolute inset-0 w-20 h-20 border-3 border-transparent border-t-blue-500 border-r-blue-400/50 rounded-full"
                      style={{ animation: "spin 2s linear infinite" }}
                    ></div>
                    <div 
                      className="absolute inset-2 w-16 h-16 border-2 border-transparent border-b-purple-500 border-l-purple-400/50 rounded-full"
                      style={{ animation: "spin 1.5s linear infinite reverse" }}
              ></div>
                    
                    {/* Center pulsing dot */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-3 h-3 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full animate-pulse shadow-lg shadow-blue-500/50"></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Title with gradient text */}
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-blue-500 bg-clip-text text-transparent">
                AI Recruiting Platform
              </h1>
            </div>

            {/* Status message */}
            <div className="space-y-3">
              <p className="text-lg font-semibold text-slate-200">
                Connecting to talent intelligence...
              </p>
              <p className="text-sm text-slate-400">
                Initializing candidate search & matching engine
              </p>
            </div>

            {/* Progress indicator */}
            <div className="space-y-2">
              <div className="h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
              <div
                  className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 rounded-full animate-progress"
                  style={{ width: "60%" }}
              ></div>
              </div>
              <div className="flex justify-between text-xs text-slate-500">
                <span>Loading AI agents...</span>
                <span>Preparing pipeline...</span>
              </div>
            </div>

            {/* Feature highlights */}
            <div className="grid grid-cols-3 gap-4 pt-4">
              {[
                { icon: "🔍", label: "Smart Search" },
                { icon: "🎯", label: "AI Matching" },
                { icon: "⚡", label: "Fast Results" },
              ].map((feature, i) => (
                <div 
                  key={i}
                  className="flex flex-col items-center gap-2 p-3 rounded-xl bg-slate-800/50 border border-slate-700/30 hover:border-blue-500/50 transition-all"
                  style={{ 
                    animation: `fadeInUp 0.6s ease-out ${0.3 + i * 0.1}s both` 
                  }}
                >
                  <span className="text-2xl">{feature.icon}</span>
                  <span className="text-xs text-slate-400 font-medium">{feature.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Custom animations */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0) translateX(0); opacity: 0.4; }
          50% { transform: translateY(-20px) translateX(10px); opacity: 0.8; }
        }
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(15px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes progress {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
        .animate-pulse-slow {
          animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .animate-progress {
          animation: progress 2s ease-in-out infinite;
        }
        .border-3 {
          border-width: 3px;
        }
      `}} />
    </div>
  );
}

/**
 * Error screen component shown when backend is unavailable
 */
function BackendErrorScreen({ onRetry }: { onRetry: () => Promise<boolean> }) {
  const handleRetry = () => {
    onRetry().catch((error) => {
      console.error("Retry failed:", error);
    });
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4">
      <div className="text-center space-y-4">
        <h2 className="text-2xl font-bold text-red-400">Backend Unavailable</h2>
        <p className="text-neutral-300">
          Unable to connect to backend services
        </p>
        <button
          onClick={handleRetry}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
        >
          Retry
        </button>
      </div>
    </div>
  );
}

// Need to import React for useEffect
import React from "react";
