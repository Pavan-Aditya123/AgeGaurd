/**
 * pages/VerificationPage.jsx
 *
 * Desktop QR verification page for restricted movies.
 * Route: /verify/:movieId
 */

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import Navbar from "../components/Navbar";
import RatingBadge from "../components/RatingBadge";
import useMovie from "../hooks/useMovie";
import { createVerificationSession, getVerificationSession } from "../services/verificationService";
import { getFallbackGradient } from "../utils/posterUtils";

export default function VerificationPage() {
  const { movieId } = useParams();
  const navigate = useNavigate();
  const { movie, loading: movieLoading } = useMovie(movieId);

  const [sessionId, setSessionId] = useState(null);
  const [mobileUrl, setMobileUrl] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("pending");
  const [error, setError] = useState(null);
  const [imgError, setImgError] = useState(false);

  // Create session when page loads
  useEffect(() => {
    if (!movieId || movieLoading) return;

    createVerificationSession(movieId)
      .then((data) => {
        setSessionId(data.sessionId);
        setMobileUrl(data.mobileVerifyUrl);
      })
      .catch((err) => setError(err.message));
  }, [movieId, movieLoading]);

  // Poll for upload status after QR is shown
  useEffect(() => {
    if (!sessionId || uploadStatus === "uploaded") return;

    const interval = setInterval(() => {
      getVerificationSession(sessionId)
        .then((data) => {
          if (data.uploadStatus === "uploaded") {
            setUploadStatus("uploaded");
          }
        })
        .catch(() => {});
    }, 3000);

    return () => clearInterval(interval);
  }, [sessionId, uploadStatus]);

  if (movieLoading) {
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

      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
        <button
          onClick={() => navigate(`/movie/${movieId}`)}
          className="flex items-center gap-2 text-white/60 hover:text-white transition-colors mb-8 group"
        >
          <svg className="w-5 h-5 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Movie
        </button>

        <div className="grid md:grid-cols-2 gap-10 items-start">
          {/* Movie info */}
          <div>
            <div className="rounded-2xl overflow-hidden border border-[#2A2A35] shadow-2xl mb-6 max-w-xs">
              {!imgError ? (
                <img
                  src={movie.poster}
                  alt={movie.title}
                  className="w-full aspect-[2/3] object-cover"
                  onError={() => setImgError(true)}
                />
              ) : (
                <div className={`w-full aspect-[2/3] bg-gradient-to-b ${fallbackBg} flex items-center justify-center`}>
                  <span className="font-display text-2xl text-white/40 text-center px-4">{movie.title}</span>
                </div>
              )}
            </div>

            <h1 className="font-display text-4xl text-white tracking-wide mb-2">{movie.title}</h1>
            <div className="flex items-center gap-3 mb-4">
              <RatingBadge rating={movie.rating} size="lg" />
              <span className="text-[#E50914] text-sm font-medium">Age {movie.required_age}+ required</span>
            </div>

            <p className="text-white/70 leading-relaxed">
              This content requires identity verification before playback.
            </p>
          </div>

          {/* QR code */}
          <div className="bg-[#141418] border border-[#2A2A35] rounded-2xl p-8 flex flex-col items-center text-center">
            {error && (
              <p className="text-red-400 mb-4">{error}</p>
            )}

            {uploadStatus === "uploaded" ? (
              <div className="py-8">
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-white text-xl font-semibold mb-2">Verification Submitted</h2>
                <p className="text-white/60 text-sm">
                  Photo captured successfully. Age verification will be processed in the next phase.
                </p>
              </div>
            ) : (
              <>
                <h2 className="text-white text-lg font-semibold mb-2">Scan to Verify</h2>
                <p className="text-white/50 text-sm mb-6">
                  Open your phone camera and scan this QR code to complete identity verification.
                </p>

                {mobileUrl ? (
                  <div className="bg-white p-4 rounded-xl mb-4">
                    <QRCodeSVG value={mobileUrl} size={200} level="M" />
                  </div>
                ) : (
                  <div className="w-[232px] h-[232px] bg-white/5 rounded-xl animate-pulse mb-4" />
                )}

                {sessionId && (
                  <p className="text-white/30 text-xs break-all max-w-xs">
                    Session: {sessionId}
                  </p>
                )}

                <p className="text-white/40 text-xs mt-4">
                  Waiting for mobile verification…
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
