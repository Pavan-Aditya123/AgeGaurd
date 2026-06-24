/**
 * utils/verificationAccess.js
 *
 * Client-side cache of verified movie access (backed by sessionStorage).
 * Playback for restricted titles requires a valid verified session from the backend.
 */

const STORAGE_KEY = "ageguard_verified_access";

function readStore() {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function writeStore(store) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

/**
 * Save verified access after desktop polling confirms verification passed.
 */
export function saveVerifiedAccess(movieId, sessionId) {
  const store = readStore();
  store[String(movieId)] = {
    sessionId,
    verifiedAt: Date.now(),
  };
  writeStore(store);
}

export function getVerifiedSessionId(movieId) {
  const entry = readStore()[String(movieId)];
  return entry?.sessionId ?? null;
}

export function clearVerifiedAccess(movieId) {
  const store = readStore();
  delete store[String(movieId)];
  writeStore(store);
}

/**
 * Ask backend whether this session still grants playback.
 */
export async function checkPlaybackAccess(movieId, sessionId) {
  const params = new URLSearchParams({
    movieId: String(movieId),
    sessionId,
  });

  const response = await fetch(`/api/verification/access?${params}`);
  if (!response.ok) {
    return false;
  }

  const data = await response.json();
  return data.allowed === true;
}
