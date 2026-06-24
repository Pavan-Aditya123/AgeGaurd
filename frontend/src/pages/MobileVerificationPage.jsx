/**
 * pages/MobileVerificationPage.jsx
 *
 * Mobile camera capture page — opened via QR scan.
 * Route: /mobile-verify/:sessionId
 */

import React, { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getVerificationSession, uploadFaceImage } from "../services/verificationService";

export default function MobileVerificationPage() {
  const { sessionId } = useParams();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [sessionInfo, setSessionInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    getVerificationSession(sessionId)
      .then((data) => {
        setSessionInfo(data);
        if (data.verificationStatus === "verified" || data.verificationStatus === "denied") {
          setResult({
            verified: data.verified,
            predictedAge: data.predictedAge,
            requiredAge: data.requiredAge,
          });
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [sessionId]);

  useEffect(() => {
    if (loading || error || result) return;

    let cancelled = false;

    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false,
        });

        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }

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
            "Camera blocked: mobile browsers require HTTPS. Run npm run update-network, then npm run start:https, open the HTTPS URL on your phone, accept the security warning once, then scan the QR again."
          );
        } else if (err.name === "NotAllowedError") {
          setError("Camera permission denied. Allow camera access in your browser settings and tap Retry.");
        } else {
          setError("Could not open camera. Allow camera permission and tap Retry.");
        }
      }
    }

    startCamera();

    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, [loading, error, result]);

  const handleCapture = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !cameraReady) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const jpegDataUrl = canvas.toDataURL("image/jpeg", 0.9);

    setUploading(true);
    setError(null);

    try {
      const uploadResult = await uploadFaceImage(sessionId, jpegDataUrl);
      streamRef.current?.getTracks().forEach((t) => t.stop());
      setResult({
        verified: uploadResult.verified,
        predictedAge: uploadResult.predictedAge,
        requiredAge: uploadResult.requiredAge,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center p-6">
        <p className="text-white/40 animate-pulse">Loading session…</p>
      </div>
    );
  }

  if (error && !result) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] flex flex-col items-center justify-center p-6 text-center gap-4">
        <p className="text-red-400">{error}</p>
        <button onClick={() => window.location.reload()} className="btn-secondary">
          Retry
        </button>
      </div>
    );
  }

  if (result) {
    const granted = result.verified === true;

    return (
      <div className="min-h-screen bg-[#0A0A0F] flex flex-col items-center justify-center p-6 text-center">
        <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 ${granted ? "bg-green-500/20" : "bg-red-500/20"}`}>
          {granted ? (
            <svg className="w-10 h-10 text-green-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-10 h-10 text-red-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </div>
        <h1 className="text-white text-2xl font-semibold mb-3">
          {granted ? "Verification Successful" : "Verification Failed"}
        </h1>
        <p className="text-white/60 max-w-sm">
          Estimated age: {result.predictedAge} years.
          {result.requiredAge != null && ` Required: ${result.requiredAge}+.`}
        </p>
        <p className="text-white/50 text-sm mt-4 max-w-sm">
          {granted
            ? "Return to your desktop — playback will unlock automatically."
            : "You do not meet the age requirement for this title."}
        </p>
        {sessionInfo?.movieTitle && (
          <p className="text-white/40 text-sm mt-6">
            {sessionInfo.movieTitle}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0A0F] flex flex-col">
      <div className="px-4 py-5 text-center border-b border-[#2A2A35]">
        <p className="text-[#E50914] text-xs font-bold uppercase tracking-widest mb-1">AgeGuard</p>
        <h1 className="text-white text-lg font-semibold">Identity Verification</h1>
        {sessionInfo?.movieTitle && (
          <p className="text-white/50 text-sm mt-1">{sessionInfo.movieTitle}</p>
        )}
      </div>

      <div className="flex-1 flex flex-col items-center justify-center p-4 gap-6">
        <div className="relative w-full max-w-sm aspect-[3/4] bg-black rounded-2xl overflow-hidden border border-[#2A2A35]">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover mirror"
            style={{ transform: "scaleX(-1)" }}
          />
          {!cameraReady && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/60">
              <p className="text-white/50 text-sm animate-pulse">Starting camera…</p>
            </div>
          )}
        </div>

        <p className="text-white/50 text-sm text-center max-w-xs">
          Position your face in the frame, then tap Capture.
        </p>

        <button
          onClick={handleCapture}
          disabled={!cameraReady || uploading}
          className="btn-primary text-base px-10 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? "Uploading…" : "Capture"}
        </button>
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
