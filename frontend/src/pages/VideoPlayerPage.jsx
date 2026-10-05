/**
 * pages/VideoPlayerPage.jsx
 *
 * Fullscreen video player with access control for restricted titles.
 */

import React, { useRef, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import useMovie from "../hooks/useMovie";
import {
  checkPlaybackAccess,
  getVerifiedSessionId,
} from "../utils/verificationAccess";

export default function VideoPlayerPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { movie, loading } = useMovie(id);
  const videoRef = useRef(null);
  const [accessChecked, setAccessChecked] = useState(false);
  const [accessDenied, setAccessDenied] = useState(false);

  const videoPath = movie?.video ? encodeURI(movie.video) : null;

  // Debug: log the resolved video URL whenever movie data is available
  useEffect(() => {
    if (!movie) return;
    console.log("Video Path:", videoPath);
    console.log("Raw video field:", movie.video);
    console.log("Movie restricted:", movie.restricted);
  }, [movie, videoPath]);

  useEffect(() => {
    if (loading || !movie) return;

    async function verifyAccess() {
      if (!movie.restricted) {
        setAccessChecked(true);
        return;
      }

      const sessionId = getVerifiedSessionId(id);
      if (!sessionId) {
        setAccessDenied(true);
        setAccessChecked(true);
        return;
      }

      const allowed = await checkPlaybackAccess(id, sessionId);
      setAccessDenied(!allowed);
      setAccessChecked(true);
    }

    verifyAccess();
  }, [loading, movie, id]);

  useEffect(() => {
    if (!accessChecked || accessDenied) return;

    const video = videoRef.current;
    if (!video) return;

    const tryPlay = () => {
      video.play().catch(() => {});
    };

    video.addEventListener("loadeddata", tryPlay);
    return () => video.removeEventListener("loadeddata", tryPlay);
  }, [accessChecked, accessDenied, videoPath]);

  if (loading || !accessChecked) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center">
        <p className="text-white/40 animate-pulse">Loading player…</p>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="fixed inset-0 bg-black flex flex-col items-center justify-center gap-4">
        <p className="text-white">Movie not found.</p>
        <button onClick={() => navigate("/")} className="btn-secondary">Back to Home</button>
      </div>
    );
  }

  if (accessDenied) {
    return (
      <div className="fixed inset-0 bg-black flex flex-col items-center justify-center gap-4 px-6 text-center">
        <p className="text-[#E50914] text-xl font-semibold">Age verification required</p>
        <p className="text-white/60 max-w-md">
          Complete identity verification before watching {movie.title}.
        </p>
        <button onClick={() => navigate(`/verify/${id}`)} className="btn-primary px-8 py-3">
          Verify & Watch
        </button>
        <button onClick={() => navigate(`/movie/${id}`)} className="btn-secondary px-6 py-3">
          Back to Details
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black flex flex-col">
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
          <p className="text-white font-semibold">{movie.title}</p>
          <p className="text-white/50 text-xs">{movie.category}</p>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center">
        {videoPath ? (
          <video
            ref={videoRef}
            key={videoPath}
            controls
            autoPlay
            playsInline
            className="w-full h-full object-contain"
          >
            <source src={videoPath} type="video/mp4" />
            Your browser does not support HTML5 video.
          </video>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <p className="text-white/60">Video file not available for this title.</p>
            <p className="text-white/30 text-xs">video field: {String(movie?.video)}</p>
          </div>
        )}
      </div>
    </div>
  );
}
