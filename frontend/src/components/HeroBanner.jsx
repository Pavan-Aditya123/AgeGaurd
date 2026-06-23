import React from "react";
import { useNavigate } from "react-router-dom";

export default function HeroBanner({ featuredMovie }) {
  const navigate = useNavigate();

  if (!featuredMovie) {
    return (
      <div className="relative h-[70vh] bg-gradient-to-br from-[#1a0a0a] to-[#0A0A0F] flex items-center justify-center">
        <div className="text-white/20 text-2xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="relative h-[85vh] min-h-[500px] overflow-hidden">
      {/* Background poster */}
      <div className="absolute inset-0">
        <img
          src={featuredMovie.poster}
          alt={featuredMovie.title}
          className="w-full h-full object-cover object-top scale-105"
          style={{ filter: "blur(2px)" }}
        />
        <div className="absolute inset-0 bg-[#0A0A0F]/60" />
      </div>

      {/* Gradient bottom fade */}
      <div className="absolute inset-0 hero-gradient" />

      {/* Side vignette */}
      <div className="absolute inset-0 bg-gradient-to-r from-[#0A0A0F] via-transparent to-transparent" />

      {/* Content */}
      <div className="relative z-10 h-full flex items-end pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="max-w-xl">
          {/* Tag */}
          <div className="flex items-center gap-2 mb-4">
            <span className="text-[#E50914] text-xs font-bold uppercase tracking-widest">
              Featured
            </span>
            <span className="w-8 h-px bg-[#E50914]" />
          </div>

          {/* Title */}
          <h1 className="font-display text-6xl sm:text-7xl text-white tracking-wide leading-none mb-4">
            {featuredMovie.title}
          </h1>

          {/* Meta */}
          <div className="flex items-center gap-3 mb-4">
            <span className="text-white/60 text-sm">{featuredMovie.year}</span>
            <span className="w-1 h-1 bg-white/30 rounded-full" />
            <span className="text-white/60 text-sm">{featuredMovie.duration}</span>
            <span className="w-1 h-1 bg-white/30 rounded-full" />
            <span className="text-xs font-semibold bg-yellow-500 text-black px-2 py-0.5 rounded">
              {featuredMovie.rating}
            </span>
          </div>

          {/* Description */}
          <p className="text-white/70 text-sm leading-relaxed mb-6 line-clamp-3">
            {featuredMovie.description}
          </p>

          {/* Buttons */}
          <div className="flex items-center gap-3 flex-wrap">
            <button
              className="btn-primary"
              onClick={() => navigate(`/movie/${featuredMovie.id}`)}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
              Watch Now
            </button>
            <button
              className="btn-secondary"
              onClick={() => navigate(`/movie/${featuredMovie.id}`)}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              More Info
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
