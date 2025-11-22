// Deno Web Server for IPv6 Tools
// Usage: deno run --allow-net --allow-read server.ts [--port 8000]

import { parse } from "https://deno.land/std@0.208.0/flags/mod.ts";
import { serveDir } from "https://deno.land/std@0.208.0/http/file_server.ts";

const flags = parse(Deno.args, {
  string: ["port", "host"],
  default: {
    port: "8000",
    host: "localhost",
  },
});

const port = parseInt(flags.port);
const host = flags.host;

console.log(`🌐 IPv6 Tools Web Server`);
console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
console.log(`Starting server...`);
console.log(`Host: ${host}`);
console.log(`Port: ${port}`);
console.log(`URL: http://${host}:${port}/`);
console.log(`IPv6 URL: http://[::1]:${port}/`);
console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
console.log(`Press Ctrl+C to stop`);
console.log();

Deno.serve({
  port,
  hostname: host,
  onListen: ({ hostname, port }) => {
    console.log(`✓ Server listening on ${hostname}:${port}`);
  },
}, (req) => {
  const url = new URL(req.url);
  const pathname = url.pathname;

  // Logging
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${pathname}`);

  // API endpoints
  if (pathname.startsWith("/api/")) {
    return handleAPI(pathname, req);
  }

  // Serve static files
  return serveDir(req, {
    fsRoot: "./",
    showIndex: true,
    showDirListing: true,
  });
});

async function handleAPI(pathname: string, req: Request): Promise<Response> {
  const headers = new Headers({
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
  });

  try {
    // Parse request body if present
    const body = req.method === "POST" ? await req.json() : {};

    // Route API calls
    if (pathname === "/api/validate") {
      return new Response(
        JSON.stringify({
          valid: true,
          message: "Address validation endpoint",
        }),
        { headers }
      );
    }

    if (pathname === "/api/calculate") {
      return new Response(
        JSON.stringify({
          network: "2001:db8::/32",
          subnets: 4,
        }),
        { headers }
      );
    }

    if (pathname === "/api/generate") {
      return new Response(
        JSON.stringify({
          type: body.type || "link-local",
          address: "fe80::1",
        }),
        { headers }
      );
    }

    // 404 for unknown endpoints
    return new Response(
      JSON.stringify({
        error: "Endpoint not found",
        path: pathname,
      }),
      { status: 404, headers }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        message: error.message,
      }),
      { status: 500, headers }
    );
  }
}
