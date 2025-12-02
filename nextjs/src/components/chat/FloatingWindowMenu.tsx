"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ExternalLink, Link as LinkIcon, Globe, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  closeFloatingServiceWindow,
  listFloatingServiceWindows,
  openBrowserFallback,
  openViaFloatingService,
} from "@/lib/floating-window-service";
import type { FloatingWindowRecord } from "@/lib/floating-window-service";
import { toast } from "sonner";

const QUICK_LINKS: Array<{ label: string; url: string; icon: React.ReactNode }> =
  [
    {
      label: "LinkedIn",
      url: "https://www.linkedin.com/feed/",
      icon: <LinkIcon className="h-3.5 w-3.5" />,
    },
    {
      label: "Gmail",
      url: "https://mail.google.com/",
      icon: <Globe className="h-3.5 w-3.5" />,
    },
    {
      label: "Indeed",
      url: "https://www.indeed.com/",
      icon: <Globe className="h-3.5 w-3.5" />,
    },
  ];

export function FloatingWindowMenu(): React.JSX.Element | null {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [floatingWindows, setFloatingWindows] = useState<
    FloatingWindowRecord[]
  >([]);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const refreshFloatingWindows = useCallback(async () => {
    try {
      const windows = await listFloatingServiceWindows();
      setFloatingWindows(windows);
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    if (!isMenuOpen) {
      return;
    }

    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsMenuOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    refreshFloatingWindows();

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isMenuOpen, refreshFloatingWindows]);

  const handleOpen = async (targetUrl: string) => {
    try {
      if (!targetUrl) {
        toast.error("Please enter a URL");
        return;
      }

      await openViaFloatingService(targetUrl);
      setUrlInput("");
      refreshFloatingWindows();
      toast.success("Floating window opened");
    } catch (error) {
      console.error(error);
      openBrowserFallback(targetUrl);
      toast.error("Failed to open floating window. Opened in new tab instead.");
    }
  };

  const handleCloseWindow = async (windowId: number) => {
    try {
      await closeFloatingServiceWindow(windowId);
      refreshFloatingWindows();
    } catch (error) {
      console.error(error);
      toast.error("Unable to close window");
    }
  };

  return (
    <div className="relative" ref={containerRef}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsMenuOpen((prev) => !prev)}
        className="flex items-center gap-1.5 sm:gap-2 border-slate-600/60 bg-slate-700/40 text-slate-100 hover:bg-slate-700/70 text-xs h-8 sm:h-9 px-2 sm:px-3"
      >
        <ExternalLink className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
        <span className="hidden sm:inline">Floating Windows</span>
        <span className="sm:hidden">Windows</span>
      </Button>

      {isMenuOpen && (
        <div className="fixed left-1/2 -translate-x-1/2 top-20 sm:absolute sm:left-auto sm:right-0 sm:top-auto sm:translate-x-0 sm:mt-2 w-[calc(100vw-2rem)] sm:w-80 max-w-sm rounded-xl border border-slate-700 bg-slate-800/95 p-4 shadow-2xl backdrop-blur z-[100]">
          <div className="space-y-3">

            <div>
              <label className="text-xs font-semibold text-slate-300">
                Open URL
              </label>
              <div className="mt-1 flex gap-2">
                <Input
                  value={urlInput}
                  onChange={(event) => setUrlInput(event.target.value)}
                  placeholder="https://www.linkedin.com/in/…"
                  className="bg-slate-900/50 border-slate-700 text-slate-100 placeholder:text-slate-500"
                />
                <Button
                  size="sm"
                  onClick={() => handleOpen(urlInput)}
                  className="bg-emerald-500 hover:bg-emerald-600 text-white"
                >
                  Go
                </Button>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-slate-300 mb-2">
                Quick Links
              </p>
              <div className="grid grid-cols-2 gap-2">
                {QUICK_LINKS.map((quickLink) => (
                  <Button
                    key={quickLink.label}
                    variant="outline"
                    size="sm"
                    onClick={() => handleOpen(quickLink.url)}
                    className="justify-start gap-2 border-slate-700 bg-slate-900/30 text-slate-200 hover:bg-slate-700/40"
                  >
                    {quickLink.icon}
                    <span>{quickLink.label}</span>
                  </Button>
                ))}
              </div>
            </div>

            {floatingWindows.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-300 mb-2">
                  Open Windows
                </p>
                <div className="space-y-2 max-h-36 overflow-y-auto pr-1">
                  {floatingWindows.map((record) => (
                    <div
                      key={record.id}
                      className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-900/30 px-2 py-1.5 text-xs text-slate-300"
                    >
                      <span className="truncate">{record.url}</span>
                      <button
                        type="button"
                        onClick={() => handleCloseWindow(record.id)}
                        className="text-slate-400 hover:text-red-400"
                        aria-label="Close floating window"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

