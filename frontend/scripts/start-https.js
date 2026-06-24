/**
 * scripts/start-https.js
 *
 * Starts the dev server with HTTPS for mobile camera testing.
 * Usage: npm run start:https
 */

const fs = require("fs");
const { spawn } = require("child_process");
const path = require("path");

const root = path.join(__dirname, "..");

function loadDotEnv() {
  const envPath = path.join(root, ".env");
  if (!fs.existsSync(envPath)) return {};

  const vars = {};
  fs.readFileSync(envPath, "utf8")
    .split("\n")
    .forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) return;
      const eq = trimmed.indexOf("=");
      if (eq === -1) return;
      vars[trimmed.slice(0, eq).trim()] = trimmed.slice(eq + 1).trim();
    });
  return vars;
}

const dotenv = loadDotEnv();
const mobileUrl = dotenv.REACT_APP_MOBILE_BASE_URL || "(set REACT_APP_MOBILE_BASE_URL in .env)";

const env = {
  ...process.env,
  ...dotenv,
  HOST: "0.0.0.0",
  PORT: dotenv.PORT || process.env.PORT || "3000",
  HTTPS: "true",
  SSL_CRT_FILE: "certs/dev.crt",
  SSL_KEY_FILE: "certs/dev.key",
  DANGEROUSLY_DISABLE_HOST_CHECK: "true",
};

console.log("Starting HTTPS dev server (for mobile camera testing)...");
console.log("Desktop:  https://localhost:3000  → Advanced → Proceed (one time)");
console.log(`Phone:    ${mobileUrl}  → accept security warning once\n`);

const child = spawn("react-scripts", ["start"], {
  env,
  stdio: "inherit",
  shell: true,
  cwd: root,
});

child.on("exit", (code) => process.exit(code ?? 0));
