/**
 * scripts/update-network.js
 *
 * Run after Wi-Fi / IP change. Updates frontend + backend .env and regenerates HTTPS cert.
 * Usage: npm run update-network
 * Override IP: $env:LAN_IP="192.168.1.100"; npm run update-network
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const selfsigned = require("selfsigned");

const frontendRoot = path.join(__dirname, "..");
const backendRoot = path.join(frontendRoot, "..", "backend");

function detectLanIp() {
  if (process.env.LAN_IP) return process.env.LAN_IP.trim();
  if (process.env.SERVER_IP) return process.env.SERVER_IP.trim();

  try {
    const out = execSync(
      'powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -match \'Wi-Fi|Wireless\' -and $_.IPAddress -notmatch \'^169\\.254\' } | Select-Object -First 1).IPAddress"',
      { encoding: "utf8" }
    ).trim();
    if (out) return out;
  } catch (_) {}

  throw new Error("Could not detect Wi-Fi IP. Run: $env:LAN_IP=\"YOUR.IP.HERE\"; npm run update-network");
}

function upsertEnvLine(content, key, value) {
  const pattern = new RegExp(`^${key}=.*$`, "m");
  const line = `${key}=${value}`;
  if (pattern.test(content)) {
    return content.replace(pattern, line);
  }
  return content.trimEnd() + `\n${line}\n`;
}

async function generateCert(ip) {
  const certsDir = path.join(frontendRoot, "certs");
  fs.mkdirSync(certsDir, { recursive: true });

  const pems = await selfsigned.generate([{ name: "commonName", value: "AgeGuard Dev" }], {
    keySize: 2048,
    algorithm: "sha256",
    extensions: [
      { name: "basicConstraints", cA: false },
      { name: "keyUsage", digitalSignature: true, keyEncipherment: true },
      {
        name: "subjectAltName",
        altNames: [
          { type: 7, ip },
          { type: 7, ip: "127.0.0.1" },
          { type: 2, value: "localhost" },
        ],
      },
    ],
  });

  fs.writeFileSync(path.join(certsDir, "dev.key"), pems.private);
  fs.writeFileSync(path.join(certsDir, "dev.crt"), pems.cert);
}

function updateFrontendEnv(ip) {
  const envPath = path.join(frontendRoot, ".env");
  let content = fs.existsSync(envPath)
    ? fs.readFileSync(envPath, "utf8")
    : fs.readFileSync(path.join(frontendRoot, ".env.example"), "utf8");

  const url = `https://${ip}:3000`;
  content = upsertEnvLine(content, "REACT_APP_SERVER_IP", ip);
  content = upsertEnvLine(content, "REACT_APP_MOBILE_BASE_URL", url);
  content = upsertEnvLine(content, "REACT_APP_USE_HTTPS", "true");

  fs.writeFileSync(envPath, content);
  return url;
}

function updateBackendEnv(ip) {
  const envPath = path.join(backendRoot, ".env");
  let content = fs.existsSync(envPath)
    ? fs.readFileSync(envPath, "utf8")
    : fs.readFileSync(path.join(backendRoot, ".env.example"), "utf8");

  const url = `https://${ip}:3000`;
  content = upsertEnvLine(content, "SERVER_IP", ip);
  content = upsertEnvLine(content, "USE_HTTPS", "true");
  content = upsertEnvLine(content, "FRONTEND_BASE_URL", url);

  fs.writeFileSync(envPath, content);
}

async function main() {
  const ip = detectLanIp();
  const url = updateFrontendEnv(ip);
  updateBackendEnv(ip);
  await generateCert(ip);

  console.log(`✓ Network updated for ${ip}`);
  console.log(`  frontend/.env → REACT_APP_MOBILE_BASE_URL=${url}`);
  console.log(`  backend/.env  → SERVER_IP=${ip}, FRONTEND_BASE_URL=${url}`);
  console.log(`  certs         → regenerated for ${ip}`);
  console.log(`\nNext steps:`);
  console.log(`  1. Restart backend: cd backend && python app.py`);
  console.log(`  2. Restart frontend: cd frontend && npm run start:https`);
  console.log(`  3. On phone: open ${url}`);
  console.log(`  4. Tap Advanced → Proceed (one time per new IP)`);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
