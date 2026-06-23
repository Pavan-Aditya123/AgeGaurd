"""
routes/movie_routes.py

Flask Blueprint for all movie-related API endpoints.
Registered in app.py under the /movies prefix.

Future phases add blueprints here:
  Phase 2: verification_routes.py  → /verify, /qr, /session
  Phase 5: age_routes.py           → /predict-age
"""

from flask import Blueprint, jsonify
from services.movie_service import get_all_movies, get_movie_by_id

movie_bp = Blueprint("movies", __name__)


@movie_bp.route("/", methods=["GET"])
def list_movies():
    """GET /movies — return all movies."""
    return jsonify(get_all_movies())


@movie_bp.route("/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    """GET /movies/<id> — return a single movie."""
    movie = get_movie_by_id(movie_id)
    if movie:
        return jsonify(movie)
    return jsonify({"error": "Movie not found"}), 404
