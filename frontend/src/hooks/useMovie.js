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

export default function useMovie(id) {
  const [movie, setMovie]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetchMovieById(id)
      .then((data) => {
        setMovie(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  return { movie, loading, error };
}
