"""
routes/verification_routes.py

Verification API endpoints for QR flow and face photo upload (Phase 3).
"""

import base64
import os
import re
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from services.movie_service import get_movie_by_id
from services.session_service import create_session, get_session, mark_uploaded

verification_bp = Blueprint("verification", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000")


def _mobile_verify_url(session_id: str) -> str:
    return f"{FRONTEND_BASE_URL}/mobile-verify/{session_id}"


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
    """GET /api/verification/session/<sessionId> — session status lookup."""
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    movie = get_movie_by_id(session["movieId"])
    return jsonify({
        "sessionId": session["sessionId"],
        "movieId": session["movieId"],
        "uploadStatus": session["uploadStatus"],
        "imagePath": session["imagePath"],
        "movieTitle": movie["title"] if movie else None,
        "requiredAge": movie["required_age"] if movie else None,
    })


@verification_bp.route("/upload-face", methods=["POST"])
def upload_face():
    """
    POST /api/upload-face
    Body: { "sessionId": "...", "image": "<base64 JPEG data URL or raw base64>" }
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("sessionId")
    image_data = data.get("image")

    if not session_id or not image_data:
        return jsonify({"error": "sessionId and image are required"}), 400

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 404

    # Strip data URL prefix if present (e.g. "data:image/jpeg;base64,...")
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

    return jsonify({
        "success": True,
        "imagePath": filepath,
    })
