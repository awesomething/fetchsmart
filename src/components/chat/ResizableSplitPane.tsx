"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { GripVertical } from "lucide-react";

interface ResizableSplitPaneProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  defaultLeftWidth?: number; // Percentage (0-100)
  minLeftWidth?: number; // Percentage
  maxLeftWidth?: number; // Percentage
  storageKey?: string; // For persisting width in localStorage
}

/**
 * ResizableSplitPane - Professional draggable split pane component
 * Supports mouse and touch events, with smooth animations and persistence
 */
export function ResizableSplitPane({
  leftPanel,
  rightPanel,
  defaultLeftWidth = 40,
  minLeftWidth = 20,
  maxLeftWidth = 70,
  storageKey = "split-pane-width",
}: ResizableSplitPaneProps): React.JSX.Element {
  const [leftWidth, setLeftWidth] = useState<number>(() => {
    if (typeof window !== "undefined" && storageKey) {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = parseFloat(saved);
        if (!isNaN(parsed) && parsed >= minLeftWidth && parsed <= maxLeftWidth) {
          return parsed;
        }
      }
    }
    return defaultLeftWidth;
  });

  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const dragStartX = useRef<number>(0);
  const dragStartWidth = useRef<number>(0);

  // Save width to localStorage
  useEffect(() => {
    if (storageKey && typeof window !== "undefined") {
      localStorage.setItem(storageKey, leftWidth.toString());
    }
  }, [leftWidth, storageKey]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    dragStartX.current = e.clientX;
    dragStartWidth.current = leftWidth;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, [leftWidth]);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    e.preventDefault();
    setIsDragging(true);
    dragStartX.current = e.touches[0].clientX;
    dragStartWidth.current = leftWidth;
    document.body.style.userSelect = "none";
  }, [leftWidth]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const containerWidth = containerRef.current.offsetWidth;
    const deltaX = e.clientX - dragStartX.current;
    const deltaPercent = (deltaX / containerWidth) * 100;
    const newWidth = Math.max(
      minLeftWidth,
      Math.min(maxLeftWidth, dragStartWidth.current + deltaPercent)
    );

    setLeftWidth(newWidth);
  }, [isDragging, minLeftWidth, maxLeftWidth]);

  const handleTouchMove = useCallback((e: TouchEvent) => {
    if (!isDragging || !containerRef.current) return;

    const containerWidth = containerRef.current.offsetWidth;
    const deltaX = e.touches[0].clientX - dragStartX.current;
    const deltaPercent = (deltaX / containerWidth) * 100;
    const newWidth = Math.max(
      minLeftWidth,
      Math.min(maxLeftWidth, dragStartWidth.current + deltaPercent)
    );

    setLeftWidth(newWidth);
  }, [isDragging, minLeftWidth, maxLeftWidth]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.addEventListener("touchmove", handleTouchMove, { passive: false });
      document.addEventListener("touchend", handleMouseUp);
      return () => {
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
        document.removeEventListener("touchmove", handleTouchMove);
        document.removeEventListener("touchend", handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleTouchMove, handleMouseUp]);

  return (
    <div
      ref={containerRef}
      className="h-full w-full flex relative"
    >
      {/* Left Panel */}
      <div
        className="flex-shrink-0 flex flex-col overflow-hidden transition-all duration-200 ease-out"
        style={{ width: `${leftWidth}%` }}
      >
        {leftPanel}
      </div>

      {/* Draggable Divider */}
      <div
        className={`
          flex-shrink-0 w-1 bg-slate-700 hover:bg-slate-600 cursor-col-resize
          transition-colors duration-150 relative group
          ${isDragging ? "bg-blue-500" : ""}
        `}
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
        role="separator"
        aria-label="Resize panels"
        aria-orientation="vertical"
        aria-valuemin={minLeftWidth}
        aria-valuemax={maxLeftWidth}
        aria-valuenow={leftWidth}
      >
        {/* Visual grip indicator */}
        <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-8 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="flex flex-col gap-1">
            <GripVertical className="h-4 w-4 text-slate-400" />
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div
        className="flex-1 flex flex-col overflow-hidden min-w-0"
        style={{ width: `${100 - leftWidth}%` }}
      >
        {rightPanel}
      </div>
    </div>
  );
}

