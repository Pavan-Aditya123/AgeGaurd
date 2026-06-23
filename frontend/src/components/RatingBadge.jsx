/**
 * components/RatingBadge.jsx
 *
 * Displays a coloured rating pill (U / U/A / A).
 * Colour logic pulled from utils/ratingUtils.js — not hardcoded here.
 */

import React from "react";
import { getRatingColorClasses } from "../utils/ratingUtils";

export default function RatingBadge({ rating, size = "sm" }) {
  const colorClass = getRatingColorClasses(rating);
  const sizeClass  = size === "lg"
    ? "text-sm px-3 py-1 rounded-md"
    : "text-xs px-2 py-0.5 rounded";

  return (
    <span className={`font-bold ${colorClass} ${sizeClass}`}>
      {rating}
    </span>
  );
}
