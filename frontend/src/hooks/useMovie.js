/**
 * hooks/useMovie.js
 *
 * Custom React hook that fetches a single movie by ID.
 * Used by MovieDetailPage and VideoPlayerPage.
 *
 * Usage:
 *   const { movie, loading, error } = useMovie(id);
 */

import { useState, useEffect } from "react";
import { fetchMovieById } from "../services/movieService";
import MOVIES from "../data/movies";

export default function useMovie(id) {
  const [movie, setMovie]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetchMovieById(id)
      .then((data) => {
        console.log("Movie loaded from backend:", data);
        console.log("Video Path:", data?.video);
        setMovie(data);
        setLoading(false);
      })
      .catch((err) => {
        console.warn("Backend unavailable, using static fallback:", err.message);
        // Fall back to static data so the player always has a movie object
        const fallback = MOVIES.find((m) => String(m.id) === String(id)) || null;
        console.log("Fallback movie:", fallback);
        console.log("Video Path:", fallback?.video);
        setMovie(fallback);
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  return { movie, loading, error };
}
