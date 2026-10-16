/**
 * services/verificationService.js
 *
 * All API calls go to the same origin (port 3000) — both desktop and mobile.
 * The React dev server proxies /api/* → Flask :5000 (HTTP).
 *
 * This means:
 *   Desktop: https://localhost:3000/api/... → proxy → http://localhost:5000
 *   Mobile:  https://192.168.40.134:3000/api/... → proxy → http://localhost:5000
 *
 * No mixed content, no direct port-5000 access needed.
 */

// Always use same origin — let the proxy handle forwarding to Flask
const BASE_URL = "";

export async function createVerificationSession(movieId) {
  const res = await fetch(`${BASE_URL}/api/verification/session`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ movieId: Number(movieId) }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Failed to create session (${res.status})`);
  }
  return res.json();
}

export async function getVerificationSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/verification/session/${sessionId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Session not found (${res.status})`);
  }
  return res.json();
}

export async function uploadFaceImage(sessionId, imageBase64) {
  const res = await fetch(`${BASE_URL}/api/upload-face`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ sessionId, image: imageBase64 }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Upload failed (${res.status})`);
  }
  return res.json();
}
