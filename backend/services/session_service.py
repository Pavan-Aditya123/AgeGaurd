"""
services/session_service.py

In-memory session store for QR verification flow (Phase 3).
Phase 4+ may replace this with a database or Redis.
"""

import uuid
from datetime import datetime, timezone

# sessionId -> { sessionId, movieId, uploadStatus, imagePath, createdAt }
_sessions: dict[str, dict] = {}


def create_session(movie_id: int) -> dict:
    """Create a new verification session for a restricted movie."""
    session_id = str(uuid.uuid4())
    session = {
        "sessionId": session_id,
        "movieId": movie_id,
        "uploadStatus": "pending",
        "imagePath": None,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> dict | None:
    """Return session dict or None if not found."""
    return _sessions.get(session_id)


def mark_uploaded(session_id: str, image_path: str) -> dict | None:
    """Update session after a face photo is uploaded."""
    session = _sessions.get(session_id)
    if not session:
        return None
    session["uploadStatus"] = "uploaded"
    session["imagePath"] = image_path
    return session
