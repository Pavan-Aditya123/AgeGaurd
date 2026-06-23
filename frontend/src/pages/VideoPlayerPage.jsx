/**
 * pages/VideoPlayerPage.jsx
 *
 * Fullscreen video player.
 * Data fetched via useMovie(id) hook.
 * Phase 2+ will add: session token validation before allowing playback.
 */

import React, { useRef, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import useMovie from "../hooks/useMovie";

const TRAILER_PATH = "/Videos/Kung Fu Panda_Trailer.mp4";

export default function VideoPlayerPage() {
  const { id }    = useParams();
  const navigate  = useNavigate();
  const { movie } = useMovie(id);
  const videoRef  = useRef(null);

  // Temporarily use the same local trailer for every movie.
  const videoPath = encodeURI(TRAILER_PATH);

  useEffect(() => {
    console.log("Movie:", movie);
    console.log("Video Path:", videoPath);
  }, [movie, videoPath]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const tryPlay = () => {
      video.play().catch((err) => {
        console.warn("Autoplay blocked, user must press play:", err.message);
      });
    };

    video.addEventListener("loadeddata", tryPlay);
    return () => video.removeEventListener("loadeddata", tryPlay);
  }, [videoPath]);

  const handleVideoError = (e) => {
    const el = e.target;
    console.error("Video error:", el.error?.code, el.error?.message);
    console.error("Video src:", el.currentSrc || el.src);
  };

  return (
    <div className="fixed inset-0 bg-black flex flex-col">
      {/* Top bar */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-gradient-to-b from-black/80 to-transparent px-6 py-4 flex items-center gap-4">
        <button
          onClick={() => navigate(`/movie/${id}`)}
          className="text-white/70 hover:text-white transition-colors"
          aria-label="Back to movie details"
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

      {/* HTML5 video player */}
      <div className="flex-1 flex items-center justify-center">
        <video
          ref={videoRef}
          key={videoPath}
          controls
          autoPlay
          playsInline
          className="w-full h-full object-contain"
          onError={handleVideoError}
        >
          <source src={videoPath} type="video/mp4" />
          Your browser does not support HTML5 video.
        </video>
      </div>
    </div>
  );
}
