"use client";

import { useState, useEffect } from "react";
import { ArrowDown, ArrowRight, X, CheckCircle } from "lucide-react";

interface WalkthroughStep {
  id: number;
  title: string;
  description: string;
  targetSelector: string;
  position: "top" | "bottom" | "left" | "right";
  arrowDirection: "down" | "right" | "up" | "left";
}

const WALKTHROUGH_STEPS: WalkthroughStep[] = [
  {
    id: 1,
    title: "Step 1: Enter User ID",
    description: 'Click "Enter user ID", type your username, and confirm with the green checkmark.',
    targetSelector: '[data-walkthrough="user-id-input"]',
    position: "bottom",
    arrowDirection: "down",
  },
  {
    id: 2,
    title: "Step 2: Create Session",
    description: 'Click "Select session", scroll down, and click "Create New Session".',
    targetSelector: '[data-walkthrough="session-selector"]',
    position: "left",
    arrowDirection: "right",
  },
  {
    id: 3,
    title: "Step 3: Start Searching!",
    description: 'Type "Find senior engineers on GitHub" and get instant candidate results.',
    targetSelector: '[data-walkthrough="chat-input"]',
    position: "top",
    arrowDirection: "up",
  },
];

interface WalkthroughOverlayProps {
  onComplete: () => void;
  onSkip: () => void;
}

export function WalkthroughOverlay({
  onComplete,
  onSkip,
}: WalkthroughOverlayProps): React.JSX.Element | null {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetPosition, setTargetPosition] = useState<DOMRect | null>(null);

  const step = WALKTHROUGH_STEPS[currentStep];

  useEffect(() => {
    // Find the target element and get its position
    const updatePosition = () => {
      const targetElement = document.querySelector(step.targetSelector);
      if (targetElement) {
        const rect = targetElement.getBoundingClientRect();
        setTargetPosition(rect);
      }
    };

    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition);

    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition);
    };
  }, [step.targetSelector]);

  const handleNext = () => {
    if (currentStep < WALKTHROUGH_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (!targetPosition) {
    return null;
  }

  // Calculate tooltip position based on target element
  const getTooltipStyle = (): React.CSSProperties => {
    const offset = 20;
    const arrowSize = 40;

    switch (step.position) {
      case "bottom":
        return {
          top: targetPosition.bottom + offset + arrowSize,
          left: targetPosition.left + targetPosition.width / 2,
          transform: "translateX(-50%)",
        };
      case "top":
        return {
          top: targetPosition.top - offset - arrowSize,
          left: targetPosition.left + targetPosition.width / 2,
          transform: "translate(-50%, -100%)",
        };
      case "left":
        return {
          top: targetPosition.top + targetPosition.height / 2,
          left: targetPosition.left - offset - arrowSize,
          transform: "translate(-100%, -50%)",
        };
      case "right":
        return {
          top: targetPosition.top + targetPosition.height / 2,
          left: targetPosition.right + offset + arrowSize,
          transform: "translateY(-50%)",
        };
      default:
        return {};
    }
  };

  // Calculate arrow position
  const getArrowStyle = (): React.CSSProperties => {
    const offset = 10;

    switch (step.position) {
      case "bottom":
        return {
          top: targetPosition.bottom + offset,
          left: targetPosition.left + targetPosition.width / 2,
          transform: "translateX(-50%)",
        };
      case "top":
        return {
          top: targetPosition.top - offset - 30,
          left: targetPosition.left + targetPosition.width / 2,
          transform: "translateX(-50%) rotate(180deg)",
        };
      case "left":
        return {
          top: targetPosition.top + targetPosition.height / 2,
          left: targetPosition.left - offset - 30,
          transform: "translateY(-50%) rotate(90deg)",
        };
      case "right":
        return {
          top: targetPosition.top + targetPosition.height / 2,
          left: targetPosition.right + offset,
          transform: "translateY(-50%) rotate(-90deg)",
        };
      default:
        return {};
    }
  };

  return (
    <>
      {/* Dark overlay with hole around target element */}
      <div className="fixed inset-0 z-[300] pointer-events-none">
        {/* Top */}
        <div
          className="absolute left-0 right-0 bg-black/70"
          style={{
            top: 0,
            height: targetPosition.top,
          }}
        />
        {/* Left */}
        <div
          className="absolute top-0 bottom-0 bg-black/70"
          style={{
            left: 0,
            width: targetPosition.left,
          }}
        />
        {/* Right */}
        <div
          className="absolute top-0 bottom-0 bg-black/70"
          style={{
            left: targetPosition.right,
            right: 0,
          }}
        />
        {/* Bottom */}
        <div
          className="absolute left-0 right-0 bg-black/70"
          style={{
            top: targetPosition.bottom,
            bottom: 0,
          }}
        />

        {/* Highlight ring around target */}
        <div
          className="absolute border-4 border-emerald-400 rounded-lg animate-pulse pointer-events-none"
          style={{
            top: targetPosition.top - 4,
            left: targetPosition.left - 4,
            width: targetPosition.width + 8,
            height: targetPosition.height + 8,
          }}
        />
      </div>

      {/* Animated arrow pointing to target */}
      <div
        className="fixed z-[301] text-emerald-400 animate-bounce pointer-events-none"
        style={getArrowStyle()}
      >
        {step.arrowDirection === "down" && <ArrowDown className="w-8 h-8" />}
        {step.arrowDirection === "up" && <ArrowDown className="w-8 h-8 rotate-180" />}
        {step.arrowDirection === "left" && <ArrowRight className="w-8 h-8 rotate-180" />}
        {step.arrowDirection === "right" && <ArrowRight className="w-8 h-8" />}
      </div>

      {/* Tooltip with instructions */}
      <div
        className="fixed z-[302] pointer-events-auto"
        style={getTooltipStyle()}
      >
        <div className="bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-xl shadow-2xl p-6 max-w-sm border-2 border-emerald-400">
          {/* Close button */}
          <button
            onClick={onSkip}
            className="absolute top-2 right-2 text-white/70 hover:text-white transition-colors"
            aria-label="Skip walkthrough"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Step indicator */}
          <div className="flex items-center gap-2 mb-3">
            <div className="flex items-center justify-center w-8 h-8 bg-white/20 rounded-full">
              <span className="text-white font-bold">{step.id}</span>
            </div>
            <div className="text-xs text-emerald-100">
              Step {currentStep + 1} of {WALKTHROUGH_STEPS.length}
            </div>
          </div>

          {/* Title */}
          <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>

          {/* Description */}
          <p className="text-sm text-emerald-50 mb-4 leading-relaxed">
            {step.description}
          </p>

          {/* Navigation buttons */}
          <div className="flex items-center justify-between gap-3">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="text-sm text-white/70 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>

            <div className="flex gap-1.5">
              {WALKTHROUGH_STEPS.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full transition-all ${
                    index === currentStep
                      ? "bg-white w-6"
                      : index < currentStep
                      ? "bg-emerald-300"
                      : "bg-white/30"
                  }`}
                />
              ))}
            </div>

            {currentStep < WALKTHROUGH_STEPS.length - 1 ? (
              <button
                onClick={handleNext}
                className="bg-white text-emerald-700 font-semibold px-4 py-2 rounded-lg hover:bg-emerald-50 transition-colors text-sm"
              >
                Next
              </button>
            ) : (
              <button
                onClick={onComplete}
                className="bg-white text-emerald-700 font-semibold px-4 py-2 rounded-lg hover:bg-emerald-50 transition-colors text-sm flex items-center gap-2"
              >
                <CheckCircle className="w-4 h-4" />
                Got it!
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
