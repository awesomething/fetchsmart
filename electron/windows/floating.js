const { BrowserWindow } = require("electron");
const { URL } = require("url");

const floatingWindows = new Map();

function sanitizeUrl(rawUrl) {
  if (!rawUrl || typeof rawUrl !== "string") {
    throw new Error("URL is required");
  }

  let normalized = rawUrl.trim();
  if (!/^https?:\/\//i.test(normalized)) {
    normalized = `https://${normalized}`;
  }

  const parsed = new URL(normalized);
  return parsed.toString();
}

function createFloatingWindow(rawUrl, options = {}) {
  const targetUrl = sanitizeUrl(rawUrl);

  const floatingWindow = new BrowserWindow({
    width: options.width || 900,
    height: options.height || 700,
    alwaysOnTop: options.alwaysOnTop !== false,
    frame: options.frame !== false,
    resizable: options.resizable !== false,
    backgroundColor: "#000000",
    show: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
  });

  floatingWindow.loadURL(targetUrl);

  const id = floatingWindow.id;
  floatingWindows.set(id, { window: floatingWindow, url: targetUrl });

  floatingWindow.on("closed", () => {
    floatingWindows.delete(id);
  });

  return id;
}

function closeFloatingWindow(windowId) {
  const record = floatingWindows.get(windowId);
  if (!record) {
    return;
  }

  const { window } = record;
  if (!window.isDestroyed()) {
    window.close();
  }

  floatingWindows.delete(windowId);
}

function listFloatingWindows() {
  return Array.from(floatingWindows.entries()).map(([id, meta]) => ({
    id,
    url: meta.url,
  }));
}

module.exports = {
  createFloatingWindow,
  closeFloatingWindow,
  listFloatingWindows,
};

