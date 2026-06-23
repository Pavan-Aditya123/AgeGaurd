/**
 * data/movies.js
 * 
 * Static movie data used as a fallback if the backend is unreachable.
 * In production, all data comes from GET /movies (Flask API).
 * Future phases may add fields like: verificationStatus, sessionToken, qrCode.
 */

const MOVIES = [
  {
    id: 1,
    title: "Chhichhore",
    description:
      "A group of middle-aged men try to relive their college days after their son meets with a tragic accident. A heartwarming story about friendship, failure, and the spirit to never give up.",
    rating: "U",
    required_age: 0,
    restricted: false,
    category: "Drama / Comedy",
    poster:
      "https://cdn.cinematerial.com/p/297x/pzp2uua4/chhichhore-indian-movie-poster-md.jpg?v=1568837614",
    video: "/Videos/Kung Fu Panda_Trailer.mp4",
    year: 2019,
    duration: "2h 21m",
  },
  {
    id: 2,
    title: "Interstellar",
    description:
      "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival. A visually stunning and emotionally resonant sci-fi epic about love, time, and sacrifice.",
    rating: "U/A 13+",
    required_age: 13,
    restricted: false,
    category: "Sci-Fi / Adventure",
    poster:
      "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg",
    video: "/Videos/Kung Fu Panda_Trailer.mp4",
    year: 2014,
    duration: "2h 49m",
  },
  {
    id: 3,
    title: "Dhurandhar",
    description:
      "A gripping crime thriller that dives deep into the world of power, betrayal, and survival. A bold cinematic experience that pushes boundaries of storytelling.",
    rating: "A (18+)",
    required_age: 18,
    restricted: true,
    category: "Crime / Thriller",
    poster:
      "https://image.tmdb.org/t/p/w500/snBOuXDdhmTvlzMUvP9Em3Pp1u1.jpg",
    video: "/Videos/Kung Fu Panda_Trailer.mp4",
    year: 2024,
    duration: "2h 15m",
  },
  {
    id: 4,
    title: "Animal",
    description:
      "A vengeful son sets out on a rampage after his beloved father is shot by unknown assassins. A raw, intense tale of love, violence, and primal instinct.",
    rating: "A (18+)",
    required_age: 18,
    restricted: true,
    category: "Action / Drama",
    poster:
      "https://upload.wikimedia.org/wikipedia/en/9/90/Animal_%282023_film%29_poster.jpg",
    video: "/Videos/Kung Fu Panda_Trailer.mp4",
    year: 2023,
    duration: "3h 21m",
  },
  {
    id: 5,
    title: "John Wick 4",
    description:
      "John Wick uncovers a path to defeating the High Table. But before he can earn his freedom, Wick must face off against a new enemy with powerful alliances across the globe.",
    rating: "A (18+)",
    required_age: 18,
    restricted: true,
    category: "Action / Thriller",
    poster:
      "https://upload.wikimedia.org/wikipedia/en/6/6e/John_Wick_Chapter_4_poster.jpg",
    video: "/Videos/Kung Fu Panda_Trailer.mp4",
    year: 2023,
    duration: "2h 49m",
  },
  {
    id: 6,
    title: "Kung Fu Panda",
    description:
      "Po the panda is chosen as the Dragon Warrior to protect the Valley of Peace from a villainous snow leopard. A fun-filled animated adventure packed with humor and heart.",
    rating: "U",
    required_age: 0,
    restricted: false,
    category: "Animation / Comedy",
    poster:
      "/Posters/kung-fu-panda.webp",
    video: "/Videos/Kung Fu Panda_Trailer.mp4",
    year: 2008,
    duration: "1h 32m",
  },
];

export default MOVIES;
