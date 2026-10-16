/**
 * pages/MobileVerificationPage.jsx
 *
 * Mobile camera capture page — opened via QR scan.
 * Shows pipeline stage messages during verification.
 * Handles ALLOW / RESTRICT / RECAPTURE decisions from backend.
 */

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { getVerificationSession, uploadFaceImage } from "../services/verificationService";

const STAGE_MESSAGES = [
  "Detecting face…",
  "Checking image quality…",
  "Checking liveness…",
  "Checking image authenticity…",
  "Estimating age…",
  "Making decision…",
];

export default function MobileVerificationPage() {
  const { sessionId } = useParams();
  const videoRef  = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [sessionInfo, setSessionInfo]   = useState(null);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState(null);
  const [cameraReady, setCameraReady]   = useState(false);
  const [uploading, setUploading]       = useState(false);
  const [stageIdx, setStageIdx]         = useState(0);
  const [result, setResult]             = useState(null);

  // Cycle through stage messages while uploading
  useEffect(() => {
    if (!uploading) return;
    const id = setInterval(() => {
      setStageIdx((i) => (i + 1 < STAGE_MESSAGES.length ? i + 1 : i));
    }, 900);
    return () => clearInterval(id);
  }, [uploading]);

  useEffect(() => {
    getVerificationSession(sessionId)
      .then((data) => {
        setSessionInfo(data);
        const s = data.verificationStatus;
        if (s === "verified" || s === "denied" || s === "recapture") {
          setResult({
            decision:     data.decision,
            predictedAge: data.predictedAge,
            requiredAge:  data.requiredAge,
            reason:       data.reason,
            verified:     data.verified,
          });
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [sessionId]);

  const startCamera = useCallback(async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setCameraReady(true);
      }
    } catch (err) {
      const isInsecure =
        window.location.protocol === "http:" &&
        !["localhost", "127.0.0.1"].includes(window.location.hostname);
      if (isInsecure) {
        setError(
          "Camera blocked: mobile browsers require HTTPS. Run npm run start:https on your laptop, scan the QR again, and accept the security warning once."
        );
      } else if (err.name === "NotAllowedError") {
        setError("Camera permission denied. Allow camera access in browser settings and tap Retry.");
      } else {
        setError("Could not open camera. Allow camera permission and tap Retry.");
      }
    }
  }, []);

  useEffect(() => {
    if (loading || error || result) return;
    let cancelled = false;
    async function init() {
      if (!cancelled) await startCamera();
    }
    init();
    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, [loading, error, result, startCamera]);

  const handleCapture = async () => {
    const video  = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !cameraReady) return;

    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    const jpegDataUrl = canvas.toDataURL("image/jpeg", 0.92);

    setUploading(true);
    setStageIdx(0);
    setError(null);

    try {
      const res = await uploadFaceImage(sessionId, jpegDataUrl);
      streamRef.current?.getTracks().forEach((t) => t.stop());
      setResult({
        decision:     res.decision,
        predictedAge: res.predictedAge,
        requiredAge:  res.requiredAge,
        reason:       res.reason,
        verified:     res.verified,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleRetry = () => {
    setResult(null);
    setError(null);
    setCameraReady(false);
    setStageIdx(0);
  };

  // ---- Loading ----
  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center p-6">
        <p className="text-white/40 animate-pulse">Loading session…</p>
      </div>
    );
  }

  // ---- Camera error (no result yet) ----
  if (error && !result) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex flex-col items-center justify-center p-6 text-center gap-4">
        <div className="w-14 h-14 bg-red-500/20 rounded-full flex items-center justify-center">
          <svg className="w-7 h-7 text-red-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-2.694-.833-3.464 0L3.34 16.5C2.57 18.333 3.532 20 5.072 20z" />
          </svg>
        </div>
        <p className="text-red-400 text-sm max-w-xs">{error}</p>
        <button onClick={() => window.location.reload()} className="btn-secondary">
          Retry
        </button>
      </div>
    );
  }

  // ---- Final result ----
  if (result) {
    const { decision, predictedAge, requiredAge, reason } = result;
    const isAllow    = decision === "ALLOW";
    const isRestrict = decision === "RESTRICT";
    const isRecapture = decision === "RECAPTURE" || (!isAllow && !isRestrict);

    const icon = isAllow ? (
      <svg className="w-10 h-10 text-green-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    ) : isRestrict ? (
      <svg className="w-10 h-10 text-red-400" fill="currentColor" viewBox="0 0 24 24">
        <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2z" />
      </svg>
    ) : (
      <svg className="w-10 h-10 text-yellow-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    );

    const bgColor = isAllow ? "bg-green-500/20" : isRestrict ? "bg-red-500/20" : "bg-yellow-500/20";
    const title   = isAllow ? "Verification Successful" : isRestrict ? "Access Denied" : "Please Recapture";

    return (
      <div className="min-h-screen bg-[#0A0A0F] flex flex-col items-center justify-center p-6 text-center">
        <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 ${bgColor}`}>
          {icon}
        </div>
        <h1 className="text-white text-2xl font-semibold mb-3">{title}</h1>
        <p className="text-white/60 text-sm max-w-xs leading-relaxed mb-2">{reason}</p>

        {predictedAge != null && (
          <p className="text-white/40 text-xs mt-1">
            Estimated age: {predictedAge} years
            {requiredAge != null && requiredAge > 0 && ` · Required: ${requiredAge}+`}
          </p>
        )}

        {isAllow && (
          <p className="text-white/50 text-sm mt-6 max-w-sm">
            Return to your desktop — playback will unlock automatically.
          </p>
        )}

        {isRecapture && (
          <button onClick={handleRetry} className="btn-primary mt-6 px-8 py-3">
            Try Again
          </button>
        )}

        {sessionInfo?.movieTitle && (
          <p className="text-white/30 text-xs mt-6">{sessionInfo.movieTitle}</p>
        )}
      </div>
    );
  }

  // ---- Camera view ----
  return (
    <div className="min-h-screen bg-[#0A0A0F] flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 text-center border-b border-[#2A2A35]">
        <p className="text-[#E50914] text-xs font-bold uppercase tracking-widest mb-1">AgeGuard</p>
        <h1 className="text-white text-lg font-semibold">Identity Verification</h1>
        {sessionInfo?.movieTitle && (
          <p className="text-white/50 text-sm mt-1">{sessionInfo.movieTitle}</p>
        )}
      </div>

      <div className="flex-1 flex flex-col items-center justify-center p-4 gap-5">
        {/* Camera preview */}
        <div className="relative w-full max-w-sm aspect-[3/4] bg-black rounded-2xl overflow-hidden border border-[#2A2A35]">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{ transform: "scaleX(-1)" }}
          />

          {/* Face guide overlay */}
          {cameraReady && !uploading && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-48 h-60 border-2 border-white/30 rounded-full" />
            </div>
          )}

          {!cameraReady && !uploading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/60">
              <p className="text-white/50 text-sm animate-pulse">Starting camera…</p>
            </div>
          )}

          {/* Pipeline stage overlay */}
          {uploading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/75 gap-4">
              <div className="w-10 h-10 border-2 border-[#E50914] border-t-transparent rounded-full animate-spin" />
              <p className="text-white text-sm font-medium px-4 text-center">
                {STAGE_MESSAGES[stageIdx]}
              </p>
            </div>
          )}
        </div>

        {!uploading && (
          <p className="text-white/50 text-sm text-center max-w-xs">
            Position your face inside the oval, look directly at the camera, then tap Capture.
          </p>
        )}

        {error && (
          <p className="text-red-400 text-sm text-center max-w-xs">{error}</p>
        )}

        <button
          onClick={handleCapture}
          disabled={!cameraReady || uploading}
          className="btn-primary text-base px-10 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? "Verifying…" : "Capture"}
        </button>
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
