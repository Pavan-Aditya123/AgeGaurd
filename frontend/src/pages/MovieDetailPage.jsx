/**
 * pages/MovieDetailPage.jsx
 *
 * Full detail view for a single movie.
 * Data fetched via useMovie(id) hook.
 * Phase 2 will replace handlePlay() with QR generation logic.
 */

import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar      from "../components/Navbar";
import RatingBadge from "../components/RatingBadge";
import useMovie    from "../hooks/useMovie";
import { getAccessLabel } from "../utils/ratingUtils";
import { getFallbackGradient } from "../utils/posterUtils";

export default function MovieDetailPage() {
  const { id }       = useParams();
  const navigate     = useNavigate();
  const { movie, loading } = useMovie(id);
  const [imgError, setImgError] = useState(false);

  /**
   * handlePlay()
   * Phase 1: Navigate directly to player.
   * Phase 2: Will trigger QR code generation for restricted movies.
   */
  const handlePlay = () => {
    navigate(`/watch/${id}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center">
        <div className="text-white/40 animate-pulse text-lg">Loading...</div>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex flex-col items-center justify-center gap-4">
        <p className="text-white text-xl">Movie not found.</p>
        <button onClick={() => navigate("/")} className="btn-secondary">Back to Home</button>
      </div>
    );
  }

  const fallbackBg = getFallbackGradient(movie.id);

  return (
    <div className="min-h-screen bg-[#0A0A0F]">
      <Navbar />

      {/* Blurred background */}
      <div className="fixed inset-0 z-0">
        {!imgError && (
          <img
            src={movie.poster}
            alt=""
            className="w-full h-full object-cover opacity-10 scale-110"
            style={{ filter: "blur(20px)" }}
            onError={() => setImgError(true)}
          />
        )}
        <div className="absolute inset-0 bg-[#0A0A0F]/80" />
      </div>

      <div className="relative z-10 pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto">

        {/* Back */}
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2 text-white/60 hover:text-white transition-colors mb-8 group"
        >
          <svg className="w-5 h-5 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Home
        </button>

        <div className="flex flex-col md:flex-row gap-10">
          {/* Poster */}
          <div className="flex-shrink-0 w-full md:w-64">
            <div className="rounded-2xl overflow-hidden border border-[#2A2A35] shadow-2xl shadow-black/50">
              {!imgError ? (
                <img
                  src={movie.poster}
                  alt={movie.title}
                  className="w-full aspect-[2/3] object-cover"
                  onError={() => setImgError(true)}
                />
              ) : (
                <div className={`w-full aspect-[2/3] bg-gradient-to-b ${fallbackBg} flex items-center justify-center`}>
                  <span className="font-display text-3xl text-white/40 text-center px-4">{movie.title}</span>
                </div>
              )}
            </div>

            {movie.restricted && (
              <div className="mt-4 bg-[#E50914]/10 border border-[#E50914]/30 rounded-xl p-3 flex items-start gap-2">
                <svg className="w-4 h-4 text-[#E50914] flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2z" />
                </svg>
                <p className="text-[#E50914] text-xs leading-relaxed">
                  Age verification required. You must be {movie.required_age}+ to watch.
                </p>
              </div>
            )}
          </div>

          {/* Details */}
          <div className="flex-1">
            <p className="text-[#E50914] text-xs font-bold uppercase tracking-widest mb-2">{movie.category}</p>

            <h1 className="font-display text-5xl sm:text-6xl text-white tracking-wide leading-none mb-4">
              {movie.title}
            </h1>

            <div className="flex items-center gap-3 flex-wrap mb-6">
              <RatingBadge rating={movie.rating} size="lg" />
              <span className="text-white/50 text-sm">{movie.year}</span>
              <span className="w-1 h-1 bg-white/30 rounded-full" />
              <span className="text-white/50 text-sm">{movie.duration}</span>
              {movie.restricted && (
                <>
                  <span className="w-1 h-1 bg-white/30 rounded-full" />
                  <span className="text-[#E50914] text-sm font-medium">Age {movie.required_age}+</span>
                </>
              )}
            </div>

            <p className="text-white/70 leading-relaxed mb-8 max-w-lg">{movie.description}</p>

            <div className="flex items-center gap-3 flex-wrap">
              <button onClick={handlePlay} className="btn-primary text-base px-8 py-3">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
                {movie.restricted ? "Verify & Watch" : "Play Now"}
              </button>
              <button onClick={() => navigate("/")} className="btn-secondary text-base px-6 py-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Browse More
              </button>
            </div>

            {/* Info cards */}
            <div className="grid grid-cols-3 gap-3 mt-10">
              <div className="bg-[#141418] border border-[#2A2A35] rounded-xl p-4">
                <p className="text-[#8A8A9A] text-xs mb-1">Category</p>
                <p className="text-white text-sm font-medium">{movie.category}</p>
              </div>
              <div className="bg-[#141418] border border-[#2A2A35] rounded-xl p-4">
                <p className="text-[#8A8A9A] text-xs mb-1">Rating</p>
                <p className="text-white text-sm font-medium">{movie.rating}</p>
              </div>
              <div className="bg-[#141418] border border-[#2A2A35] rounded-xl p-4">
                <p className="text-[#8A8A9A] text-xs mb-1">Access</p>
                <p className={`text-sm font-medium ${movie.restricted ? "text-[#E50914]" : "text-green-400"}`}>
                  {getAccessLabel(movie)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
