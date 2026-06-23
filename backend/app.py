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
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# ---------------------------------------------------------------------------
# Register blueprints
# ---------------------------------------------------------------------------
app.register_blueprint(movie_bp, url_prefix="/movies")

# Phase 2+: register additional blueprints here
# from routes.verification_routes import verification_bp
# app.register_blueprint(verification_bp, url_prefix="/verify")


# ---------------------------------------------------------------------------
# Health check (no blueprint needed — root-level utility route)
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "AgeGuard backend is running"})


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
    app.run(debug=True, port=5000)
