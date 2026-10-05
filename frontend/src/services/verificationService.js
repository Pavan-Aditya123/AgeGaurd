/**
 * services/verificationService.js
 *
 * API layer for QR verification and face photo upload (Phase 3).
 */

function getBackendUrl() {
  // When on mobile, we need to use the backend IP and port
  const ip = process.env.REACT_APP_SERVER_IP;
  const port = process.env.REACT_APP_BACKEND_PORT || "5000";
  
  if (ip) {
    // Backend uses HTTP (Flask dev server doesn't have SSL)
    return `http://${ip}:${port}`;
  }
  
  // Fallback to proxy for desktop
  return "";
}

const BASE_URL = getBackendUrl();

/**
 * Create a verification session for a restricted movie.
 * @param {number|string} movieId
 * @returns {Promise<{ sessionId, movieId, mobileVerifyUrl }>}
 */
export async function createVerificationSession(movieId) {
  const response = await fetch(`${BASE_URL}/api/verification/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ movieId: Number(movieId) }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Failed to create session (status ${response.status})`);
  }

  return response.json();
}

/**
 * Fetch session status by sessionId.
 * @param {string} sessionId
 */
export async function getVerificationSession(sessionId) {
  const response = await fetch(`${BASE_URL}/api/verification/session/${sessionId}`);

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Session not found (status ${response.status})`);
  }

  return response.json();
}

/**
 * Upload a captured face photo as base64 JPEG.
 * @param {string} sessionId
 * @param {string} imageBase64  JPEG data URL or raw base64 string
 */
export async function uploadFaceImage(sessionId, imageBase64) {
  const response = await fetch(`${BASE_URL}/api/upload-face`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId, image: imageBase64 }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Upload failed (status ${response.status})`);
  }

  return response.json();
}
