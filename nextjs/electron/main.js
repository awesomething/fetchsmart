const { app } = require("electron");
const http = require("http");
const {
  createFloatingWindow,
  closeFloatingWindow,
  listFloatingWindows,
} = require("./windows/floating");

const SERVICE_PORT = Number(process.env.FLOATING_WINDOW_PORT || 6415);

function setCorsHeaders(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader(
    "Access-Control-Allow-Methods",
    "GET,POST,DELETE,OPTIONS",
  );
  res.setHeader(
    "Access-Control-Allow-Headers",
    "Content-Type, Authorization",
  );
}

function sendJson(res, statusCode, payload) {
  setCorsHeaders(res);
  if (statusCode === 204) {
    res.writeHead(statusCode);
    res.end();
    return;
  }
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, { "Content-Type": "application/json" });
  res.end(body);
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let rawData = "";
    req.on("data", chunk => {
      rawData += chunk;
    });
    req.on("end", () => {
      try {
        resolve(rawData ? JSON.parse(rawData) : {});
      } catch (error) {
        reject(error);
      }
    });
    req.on("error", reject);
  });
}

function startServer() {
  const server = http.createServer(async (req, res) => {
    if (!req.url) {
      sendJson(res, 400, { error: "Invalid request" });
      return;
    }

    if (req.method === "OPTIONS") {
      setCorsHeaders(res);
      res.writeHead(204);
      res.end();
      return;
    }

    const url = new URL(req.url, `http://localhost:${SERVICE_PORT}`);
    const pathname = url.pathname;

    try {
      if (req.method === "GET" && pathname === "/health") {
        sendJson(res, 200, { status: "ok" });
        return;
      }

      if (req.method === "GET" && pathname === "/windows") {
        const windows = listFloatingWindows();
        sendJson(res, 200, { windows });
        return;
      }

      if (req.method === "POST" && pathname === "/windows") {
        const body = await parseBody(req);
        if (!body.url) {
          sendJson(res, 400, { error: "url is required" });
          return;
        }
        const id = createFloatingWindow(body.url, body.options);
        sendJson(res, 201, { id });
        return;
      }

      if (req.method === "DELETE" && pathname.startsWith("/windows/")) {
        const id = Number(pathname.split("/").pop());
        if (Number.isNaN(id)) {
          sendJson(res, 400, { error: "Invalid window id" });
          return;
        }
        closeFloatingWindow(id);
        sendJson(res, 204, {});
        return;
      }

      sendJson(res, 404, { error: "Route not found" });
    } catch (error) {
      console.error("Floating window server error:", error);
      sendJson(res, 500, { error: "Internal server error" });
    }
  });

  server.listen(SERVICE_PORT, "127.0.0.1", () => {
    console.log(
      `Floating window companion listening on http://127.0.0.1:${SERVICE_PORT}`,
    );
  });
}

app.whenReady().then(() => {
  startServer();
});

