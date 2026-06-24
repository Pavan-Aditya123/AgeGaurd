"""
app.py

AgeGuard Flask application entry point.
Kept intentionally thin — all logic lives in routes/ and services/.

Blueprint registration pattern makes it easy to add Phase 2+ routes:
    from routes.verification_routes import verification_bp
    app.register_blueprint(verification_bp, url_prefix="/verify")
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes.movie_routes import movie_bp
from routes.verification_routes import verification_bp
import os

# Load backend/.env when present (optional — falls back to config.py defaults)
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

app = Flask(__name__, static_folder='static')
CORS(app)

# ---------------------------------------------------------------------------
# Register blueprints
# ---------------------------------------------------------------------------
app.register_blueprint(movie_bp, url_prefix="/movies")
app.register_blueprint(verification_bp, url_prefix="/api")


# ---------------------------------------------------------------------------
# Health check (no blueprint needed — root-level utility route)
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    model_path = os.path.join(os.path.dirname(__file__), "models", "age_model.pth")
    return jsonify({
        "status": "ok",
        "message": "AgeGuard backend is running",
        "modelAvailable": os.path.exists(model_path),
    })


@app.route("/Posters/<path:filename>")
def serve_poster(filename):
    """Serve poster images from static folder."""
    return send_from_directory(os.path.join(app.static_folder, 'Posters'), filename)


@app.route("/Videos/<path:filename>")
def serve_video(filename):
    """Serve trailer videos from frontend/public/Videos (CRA dev proxy fallback)."""
    videos_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "Videos")
    return send_from_directory(videos_dir, filename)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
