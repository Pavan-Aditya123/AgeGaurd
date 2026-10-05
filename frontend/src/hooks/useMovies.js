/**
 * hooks/useMovies.js
 *
 * Custom React hook that fetches the full movie list from the backend.
 * Encapsulates loading / error state so pages stay clean.
 *
 * Usage:
 *   const { movies, loading, error } = useMovies();
 */

import { useState, useEffect } from "react";
import { fetchAllMovies } from "../services/movieService";
import MOVIES from "../data/movies";

export default function useMovies() {
  const [movies, setMovies]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    fetchAllMovies()
      .then((data) => {
        setMovies(data);
        setLoading(false);
      })
      .catch((err) => {
        console.warn("Backend unavailable, using static fallback:", err.message);
        setMovies(MOVIES);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { movies, loading, error };
}
