/**
 * App.js
 *
 * Root component. Wraps the app in BrowserRouter and
 * delegates all routing to routes/AppRoutes.jsx.
 * No page-level logic lives here — just the router shell.
 */

import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes";

function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
