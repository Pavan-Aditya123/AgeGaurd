/**
 * pages/VerificationPage.jsx
 *
 * Desktop QR verification page for restricted movies.
 * Polls backend every 2 s for session status.
 * Handles: verified (ALLOW) | denied (RESTRICT) | recapture (RECAPTURE)
 */

import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import Navbar from "../components/Navbar";
import RatingBadge from "../components/RatingBadge";
import useMovie from "../hooks/useMovie";
import { createVerificationSession, getVerificationSession } from "../services/verificationService";
import { getFallbackGradient } from "../utils/posterUtils";
import { getMobileVerifyUrl } from "../utils/networkUtils";
import { saveVerifiedAccess } from "../utils/verificationAccess";

export default function VerificationPage() {
  const { movieId } = useParams();
  const navigate    = useNavigate();
  const { movie, loading: movieLoading } = useMovie(movieId);

  const [sessionId, setSessionId]                   = useState(null);
  const [mobileUrl, setMobileUrl]                   = useState(null);
  const [verificationStatus, setVerificationStatus] = useState("pending");
  const [predictedAge, setPredictedAge]             = useState(null);
  const [reason, setReason]                         = useState(null);
  const [error, setError]                           = useState(null);
  const [imgError, setImgError]                     = useState(false);

  const startSession = useCallback(() => {
    setError(null);
    createVerificationSession(movieId)
      .then((data) => {
        setSessionId(data.sessionId);
        setMobileUrl(getMobileVerifyUrl(data.sessionId));
      })
      .catch((err) => setError(err.message));
  }, [movieId]);

  // Create session when movie loads
  useEffect(() => {
    if (!movieId || movieLoading) return;
    startSession();
  }, [movieId, movieLoading, startSession]);

  // Poll backend every 2 s
  useEffect(() => {
    const terminal = ["verified", "denied", "recapture"];
    if (!sessionId || terminal.includes(verificationStatus)) return;

    const interval = setInterval(() => {
      getVerificationSession(sessionId)
        .then((data) => {
          const s = data.verificationStatus;
          if (terminal.includes(s)) {
            setVerificationStatus(s);
            setPredictedAge(data.predictedAge);
            setReason(data.reason);
            if (s === "verified") {
              saveVerifiedAccess(movieId, sessionId);
            }
          }
        })
        .catch(() => {});
    }, 2000);

    return () => clearInterval(interval);
  }, [sessionId, verificationStatus, movieId]);

  const handleNewAttempt = () => {
    setVerificationStatus("pending");
    setPredictedAge(null);
    setReason(null);
    setSessionId(null);
    setMobileUrl(null);
    startSession();
  };

  if (movieLoading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center">
        <div className="text-white/40 animate-pulse text-lg">Loading…</div>
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
                <img src={movie.poster} alt={movie.title} className="w-full aspect-[2/3] object-cover" onError={() => setImgError(true)} />
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

          {/* Verification panel */}
          <div className="bg-[#141418] border border-[#2A2A35] rounded-2xl p-8 flex flex-col items-center text-center">
            {error && (
            <div className="w-full bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-4 text-center">
              <p className="text-red-400 text-sm mb-2">{error}</p>
              <p className="text-white/40 text-xs">Make sure the backend is running on port 5000</p>
              <button
                onClick={startSession}
                className="mt-3 text-xs text-white/60 underline hover:text-white"
              >
                Retry
              </button>
            </div>
          )}

            {/* ---- ALLOWED ---- */}
            {verificationStatus === "verified" && (
              <div className="py-8">
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-white text-xl font-semibold mb-2">Access Granted</h2>
                {predictedAge != null && (
                  <p className="text-white/60 text-sm mb-2">
                    Estimated age: {predictedAge} years · Required: {movie.required_age}+
                  </p>
                )}
                <p className="text-green-400/70 text-xs mb-6">{reason}</p>
                <button onClick={() => navigate(`/watch/${movieId}`)} className="btn-primary text-base px-8 py-3">
                  Watch Now
                </button>
              </div>
            )}

            {/* ---- RESTRICTED ---- */}
            {verificationStatus === "denied" && (
              <div className="py-8">
                <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-red-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2z" />
                  </svg>
                </div>
                <h2 className="text-white text-xl font-semibold mb-2">Access Denied</h2>
                {predictedAge != null && (
                  <p className="text-white/60 text-sm mb-2">
                    Estimated age: {predictedAge} years · Required: {movie.required_age}+
                  </p>
                )}
                <p className="text-red-400/70 text-xs mb-6">{reason}</p>
                <button onClick={() => navigate("/")} className="btn-secondary text-base px-6 py-3">
                  Back to Home
                </button>
              </div>
            )}

            {/* ---- RECAPTURE ---- */}
            {verificationStatus === "recapture" && (
              <div className="py-8">
                <div className="w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </div>
                <h2 className="text-white text-xl font-semibold mb-2">Please Recapture</h2>
                <p className="text-white/60 text-sm mb-6 max-w-xs leading-relaxed">{reason}</p>
                <button onClick={handleNewAttempt} className="btn-primary text-base px-8 py-3">
                  Try Again
                </button>
              </div>
            )}

            {/* ---- PENDING / WAITING ---- */}
            {verificationStatus === "pending" && (
              <>
                <h2 className="text-white text-lg font-semibold mb-2">Scan to Verify</h2>
                <p className="text-white/50 text-sm mb-4">
                  Open your phone camera and scan the QR code. Make sure your phone is on the same Wi‑Fi.
                </p>
                <p className="text-amber-400/80 text-xs mb-4 max-w-xs">
                  First time: accept the HTTPS warning on your phone, then allow camera access.
                </p>

                {mobileUrl ? (
                  <>
                    <div className="bg-white p-4 rounded-xl mb-4">
                      <QRCodeSVG value={mobileUrl} size={200} level="M" />
                    </div>
                    <p className="text-white/50 text-xs break-all max-w-xs mb-2">{mobileUrl}</p>
                  </>
                ) : (
                  <div className="w-[232px] h-[232px] bg-white/5 rounded-xl animate-pulse mb-4" />
                )}

                {sessionId && (
                  <p className="text-white/20 text-xs break-all max-w-xs">Session: {sessionId}</p>
                )}
                <p className="text-white/40 text-xs mt-4 animate-pulse">Waiting for mobile verification…</p>
              </>
            )}

            {/* ---- PROCESSING ---- */}
            {verificationStatus === "processing" && (
              <div className="py-8 flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-2 border-[#E50914] border-t-transparent rounded-full animate-spin" />
                <p className="text-white/60 text-sm">Running AI verification…</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
