/**
 * utils/networkUtils.js
 *
 * Builds the mobile verification base URL for QR codes.
 * Phones cannot use localhost — must use the laptop's LAN IP + correct port.
 *
 * Configuration priority:
 * 1. REACT_APP_MOBILE_BASE_URL (full URL)
 * 2. REACT_APP_SERVER_IP + port + HTTPS flag
 * 3. Current browser origin (when not localhost)
 */

function buildUrlFromParts() {
  const ip = process.env.REACT_APP_SERVER_IP;
  const port = process.env.REACT_APP_FRONTEND_PORT || "3000";
  const useHttps = (process.env.REACT_APP_USE_HTTPS || "true").toLowerCase() !== "false";
  if (!ip) return null;
  const scheme = useHttps ? "https" : "http";
  return `${scheme}://${ip}:${port}`;
}

/**
 * Base URL phones should use to reach this dev server.
 */
export function getMobileBaseUrl() {
  const explicit = process.env.REACT_APP_MOBILE_BASE_URL;
  if (explicit) {
    return explicit.replace(/\/$/, "");
  }

  const fromParts = buildUrlFromParts();
  if (fromParts) {
    return fromParts;
  }

  const { protocol, hostname, port } = window.location;
  const isLocal = hostname === "localhost" || hostname === "127.0.0.1";

  if (!isLocal) {
    const portSuffix = port ? `:${port}` : "";
    return `${protocol}//${hostname}${portSuffix}`;
  }

  console.warn(
    "Set REACT_APP_MOBILE_BASE_URL or REACT_APP_SERVER_IP in frontend/.env, or run: npm run update-network"
  );
  return window.location.origin;
}

export function getMobileVerifyUrl(sessionId) {
  return `${getMobileBaseUrl()}/mobile-verify/${sessionId}`;
}
