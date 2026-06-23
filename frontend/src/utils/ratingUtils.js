/**
 * utils/ratingUtils.js
 *
 * Pure helper functions for age-rating logic.
 * Centralised here so rating rules never get duplicated across components.
 *
 * Future phases will extend these for access-control decisions.
 */

/**
 * Returns Tailwind CSS classes for a given rating string.
 * @param {string} rating  e.g. "U", "U/A 13+", "A (18+)"
 * @returns {string} Tailwind class string
 */
export function getRatingColorClasses(rating) {
  if (rating === "U")            return "bg-green-600 text-white";
  if (rating.includes("U/A"))   return "bg-yellow-500 text-black";
  if (rating.includes("A"))     return "bg-red-600 text-white";
  return "bg-gray-600 text-white";
}

/**
 * Returns a human-readable access label for a movie.
 * @param {Object} movie
 * @returns {string}
 */
export function getAccessLabel(movie) {
  if (!movie.restricted) return "Open";
  return `Age ${movie.required_age}+ Required`;
}

/**
 * Checks whether a given age meets the movie's required age.
 * Used by the access-control engine in Phase 6.
 * @param {number} predictedAge
 * @param {number} requiredAge
 * @returns {boolean}
 */
export function isAgeEligible(predictedAge, requiredAge) {
  return predictedAge >= requiredAge;
}
