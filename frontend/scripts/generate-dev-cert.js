/**
 * scripts/generate-dev-cert.js
 *
 * Generates a self-signed TLS cert for local HTTPS dev (mobile camera access).
 * Run: npm run setup-https
 */

const fs = require("fs");
const path = require("path");
const selfsigned = require("selfsigned");

async function main() {
  const ip = process.env.LAN_IP;
  if (!ip) {
    console.error("Set LAN_IP or run: npm run update-network");
    process.exit(1);
  }
  const certsDir = path.join(__dirname, "..", "certs");

  fs.mkdirSync(certsDir, { recursive: true });

  const attrs = [{ name: "commonName", value: "AgeGuard Dev" }];
  const pems = await selfsigned.generate(attrs, {
    keySize: 2048,
    algorithm: "sha256",
    extensions: [
      { name: "basicConstraints", cA: false },
      {
        name: "keyUsage",
        digitalSignature: true,
        keyEncipherment: true,
      },
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

  console.log(`✓ HTTPS certs generated for ${ip}`);
  console.log(`  → frontend/certs/dev.crt`);
  console.log(`  → frontend/certs/dev.key`);
  console.log(`\nRestart npm start, then on your phone open:`);
  console.log(`  https://${ip}:3000`);
  console.log(`Accept the security warning once, then scan the QR again.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
