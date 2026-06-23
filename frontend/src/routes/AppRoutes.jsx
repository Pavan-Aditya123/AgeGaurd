/**
 * routes/AppRoutes.jsx
 *
 * Central routing configuration for the entire application.
 * All <Route> definitions live here — never scattered across components.
 *
 * Future phases add routes here:
 *   Phase 2: /verify/:sessionId   → QR verification landing
 *   Phase 3: /mobile/:sessionId   → Mobile camera page
 */

import React from "react";
import { Routes, Route } from "react-router-dom";

import HomePage         from "../pages/HomePage";
import MovieDetailPage  from "../pages/MovieDetailPage";
import VideoPlayerPage  from "../pages/VideoPlayerPage";

// Route path constants — import these anywhere you need to navigate
export const ROUTES = {
  HOME:         "/",
  MOVIE_DETAIL: "/movie/:id",
  WATCH:        "/watch/:id",
  // Phase 2+
  // VERIFY:    "/verify/:sessionId",
  // MOBILE:    "/mobile/:sessionId",
};

export default function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.HOME}         element={<HomePage />} />
      <Route path={ROUTES.MOVIE_DETAIL} element={<MovieDetailPage />} />
      <Route path={ROUTES.WATCH}        element={<VideoPlayerPage />} />
    </Routes>
  );
}
