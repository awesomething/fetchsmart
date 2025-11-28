"use client";

import { useState, useEffect, useRef, RefObject } from "react";

/**
 * Hook to track the width of a container element
 * Useful for responsive layouts that depend on container size rather than viewport
 */
export function useContainerWidth<T extends HTMLElement = HTMLDivElement>(): [
  RefObject<T | null>,
  number
] {
  const containerRef = useRef<T | null>(null);
  const [width, setWidth] = useState<number>(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Set initial width
    setWidth(container.offsetWidth);

    // Create ResizeObserver to track width changes
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setWidth(entry.contentRect.width);
      }
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  return [containerRef, width];
}

