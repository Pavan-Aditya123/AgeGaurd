"""
routes/verification_routes.py

Verification API endpoints for QR flow and face photo upload.
"""

import base64
import os
import re
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
from services.age_estimation_service import predict_age

verification_bp = Blueprint("verification", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")


def _mobile_verify_url(session_id: str) -> str:
    return f"{FRONTEND_BASE_URL.rstrip('/')}/mobile-verify/{session_id}"


def _session_response(session: dict) -> dict:
    movie = get_movie_by_id(session["movieId"])
    return {
        "sessionId": session["sessionId"],
        "movieId": session["movieId"],
        "uploadStatus": session["uploadStatus"],
        "verificationStatus": session["verificationStatus"],
        "imagePath": session["imagePath"],
        "predictedAge": session["predictedAge"],
        "requiredAge": session.get("requiredAge") or (movie["required_age"] if movie else None),
        "verified": session["verified"],
        "movieTitle": movie["title"] if movie else None,
    }


@verification_bp.route("/verification/session", methods=["POST"])
def create_verification_session():
    """
    POST /api/verification/session
    Body: { "movieId": 3 }
    Creates a session and returns sessionId + mobile QR URL.
    """
    data = request.get_json(silent=True) or {}
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
        "success": True,
        "sessionId": session["sessionId"],
        "movieId": session["movieId"],
        "mobileVerifyUrl": _mobile_verify_url(session["sessionId"]),
    })


@verification_bp.route("/verification/session/<session_id>", methods=["GET"])
def get_verification_session(session_id):
    """GET /api/verification/session/<sessionId> — session status and verification result."""
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found or expired"}), 404

    return jsonify(_session_response(session))


@verification_bp.route("/verification/access", methods=["GET"])
def check_verification_access():
    """
    GET /api/verification/access?movieId=3&sessionId=...
    Validates that a verified session grants playback for the given movie.
    """
    movie_id = request.args.get("movieId")
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
        "reason": "verified" if allowed else "verification_required",
    })


@verification_bp.route("/upload-face", methods=["POST"])
def upload_face():
    """
    POST /api/upload-face
    Body: { "sessionId": "...", "image": "<base64 JPEG data URL or raw base64>" }
    Returns predicted age and verification result.
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("sessionId")
    image_data = data.get("image")

    if not session_id or not image_data:
        return jsonify({"error": "sessionId and image are required"}), 400

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid or expired session"}), 404

    if isinstance(image_data, str) and "," in image_data:
        image_data = re.sub(r"^data:image/\w+;base64,", "", image_data)

    try:
        image_bytes = base64.b64decode(image_data)
    except Exception:
        return jsonify({"error": "Invalid base64 image data"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{session_id}_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    mark_uploaded(session_id, filepath)

    # Also save cropped face for debugging
    from services.face_detection_service import detect_and_crop_face
    face_image = detect_and_crop_face(filepath)
    if face_image:
        face_filename = f"{session_id}_{timestamp}_face.jpg"
        face_filepath = os.path.join(UPLOAD_FOLDER, face_filename)
        face_image.save(face_filepath)

    try:
        predicted_age = predict_age(filepath)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Age prediction failed: {str(e)}"}), 500

    movie = get_movie_by_id(session["movieId"])
    required_age = movie.get("required_age") if movie else None
    is_verified = required_age is not None and predicted_age >= required_age

    mark_verified(
        session_id,
        predicted_age=predicted_age,
        required_age=required_age,
        verified=is_verified,
    )

    return jsonify({
        "success": True,
        "imagePath": filepath,
        "predictedAge": round(predicted_age, 2),
        "requiredAge": required_age,
        "verified": is_verified,
        "verificationStatus": "verified" if is_verified else "denied",
    })
