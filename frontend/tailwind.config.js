/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          red: "#E50914",
          dark: "#0A0A0F",
          card: "#141418",
          border: "#2A2A35",
          muted: "#8A8A9A",
          gold: "#F5C518",
        },
      },
      fontFamily: {
        display: ["'Bebas Neue'", "cursive"],
        body: ["'Inter'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
