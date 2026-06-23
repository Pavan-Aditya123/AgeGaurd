/**
 * pages/HomePage.jsx
 *
 * Main OTT landing page.
 * Data fetched via useMovies() hook (not inline fetch).
 */

import React, { useState } from "react";
import Navbar     from "../components/Navbar";
import HeroBanner from "../components/HeroBanner";
import MovieCard  from "../components/MovieCard";
import useMovies  from "../hooks/useMovies";

const FILTERS = ["All", "Free", "18+"];

export default function HomePage() {
  const { movies, loading, error } = useMovies();
  const [filter, setFilter] = useState("All");

  const filteredMovies = movies.filter((m) => {
    if (filter === "Free") return !m.restricted;
    if (filter === "18+")  return m.restricted;
    return true;
  });

  const featured = movies.find((m) => m.id === 2) || movies[0];

  return (
    <div className="min-h-screen bg-[#0A0A0F]">
      <Navbar />

      {!loading && !error && <HeroBanner featuredMovie={featured} />}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

        {/* Section header + filter */}
        <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
          <div>
            <h2 className="font-display text-3xl text-white tracking-wide">ALL TITLES</h2>
            <p className="text-[#8A8A9A] text-sm mt-1">{filteredMovies.length} titles available</p>
          </div>

          <div className="flex items-center gap-2 bg-[#141418] border border-[#2A2A35] rounded-xl p-1">
            {FILTERS.map((cat) => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  filter === cat ? "bg-[#E50914] text-white" : "text-[#8A8A9A] hover:text-white"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Loading skeleton */}
        {loading && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-[#141418] rounded-xl overflow-hidden animate-pulse">
                <div className="aspect-[2/3] bg-[#2A2A35]" />
                <div className="p-3 space-y-2">
                  <div className="h-4 bg-[#2A2A35] rounded" />
                  <div className="h-3 bg-[#2A2A35] rounded w-2/3" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="w-16 h-16 bg-red-900/30 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-[#E50914]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-2.694-.833-3.464 0L3.34 16.5C2.57 18.333 3.532 20 5.072 20z" />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-white font-semibold">Could not connect to backend</p>
              <p className="text-[#8A8A9A] text-sm mt-1">Make sure Flask is running on port 5000</p>
              <p className="text-[#E50914] text-xs mt-1 font-mono">{error}</p>
            </div>
          </div>
        )}

        {/* Movie grid */}
        {!loading && !error && (
          filteredMovies.length === 0 ? (
            <div className="text-center py-20 text-[#8A8A9A]">No movies found for this filter.</div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {filteredMovies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          )
        )}

        {/* Info banner */}
        {!loading && !error && (
          <div className="mt-16 bg-[#141418] border border-[#2A2A35] rounded-2xl p-6 flex items-start gap-4">
            <div className="w-10 h-10 bg-[#E50914]/10 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-[#E50914]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
              </svg>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-1">AI-Powered Age Verification</h3>
              <p className="text-[#8A8A9A] text-sm leading-relaxed">
                Titles marked with a <span className="text-[#E50914] font-medium">lock icon</span> require
                real-time facial age verification before playback. A unique QR code will be generated — scan
                it with your phone to complete a quick liveness check. No ID cards needed.
              </p>
            </div>
          </div>
        )}
      </div>

      <footer className="border-t border-[#2A2A35] mt-10 py-8 px-4 text-center text-[#8A8A9A] text-xs">
        <p className="font-display text-base text-white/20 tracking-widest mb-2">AGEGUARD</p>
        <p>AI-Powered Age Verification for OTT Platforms · B.Tech Final Year Project</p>
      </footer>
    </div>
  );
}
