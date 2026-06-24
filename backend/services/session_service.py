"""
services/session_service.py

In-memory session store for QR verification flow.
Stores upload status and age verification results until session expires.
"""

import uuid
from datetime import datetime, timedelta, timezone

from config import SESSION_TTL_MINUTES

# sessionId -> session dict
_sessions: dict[str, dict] = {}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _is_expired(session: dict) -> bool:
    created = datetime.fromisoformat(session["createdAt"])
    return _utcnow() > created + timedelta(minutes=SESSION_TTL_MINUTES)


def create_session(movie_id: int) -> dict:
    """Create a new verification session for a restricted movie."""
    session_id = str(uuid.uuid4())
    now = _utcnow().isoformat()
    session = {
        "sessionId": session_id,
        "movieId": movie_id,
        "uploadStatus": "pending",
        "verificationStatus": "pending",
        "imagePath": None,
        "predictedAge": None,
        "requiredAge": None,
        "verified": None,
        "createdAt": now,
        "verifiedAt": None,
    }
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> dict | None:
    """Return session dict or None if not found or expired."""
    session = _sessions.get(session_id)
    if not session:
        return None
    if _is_expired(session):
        del _sessions[session_id]
        return None
    return session


def mark_uploaded(session_id: str, image_path: str) -> dict | None:
    """Update session after a face photo is uploaded."""
    session = get_session(session_id)
    if not session:
        return None
    session["uploadStatus"] = "uploaded"
    session["imagePath"] = image_path
    session["verificationStatus"] = "processing"
    return session


def mark_verified(
    session_id: str,
    *,
    predicted_age: float,
    required_age: int | None,
    verified: bool,
) -> dict | None:
    """Store age prediction and verification decision on the session."""
    session = get_session(session_id)
    if not session:
        return None
    session["predictedAge"] = round(predicted_age, 2)
    session["requiredAge"] = required_age
    session["verified"] = verified
    session["verificationStatus"] = "verified" if verified else "denied"
    session["verifiedAt"] = _utcnow().isoformat()
    return session


def is_access_granted(session_id: str, movie_id: int) -> bool:
    """Return True if session exists, matches movie, and verification passed."""
    session = get_session(session_id)
    if not session:
        return False
    if session["movieId"] != movie_id:
        return False
    return session.get("verified") is True
