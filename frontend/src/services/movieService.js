/**
 * services/movieService.js
 *
 * Centralised API layer for all movie-related HTTP calls.
 * All fetch() calls to the Flask backend live here.
 *
 * Future phases will add:
 *   - generateQRCode(movieId)   → Phase 2
 *   - pollVerificationStatus()  → Phase 2
 *   - submitVerification()      → Phase 3
 */

const BASE_URL = "";   // Empty = uses CRA proxy (localhost:5000)

/**
 * Fetch all movies from the backend.
 * @returns {Promise<Array>} Array of movie objects
 */
export async function fetchAllMovies() {
  const response = await fetch(`${BASE_URL}/movies`);
  if (!response.ok) {
    throw new Error(`Failed to fetch movies (status ${response.status})`);
  }
  return response.json();
}

/**
 * Fetch a single movie by ID.
 * @param {number|string} id  Movie ID
 * @returns {Promise<Object>} Movie object
 */
export async function fetchMovieById(id) {
  const response = await fetch(`${BASE_URL}/movies/${id}`);
  if (!response.ok) {
    throw new Error(`Movie not found (status ${response.status})`);
  }
  return response.json();
}

/**
 * Health-check the Flask backend.
 * @returns {Promise<Object>} { status, message }
 */
export async function checkBackendHealth() {
  const response = await fetch(`${BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("Backend health check failed");
  }
  return response.json();
}
