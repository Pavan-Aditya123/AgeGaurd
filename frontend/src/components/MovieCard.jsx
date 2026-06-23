/**
 * components/MovieCard.jsx
 *
 * Individual movie card shown in the grid on HomePage.
 * Uses posterUtils for fallback gradient and ratingUtils via RatingBadge.
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import RatingBadge from "./RatingBadge";
import { getFallbackGradient } from "../utils/posterUtils";

export default function MovieCard({ movie }) {
  const navigate = useNavigate();
  const [imgError, setImgError] = useState(false);
  const fallbackBg = getFallbackGradient(movie.id);

  return (
    <div
      className="movie-card group"
      onClick={() => navigate(`/movie/${movie.id}`)}
    >
      {/* Poster */}
      <div className="relative aspect-[2/3] overflow-hidden">
        {!imgError ? (
          <img
            src={movie.poster}
            alt={movie.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className={`w-full h-full bg-gradient-to-b ${fallbackBg} flex items-center justify-center p-4`}>
            <span className="font-display text-2xl text-white/60 text-center">{movie.title}</span>
          </div>
        )}

        {/* Hover gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#141418] via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* Lock badge for restricted movies */}
        {movie.restricted && (
          <div className="absolute top-2 right-2">
            <div className="bg-[#E50914]/90 backdrop-blur-sm rounded-lg p-1.5 lock-pulse">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z" />
              </svg>
            </div>
          </div>
        )}

        {/* Quick-play overlay */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border-2 border-white/50">
            <svg className="w-6 h-6 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="font-semibold text-white text-sm leading-tight line-clamp-1">
            {movie.title}
          </h3>
          <RatingBadge rating={movie.rating} />
        </div>

        <p className="text-xs text-[#8A8A9A] line-clamp-2 mb-2 leading-relaxed">
          {movie.description}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-xs text-[#8A8A9A] bg-white/5 px-2 py-0.5 rounded-full">
            {movie.category}
          </span>
          <span className="text-xs text-[#8A8A9A]">{movie.year}</span>
        </div>

        {movie.restricted && (
          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#E50914]">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2z" />
            </svg>
            Age verification required
          </div>
        )}
      </div>
    </div>
  );
}
