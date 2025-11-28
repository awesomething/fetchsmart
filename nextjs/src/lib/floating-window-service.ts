// nextjs/src/lib/floating-window-service.ts

type FloatingWindowOptions = {
  width?: number;
  height?: number;
  alwaysOnTop?: boolean;
  frame?: boolean;
  resizable?: boolean;
};

type FloatingWindowRecord = {
  id: number;
  url: string;
};

// Track opened windows (for UI display purposes)
const openedWindows = new Map<number, { url: string; window: Window | null }>();
let windowIdCounter = 1;

/**
 * Normalize URL to ensure it has a protocol
 * Handles cases like "gmail.com" -> "https://gmail.com"
 */
function normalizeUrl(input: string): string {
  if (!input || typeof input !== 'string') {
    throw new Error('URL is required');
  }

  const trimmed = input.trim();
  if (!trimmed) {
    throw new Error('URL cannot be empty');
  }

  // If it already has a protocol, return as-is
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed;
  }

  // If it starts with //, add https:
  if (trimmed.startsWith('//')) {
    return `https:${trimmed}`;
  }

  // Otherwise, assume it's a domain and add https://
  return `https://${trimmed}`;
}

export async function checkFloatingService(): Promise<boolean> {
  // Always return true - browser popups are always available
  return true;
}

export async function openViaFloatingService(
  url: string,
  options?: FloatingWindowOptions,
): Promise<number> {
  // Normalize the URL to ensure it has a protocol
  const normalizedUrl = normalizeUrl(url);
  
  // Use window.open with popup features
  const width = options?.width || 900;
  const height = options?.height || 700;
  
  const features = [
    `width=${width}`,
    `height=${height}`,
    options?.resizable !== false ? 'resizable=yes' : 'resizable=no',
    'scrollbars=yes',
    'noopener',
    'noreferrer'
  ].join(',');
  
  const popup = window.open(normalizedUrl, '_blank', features);
  
  if (popup) {
    const id = windowIdCounter++;
    openedWindows.set(id, { url: normalizedUrl, window: popup });
    return id;
  }
  
  // Fallback if popup blocked
  window.open(normalizedUrl, '_blank', 'noopener,noreferrer');
  return 0;
}

export async function listFloatingServiceWindows(): Promise<
  FloatingWindowRecord[]
> {
  // Return list of tracked windows (for UI display)
  return Array.from(openedWindows.entries()).map(([id, data]) => ({
    id,
    url: data.url,
  }));
}

export async function closeFloatingServiceWindow(
  windowId: number,
): Promise<void> {
  // Try to close the window if we have a reference
  const windowData = openedWindows.get(windowId);
  if (windowData?.window && !windowData.window.closed) {
    windowData.window.close();
  }
  openedWindows.delete(windowId);
}

export function openBrowserFallback(url: string): void {
  // This is now the primary method, but keep for backwards compatibility
  if (typeof window !== "undefined") {
    try {
      const normalizedUrl = normalizeUrl(url);
      window.open(normalizedUrl, "_blank", "noopener,noreferrer");
    } catch (error) {
      console.error("Failed to normalize URL:", error);
      // Fallback to original URL if normalization fails
      window.open(url, "_blank", "noopener,noreferrer");
    }
  }
}

export type { FloatingWindowRecord, FloatingWindowOptions };
// const SERVICE_BASE_URL =
//   process.env.NEXT_PUBLIC_FLOATING_WINDOW_SERVICE_URL ||
//   "http://127.0.0.1:6415";

// type FloatingWindowOptions = {
//   width?: number;
//   height?: number;
//   alwaysOnTop?: boolean;
//   frame?: boolean;
//   resizable?: boolean;
// };

// type FloatingWindowRecord = {
//   id: number;
//   url: string;
// };

// async function request<T>(
//   path: string,
//   init: RequestInit = {},
//   timeoutMs = 1500,
// ): Promise<T> {
//   const controller = new AbortController();
//   const timeout = setTimeout(() => controller.abort(), timeoutMs);

//   try {
//     const response = await fetch(`${SERVICE_BASE_URL}${path}`, {
//       ...init,
//       headers: {
//         "Content-Type": "application/json",
//         ...(init.headers || {}),
//       },
//       signal: controller.signal,
//     });

//     if (!response.ok) {
//       throw new Error(`Service responded with ${response.status}`);
//     }

//     if (response.status === 204) {
//       return {} as T;
//     }

//     return (await response.json()) as T;
//   } finally {
//     clearTimeout(timeout);
//   }
// }

// export async function checkFloatingService(): Promise<boolean> {
//   try {
//     await request("/health");
//     return true;
//   } catch {
//     return false;
//   }
// }

// export async function openViaFloatingService(
//   url: string,
//   options?: FloatingWindowOptions,
// ): Promise<number> {
//   const payload = JSON.stringify({ url, options });
//   const result = await request<{ id: number }>("/windows", {
//     method: "POST",
//     body: payload,
//   });
//   return result.id;
// }

// export async function listFloatingServiceWindows(): Promise<
//   FloatingWindowRecord[]
// > {
//   const result = await request<{ windows: FloatingWindowRecord[] }>("/windows");
//   return result.windows;
// }

// export async function closeFloatingServiceWindow(
//   windowId: number,
// ): Promise<void> {
//   await request(`/windows/${windowId}`, {
//     method: "DELETE",
//   });
// }

// export function openBrowserFallback(url: string): void {
//   if (typeof window !== "undefined") {
//     window.open(url, "_blank", "noopener,noreferrer");
//   }
// }

// export type { FloatingWindowRecord, FloatingWindowOptions };

