/**
 * src/setupProxy.js
 *
 * Proxies all /api /movies /health requests from the React dev server
 * (HTTPS :3000) to Flask (HTTP :5000).
 *
 * Works for BOTH desktop (localhost:3000) and mobile (192.168.x.x:3000)
 * because both hit the React server which forwards to Flask internally.
 * No mixed-content issues — the browser only ever talks to port 3000.
 */

const { createProxyMiddleware } = require("http-proxy-middleware");

const BACKEND = "http://localhost:5000";

const proxy = createProxyMiddleware({
  target:       BACKEND,
  changeOrigin: true,
  secure:       false,
  logLevel:     "warn",
});

module.exports = function (app) {
  app.use("/api",     proxy);
  app.use("/movies",  proxy);
  app.use("/health",  proxy);
  app.use("/Posters", proxy);
  app.use("/Videos",  proxy);
};
