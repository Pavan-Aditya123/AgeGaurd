"""
app.py

AgeGuard Flask application entry point.
All AI models are loaded at startup to avoid cold-start delays.
"""

import os
import logging
import sys

# ---------------------------------------------------------------------------
# Load backend/.env when present
# ---------------------------------------------------------------------------
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes.movie_routes import movie_bp
from routes.verification_routes import verification_bp


# ---------------------------------------------------------------------------
# Auto-download YuNet face detector model if missing (one-time, ~232 KB)
# ---------------------------------------------------------------------------
def _ensure_yunet():
    import urllib.request
    yunet = os.path.join(os.path.dirname(__file__), "models", "face_detection_yunet.onnx")
    if not os.path.exists(yunet):
        url = ("https://github.com/opencv/opencv_zoo/raw/main/"
               "models/face_detection_yunet/face_detection_yunet_2023mar.onnx")
        logger.info("[STARTUP] Downloading YuNet face detector (~232 KB)…")
        try:
            urllib.request.urlretrieve(url, yunet)
            logger.info("[STARTUP] YuNet downloaded OK")
        except Exception as e:
            logger.error("[STARTUP] YuNet download FAILED: %s — face detection may not work", e)

_ensure_yunet()

app = Flask(__name__, static_folder="static")
CORS(app)

# ---------------------------------------------------------------------------
# Register blueprints
# ---------------------------------------------------------------------------
app.register_blueprint(movie_bp, url_prefix="/movies")
app.register_blueprint(verification_bp, url_prefix="/api")


# ---------------------------------------------------------------------------
# Pre-load all AI models once at startup
# ---------------------------------------------------------------------------
def _preload_models():
    """Load all three models into memory before the first request."""
    errors = []

    logger.info("=" * 60)
    logger.info("AgeGuard — Pre-loading AI models")
    logger.info("=" * 60)

    try:
        from ai.pad_detector import _get_session
        _get_session()
        logger.info("[STARTUP] PAD model loaded OK")
    except Exception as e:
        logger.error("[STARTUP] PAD model FAILED: %s", e)
        errors.append(f"PAD: {e}")

    try:
        from ai.age_estimator import _get_model
        _get_model()
        logger.info("[STARTUP] Age model loaded OK")
    except Exception as e:
        logger.error("[STARTUP] Age model FAILED: %s", e)
        errors.append(f"Age: {e}")

    try:
        from ai.manipulation_detector import _get_model
        _get_model()
        logger.info("[STARTUP] Manipulation model loaded OK")
    except Exception as e:
        logger.error("[STARTUP] Manipulation model FAILED: %s", e)
        errors.append(f"Manipulation: {e}")

    if errors:
        logger.warning("[STARTUP] Some models failed to load: %s", errors)
    else:
        logger.info("[STARTUP] All models loaded successfully")
    logger.info("=" * 60)
    return errors


_model_errors = _preload_models()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    from ai.config import AGE_MODEL_PATH, PAD_MODEL_PATH, MANIPULATION_MODEL_PATH
    return jsonify({
        "status": "ok",
        "message": "AgeGuard backend is running",
        "models": {
            "age":          os.path.exists(AGE_MODEL_PATH),
            "pad":          os.path.exists(PAD_MODEL_PATH),
            "manipulation": os.path.exists(MANIPULATION_MODEL_PATH),
        },
        "model_errors": _model_errors,
    })


@app.route("/Posters/<path:filename>")
def serve_poster(filename):
    return send_from_directory(os.path.join(app.static_folder, "Posters"), filename)


@app.route("/Videos/<path:filename>")
def serve_video(filename):
    videos_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "Videos")
    return send_from_directory(videos_dir, filename)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("[STARTUP] Running Flask HTTP on 0.0.0.0:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)