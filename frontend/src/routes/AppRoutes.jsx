/**
 * routes/AppRoutes.jsx
 *
 * Central routing configuration for the entire application.
 * All <Route> definitions live here — never scattered across components.
 */

import React from "react";
import { Routes, Route } from "react-router-dom";

import HomePage                 from "../pages/HomePage";
import MovieDetailPage          from "../pages/MovieDetailPage";
import VideoPlayerPage          from "../pages/VideoPlayerPage";
import VerificationPage         from "../pages/VerificationPage";
import MobileVerificationPage   from "../pages/MobileVerificationPage";
import VideoTestPage            from "../pages/VideoTestPage"; // TEMP: remove after debugging

// Route path constants — import these anywhere you need to navigate
export const ROUTES = {
  HOME:           "/",
  MOVIE_DETAIL:   "/movie/:id",
  WATCH:          "/watch/:id",
  VERIFY:         "/verify/:movieId",
  MOBILE_VERIFY:  "/mobile-verify/:sessionId",
  VIDEO_TEST:     "/video-test", // TEMP: remove after debugging
};

export default function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.HOME}           element={<HomePage />} />
      <Route path={ROUTES.MOVIE_DETAIL}   element={<MovieDetailPage />} />
      <Route path={ROUTES.WATCH}          element={<VideoPlayerPage />} />
      <Route path={ROUTES.VERIFY}         element={<VerificationPage />} />
      <Route path={ROUTES.MOBILE_VERIFY}  element={<MobileVerificationPage />} />
      <Route path={ROUTES.VIDEO_TEST}     element={<VideoTestPage />} /> {/* TEMP */}
    </Routes>
  );
}
