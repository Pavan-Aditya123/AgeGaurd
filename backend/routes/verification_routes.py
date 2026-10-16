"""
routes/verification_routes.py

Verification API endpoints for QR flow and face photo upload.
All access decisions are made EXCLUSIVELY by the backend AI pipeline.
The frontend cannot bypass verification by sending a pre-crafted payload.
"""

import base64
import os
import re
import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from config import FRONTEND_BASE_URL
from services.movie_service import get_movie_by_id
from services.session_service import (
    create_session,
    get_session,
    is_access_granted,
    mark_uploaded,
    mark_verified,
)

logger = logging.getLogger(__name__)

verification_bp = Blueprint("verification", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")


def _mobile_verify_url(session_id: str) -> str:
    return f"{FRONTEND_BASE_URL.rstrip('/')}/mobile-verify/{session_id}"


def _session_response(session: dict) -> dict:
    movie = get_movie_by_id(session["movieId"])
    return {
        "sessionId":          session["sessionId"],
        "movieId":            session["movieId"],
        "uploadStatus":       session["uploadStatus"],
        "verificationStatus": session["verificationStatus"],
        "imagePath":          session["imagePath"],
        "predictedAge":       session["predictedAge"],
        "requiredAge":        session.get("requiredAge") or (movie["required_age"] if movie else None),
        "verified":           session["verified"],
        "decision":           session.get("decision"),
        "reason":             session.get("reason"),
        "pad":                session.get("pad"),
        "manipulation":       session.get("manipulation"),
        "movieTitle":         movie["title"] if movie else None,
    }


# ---------------------------------------------------------------------------
# POST /api/verification/session — create QR session
# ---------------------------------------------------------------------------
@verification_bp.route("/verification/session", methods=["POST"])
def create_verification_session():
    data     = request.get_json(silent=True) or {}
    movie_id = data.get("movieId")

    if movie_id is None:
        return jsonify({"error": "movieId is required"}), 400
    try:
        movie_id = int(movie_id)
    except (TypeError, ValueError):
        return jsonify({"error": "movieId must be an integer"}), 400

    movie = get_movie_by_id(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    if not movie.get("restricted"):
        return jsonify({"error": "This movie does not require verification"}), 400

    session = create_session(movie_id)
    return jsonify({
        "success":        True,
        "sessionId":      session["sessionId"],
        "movieId":        session["movieId"],
        "mobileVerifyUrl": _mobile_verify_url(session["sessionId"]),
    })


# ---------------------------------------------------------------------------
# GET /api/verification/session/<sessionId> — poll status
# ---------------------------------------------------------------------------
@verification_bp.route("/verification/session/<session_id>", methods=["GET"])
def get_verification_session(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found or expired"}), 404
    return jsonify(_session_response(session))


# ---------------------------------------------------------------------------
# GET /api/verification/access — playback access check
# ---------------------------------------------------------------------------
@verification_bp.route("/verification/access", methods=["GET"])
def check_verification_access():
    movie_id   = request.args.get("movieId")
    session_id = request.args.get("sessionId")

    if not movie_id or not session_id:
        return jsonify({"error": "movieId and sessionId are required"}), 400
    try:
        movie_id = int(movie_id)
    except (TypeError, ValueError):
        return jsonify({"error": "movieId must be an integer"}), 400

    movie = get_movie_by_id(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    if not movie.get("restricted"):
        return jsonify({"allowed": True, "reason": "unrestricted"})

    allowed = is_access_granted(session_id, movie_id)
    return jsonify({
        "allowed": allowed,
        "reason":  "verified" if allowed else "verification_required",
    })


# ---------------------------------------------------------------------------
# POST /api/upload-face — receive face image, run full AI pipeline
# ---------------------------------------------------------------------------
@verification_bp.route("/upload-face", methods=["POST"])
def upload_face():
    """
    Receives a base64 JPEG face image and runs the complete AgeGuard pipeline:
      Face Detection → Quality → PAD → Manipulation → Authenticity → Age → Decision

    The backend makes the ONLY authoritative access decision.
    """
    data       = request.get_json(silent=True) or {}
    session_id = data.get("sessionId")
    image_data = data.get("image")

    if not session_id or not image_data:
        return jsonify({"error": "sessionId and image are required"}), 400

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid or expired session"}), 404

    # Decode base64 image
    if isinstance(image_data, str) and "," in image_data:
        image_data = re.sub(r"^data:image/\w+;base64,", "", image_data)
    try:
        image_bytes = base64.b64decode(image_data)
    except Exception:
        return jsonify({"error": "Invalid base64 image data"}), 400

    # Save raw upload
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename  = f"{session_id}_{timestamp}.jpg"
    filepath  = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    mark_uploaded(session_id, filepath)

    # Fetch required age for this session's movie
    movie        = get_movie_by_id(session["movieId"])
    required_age = movie.get("required_age", 0) if movie else 0

    # ------------------------------------------------------------------ #
    # RUN THE FULL AI PIPELINE
    # ------------------------------------------------------------------ #
    try:
        from ai.verification_pipeline import run_verification
        pipeline_result = run_verification(image_bytes, required_age)
    except Exception as e:
        logger.exception("[PIPELINE] Unexpected error: %s", e)
        return jsonify({"error": f"Verification pipeline error: {str(e)}"}), 500

    decision     = pipeline_result["decision"]
    is_allowed   = decision == "ALLOW"
    predicted_age = pipeline_result.get("predicted_age")  # None if age not reached

    # Save also face crop for debugging
    try:
        from services.face_detection_service import detect_and_crop_face
        face_img = detect_and_crop_face(filepath)
        if face_img:
            face_path = os.path.join(UPLOAD_FOLDER, f"{session_id}_{timestamp}_face.jpg")
            face_img.save(face_path)
    except Exception:
        pass  # Non-critical — don't fail the request

    # Persist result on session
    mark_verified(
        session_id,
        predicted_age=predicted_age,
        required_age=required_age,
        verified=is_allowed,
        decision=decision,
        reason=pipeline_result.get("reason"),
        pad=pipeline_result.get("pad"),
        manipulation=pipeline_result.get("manipulation"),
    )

    # Return clean response (no internal model details exposed)
    response = {
        "success":            True,
        "decision":           decision,
        "verificationStatus": "verified" if is_allowed else (
            "denied" if decision == "RESTRICT" else "recapture"
        ),
        "verified":           is_allowed,
        "reason":             pipeline_result.get("reason"),
        "requiredAge":        required_age,
    }
    if predicted_age is not None:
        response["predictedAge"] = predicted_age

    return jsonify(response)
