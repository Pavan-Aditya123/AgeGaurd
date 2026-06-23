import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-[#0A0A0F]/95 backdrop-blur-md shadow-lg shadow-black/50" : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 group"
          >
            <div className="w-8 h-8 bg-[#E50914] rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
              </svg>
            </div>
            <span className="font-display text-2xl text-white tracking-wider">
              AGE<span className="text-[#E50914]">GUARD</span>
            </span>
          </button>

          {/* Nav Links */}
          <div className="hidden md:flex items-center gap-6">
            <button onClick={() => navigate("/")} className="text-sm text-white/70 hover:text-white transition-colors">
              Home
            </button>
            <button className="text-sm text-white/70 hover:text-white transition-colors">
              Movies
            </button>
            <button className="text-sm text-white/70 hover:text-white transition-colors">
              Series
            </button>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-[#141418] border border-[#2A2A35] rounded-full px-3 py-1.5">
              <svg className="w-4 h-4 text-[#E50914]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
              </svg>
              <span className="text-xs text-white/60 font-medium">AI Protected</span>
            </div>
            <div className="w-8 h-8 rounded-full bg-[#E50914] flex items-center justify-center text-white text-sm font-bold">
              U
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
