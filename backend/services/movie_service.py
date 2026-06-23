"""
services/movie_service.py

Business logic layer for movies.
Routes call these functions — they never touch raw data directly.

Future phases add services here:
  Phase 2: qr_service.py        → QR code generation & session management
  Phase 4: liveness_service.py  → Blink / head-movement detection
  Phase 5: age_service.py       → ResNet18 age estimation
  Phase 6: access_service.py    → Allow / deny decision engine
"""

# ---------------------------------------------------------------------------
# In-memory data store (Phase 1).
# Phase 2+ will move this to a database or config file.
# ---------------------------------------------------------------------------
MOVIES = [
    {
        "id": 1,
        "title": "Chhichhore",
        "description": (
            "A group of middle-aged men try to relive their college days after their son meets with "
            "a tragic accident. A heartwarming story about friendship, failure, and the spirit to never give up."
        ),
        "rating": "U",
        "required_age": 0,
        "restricted": False,
        "category": "Drama / Comedy",
        "poster": "https://cdn.cinematerial.com/p/297x/pzp2uua4/chhichhore-indian-movie-poster-md.jpg?v=1568837614",
        "video": "/videos/sample.mp4",
        "year": 2019,
        "duration": "2h 21m",
    },
    {
        "id": 2,
        "title": "Interstellar",
        "description": (
            "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival. "
            "A visually stunning and emotionally resonant sci-fi epic about love, time, and sacrifice."
        ),
        "rating": "U/A 13+",
        "required_age": 13,
        "restricted": False,
        "category": "Sci-Fi / Adventure",
        "poster": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg",
        "video": "/videos/sample.mp4",
        "year": 2014,
        "duration": "2h 49m",
    },
    {
        "id": 3,
        "title": "Dhurandhar",
        "description": (
            "A gripping crime thriller that dives deep into the world of power, betrayal, and survival. "
            "A bold cinematic experience that pushes boundaries of storytelling."
        ),
        "rating": "A (18+)",
        "required_age": 18,
        "restricted": True,
        "category": "Crime / Thriller",
        "poster": "https://image.tmdb.org/t/p/w500/snBOuXDdhmTvlzMUvP9Em3Pp1u1.jpg",
        "video": "/videos/sample.mp4",
        "year": 2024,
        "duration": "2h 15m",
    },
    {
        "id": 4,
        "title": "Animal",
        "description": (
            "A vengeful son sets out on a rampage after his beloved father is shot by unknown assassins. "
            "A raw, intense tale of love, violence, and primal instinct."
        ),
        "rating": "A (18+)",
        "required_age": 18,
        "restricted": True,
        "category": "Action / Drama",
        "poster": "https://upload.wikimedia.org/wikipedia/en/9/90/Animal_%282023_film%29_poster.jpg",
        "video": "/videos/sample.mp4",
        "year": 2023,
        "duration": "3h 21m",
    },
    {
        "id": 5,
        "title": "John Wick 4",
        "description": (
            "John Wick uncovers a path to defeating the High Table. But before he can earn his freedom, "
            "Wick must face off against a new enemy with powerful alliances across the globe."
        ),
        "rating": "A (18+)",
        "required_age": 18,
        "restricted": True,
        "category": "Action / Thriller",
        "poster": "https://cdn.moviestillsdb.com/storage/posters/03/10366206_100.jpg",
        "video": "/videos/sample.mp4",
        "year": 2023,
        "duration": "2h 49m",
    },
    {
        "id": 6,
        "title": "Kung Fu Panda",
        "description": (
            "Po the panda is chosen as the Dragon Warrior to protect the Valley of Peace from a villainous "
            "snow leopard. A fun-filled animated adventure packed with humor and heart."
        ),
        "rating": "U",
        "required_age": 0,
        "restricted": False,
        "category": "Animation / Comedy",
        "poster": "/Posters/kung-fu-panda.webp",
        "video": "/videos/sample.mp4",
        "year": 2008,
        "duration": "1h 32m",
    },
]


def get_all_movies():
    """Return the full movie catalogue."""
    return MOVIES


def get_movie_by_id(movie_id: int):
    """Return a single movie dict, or None if not found."""
    return next((m for m in MOVIES if m["id"] == movie_id), None)
