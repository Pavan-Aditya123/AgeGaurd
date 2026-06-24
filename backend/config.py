"""
config.py

Centralized network and application configuration.
Set SERVER_IP once — URLs for QR codes and mobile access are derived from it.
"""

import os

# ---------------------------------------------------------------------------
# Network — change SERVER_IP when your Wi-Fi / LAN address changes
# ---------------------------------------------------------------------------
SERVER_IP = os.environ.get("SERVER_IP", "192.168.205.134")
FRONTEND_PORT = os.environ.get("FRONTEND_PORT", "3000")
BACKEND_PORT = os.environ.get("BACKEND_PORT", "5000")
USE_HTTPS = os.environ.get("USE_HTTPS", "true").lower() in ("1", "true", "yes")

# Full frontend URL used in QR codes (phones must reach this host)
FRONTEND_SCHEME = "https" if USE_HTTPS else "http"
FRONTEND_BASE_URL = os.environ.get(
    "FRONTEND_BASE_URL",
    f"{FRONTEND_SCHEME}://{SERVER_IP}:{FRONTEND_PORT}",
)

# Session lifetime for verification (minutes)
SESSION_TTL_MINUTES = int(os.environ.get("SESSION_TTL_MINUTES", "30"))
