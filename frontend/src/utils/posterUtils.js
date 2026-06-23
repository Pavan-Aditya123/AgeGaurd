/**
 * utils/posterUtils.js
 *
 * Helpers for poster/image display logic.
 */

const FALLBACK_GRADIENTS = [
  "from-red-900 to-gray-900",
  "from-blue-900 to-gray-900",
  "from-purple-900 to-gray-900",
  "from-green-900 to-gray-900",
];

/**
 * Returns a Tailwind gradient class based on movie ID.
 * Used when a poster image fails to load.
 * @param {number} id  Movie ID
 * @returns {string}
 */
export function getFallbackGradient(id) {
  return FALLBACK_GRADIENTS[id % FALLBACK_GRADIENTS.length];
}
