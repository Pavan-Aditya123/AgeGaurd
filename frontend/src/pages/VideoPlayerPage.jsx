/**
 * pages/VideoPlayerPage.jsx
 *
 * Fullscreen video player.
 * Data fetched via useMovie(id) hook.
 * Phase 2+ will add: session token validation before allowing playback.
 */

import React, { useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import useMovie from "../hooks/useMovie";

const SAMPLE_VIDEO =
  "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4";

export default function VideoPlayerPage() {
  const { id }      = useParams();
  const navigate    = useNavigate();
  const { movie }   = useMovie(id);
  const videoRef    = useRef(null);

  const [playing, setPlaying]           = useState(false);
  const [showControls, setShowControls] = useState(true);
  const controlsTimer                   = useRef(null);

  const handleMouseMove = () => {
    setShowControls(true);
    clearTimeout(controlsTimer.current);
    controlsTimer.current = setTimeout(() => {
      if (playing) setShowControls(false);
    }, 3000);
  };

  const togglePlay = () => {
    if (!videoRef.current) return;
    playing ? videoRef.current.pause() : videoRef.current.play();
    setPlaying(!playing);
  };

  return (
    <div
      className="fixed inset-0 bg-black flex flex-col"
      onMouseMove={handleMouseMove}
    >
      {/* Top bar */}
      <div
        className={`absolute top-0 left-0 right-0 z-20 bg-gradient-to-b from-black/80 to-transparent
          px-6 py-4 flex items-center gap-4 transition-opacity duration-300
          ${showControls ? "opacity-100" : "opacity-0"}`}
      >
        <button
          onClick={() => navigate(`/movie/${id}`)}
          className="text-white/70 hover:text-white transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <p className="text-white font-semibold">{movie?.title || "Loading..."}</p>
          <p className="text-white/50 text-xs">{movie?.category}</p>
        </div>
      </div>

      {/* Video */}
      <video
        ref={videoRef}
        className="w-full h-full object-contain fade-in"
        src={SAMPLE_VIDEO}
        onClick={togglePlay}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
      />

      {/* Centre play button */}
      {!playing && (
        <button
          onClick={togglePlay}
          className="absolute inset-0 flex items-center justify-center z-10"
        >
          <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border-2 border-white/50 hover:bg-white/30 transition-all">
            <svg className="w-10 h-10 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </button>
      )}

      {/* Bottom controls */}
      <div
        className={`absolute bottom-0 left-0 right-0 z-20 bg-gradient-to-t from-black/80 to-transparent
          px-6 py-6 transition-opacity duration-300 ${showControls ? "opacity-100" : "opacity-0"}`}
      >
        <div className="flex items-center gap-4">
          <button onClick={togglePlay} className="text-white hover:text-white/70 transition-colors">
            {playing ? (
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              </svg>
            ) : (
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>
          <div className="flex-1 h-1 bg-white/20 rounded-full">
            <div className="h-full bg-[#E50914] rounded-full w-0" />
          </div>
          <button
            onClick={() => navigate(`/movie/${id}`)}
            className="text-white/60 hover:text-white text-sm transition-colors"
          >
            Exit
          </button>
        </div>
        <p className="text-white/30 text-xs mt-3 text-center">
          Phase 1 · Sample video · Age verification will be added in Phase 2
        </p>
      </div>
    </div>
  );
}
