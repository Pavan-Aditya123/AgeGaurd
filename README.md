# AgeGuard — AI-Powered OTT Age Verification

> **B.Tech Final Year Project** — Real-time facial age verification for OTT streaming platforms using deep learning.

AgeGuard replaces the fake "I am 18" checkbox with genuine AI-based face verification. Before watching age-restricted content, users scan a QR code with their phone, show their face to the camera, and a multi-stage AI pipeline decides if access should be granted.

---

## Demo Flow

```
Desktop: Select restricted movie → QR code appears
Phone:   Scan QR → Camera opens → Capture face
Backend: Face Detection → Quality Check → Liveness → Deepfake → Age Estimation → Decision
Desktop: Access granted / denied / recapture → Video unlocks if allowed
```

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python 3.10+, Flask 3.0, Flask-CORS |
| AI/ML | PyTorch 2.0+, ONNX Runtime, OpenCV 4.13, HuggingFace Transformers |
| Frontend | React 18, Tailwind CSS 3, React Router v6, qrcode.react |
| Utilities | Pillow, torchvision, timm, selfsigned |

---

## AI Pipeline

Every selfie goes through 7 steps in order. Step 6 (age estimation) only runs if all previous steps pass.

```
Camera Image
    │
    ▼ Step 1 — Face Detection (YuNet ONNX)
    │   Rejects: no face, multiple faces, face too small
    │
    ▼ Step 2 — Face Quality Check
    │   Rejects: blur < 6.0, brightness < 30 or > 230, size < 48px
    │
    ▼ Step 3 — PAD / Liveness (MiniFAS ONNX)
    │   Detects: printed photos, screen replay attacks
    │   Threshold: real_score > 0.60
    │
    ▼ Step 4 — Deepfake Detection (CLIP ViT-L/14)
    │   Detects: digitally manipulated / AI-generated faces
    │   Threshold: real_score > 0.50
    │
    ▼ Step 5 — Authenticity Gate
    │   combined = (PAD_real + CLIP_real) / 2 > 0.55
    │   Age estimation SKIPPED if this fails
    │
    ▼ Step 6 — Age Estimation (ResNet18, UTKFace-trained)
    │   Output: predicted age (float), val MAE ≈ 4.86 years
    │
    ▼ Step 7 — Age Decision (±1.5 year safety margin)
         predicted > required + 1.5  → ALLOW
         |diff| ≤ 1.5                → RECAPTURE
         predicted < required - 1.5  → RESTRICT
```

---

## Models

| Model | File | Purpose | Input | Output |
|-------|------|---------|-------|--------|
| YuNet | `face_detection_yunet.onnx` | Face detection | Full image | Bounding box + confidence |
| MiniFAS | `best_model_quantized.onnx` | Liveness/anti-spoof | 128×128, norm[-1,+1] | [spoof_score, real_score] |
| CLIP ViT-L/14 | `clip_ckpt_best.pth` | Deepfake detection | 224×224, CLIP norm | [fake_score, real_score] |
| ResNet18 | `age_resnet18_best.pth` | Age estimation | 224×224, ImageNet norm | Age (float) |

All models are loaded once at backend startup into GPU/CPU memory and reused for every request.

Place model files in `backend/models/`. The YuNet model is auto-downloaded on first startup (~232 KB).

---

## Project Structure

```
AgeGuard/
│
├── start_ageguard.bat          ← Double-click to start everything
│
├── backend/
│   ├── app.py                  ← Flask entry point, model preloading
│   ├── config.py               ← Network config (IP, ports, session TTL)
│   ├── requirements.txt
│   ├── .env                    ← LAN IP, HTTPS flag (copy from .env.example)
│   │
│   ├── ai/                     ← Complete AI pipeline
│   │   ├── config.py           ← All thresholds & model paths
│   │   ├── face_detector.py    ← YuNet face detection
│   │   ├── face_quality.py     ← Blur / brightness / size checks
│   │   ├── pad_detector.py     ← MiniFAS liveness detection
│   │   ├── manipulation_detector.py  ← CLIP deepfake detection
│   │   ├── age_estimator.py    ← ResNet18 age prediction
│   │   ├── authenticity_gate.py      ← Score fusion gate
│   │   └── verification_pipeline.py  ← Orchestrates all 7 steps
│   │
│   ├── routes/
│   │   ├── movie_routes.py         ← GET /movies, GET /movies/<id>
│   │   └── verification_routes.py  ← Session, upload-face, access check
│   │
│   ├── services/
│   │   ├── movie_service.py        ← In-memory movie catalogue
│   │   ├── session_service.py      ← In-memory session store (TTL 30 min)
│   │   ├── age_estimation_service.py
│   │   └── face_detection_service.py
│   │
│   ├── models/                 ← AI model files (not in repo)
│   ├── uploads/                ← Saved selfies for debugging
│   ├── scripts/
│   │   ├── test_model_inference.py  ← Smoke test all 4 models
│   │   ├── test_api.py              ← End-to-end HTTP API test
│   │   └── test_pipeline.py         ← Pipeline test on real uploads
│   └── training/               ← Training code (UTKFace, ResNet18)
│
└── frontend/
    ├── package.json
    ├── src/
    │   ├── App.js
    │   ├── setupProxy.js           ← Proxies /api/* → Flask :5000
    │   ├── routes/AppRoutes.jsx    ← All URL routes
    │   ├── pages/
    │   │   ├── HomePage.jsx              ← Movie grid
    │   │   ├── MovieDetailPage.jsx       ← Movie details
    │   │   ├── VerificationPage.jsx      ← Desktop QR + polling
    │   │   ├── MobileVerificationPage.jsx ← Phone camera capture
    │   │   └── VideoPlayerPage.jsx       ← Video player + access gate
    │   ├── services/
    │   │   ├── verificationService.js    ← Session, upload, poll APIs
    │   │   └── movieService.js
    │   └── utils/
    │       ├── verificationAccess.js     ← sessionStorage access cache
    │       └── networkUtils.js           ← QR URL builder
    ├── certs/                    ← Self-signed SSL cert (auto-generated)
    └── scripts/
        ├── start-https.js        ← HTTPS dev server
        └── update-network.js     ← Detects LAN IP, regenerates cert
```

---

## API Endpoints

| Method | URL | Input | Output | Purpose |
|--------|-----|-------|--------|---------|
| GET | `/movies` | — | Array of movies | Homepage catalogue |
| GET | `/movies/<id>` | path: id | Single movie | Detail page |
| GET | `/health` | — | `{status, models}` | Health check |
| POST | `/api/verification/session` | `{movieId}` | `{sessionId, mobileVerifyUrl}` | Create QR session |
| GET | `/api/verification/session/<id>` | — | Full session JSON | Desktop polling |
| GET | `/api/verification/access` | `?movieId&sessionId` | `{allowed}` | Video access gate |
| POST | `/api/upload-face` | `{sessionId, image: base64}` | `{decision, verified, predictedAge, reason}` | Run AI pipeline |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- CUDA-capable GPU (optional, CPU works but slower)

### 1. Clone & install backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install frontend

```bash
cd frontend
npm install
```

### 3. Configure network

```bash
cd frontend
npm run update-network
```

This detects your LAN IP, updates both `.env` files, and regenerates the self-signed SSL certificate for your IP.

### 4. Start everything

**Option A — Double-click (Windows):**
```
start_ageguard.bat
```

**Option B — Manual (two terminals):**

Terminal 1:
```bash
python backend/app.py
```

Terminal 2:
```bash
cd frontend
npm run start:https
```

Wait ~40 seconds for all 3 AI models to load.

### 5. Open in browser

Desktop: `https://localhost:3000`
- Accept the self-signed certificate warning (Advanced → Proceed) once

Phone (for QR scanning):
- Open `https://192.168.x.x:3000` manually first
- Accept the certificate warning once
- Then scan QR codes normally

> **Important:** Always use `npm run start:https`, not `npm run start`. Mobile browsers block camera access on plain HTTP.

---

## Configuration

All AI thresholds are in `backend/ai/config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `FACE_MIN_SIZE_PX` | 60 | Minimum face bounding box (pixels) |
| `QUALITY_BLUR_THRESHOLD` | 6.0 | Laplacian variance minimum |
| `QUALITY_DARK_THRESHOLD` | 30 | Minimum mean brightness |
| `QUALITY_BRIGHT_THRESHOLD` | 230 | Maximum mean brightness |
| `PAD_REAL_THRESHOLD` | 0.60 | MiniFAS real-score minimum |
| `MANIP_REAL_THRESHOLD` | 0.50 | CLIP real-score minimum |
| `AUTHENTICITY_THRESHOLD` | 0.55 | Combined gate minimum |
| `AGE_MARGIN` | 1.5 years | Boundary zone → RECAPTURE |

Network settings are in `backend/config.py` (overridden by `backend/.env`):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SESSION_TTL_MINUTES` | 30 | Session expiry time |
| `SERVER_IP` | auto-detected | LAN IP for QR codes |

---

## Running Tests

```bash
# Test all 4 models load and produce valid output
python backend/scripts/test_model_inference.py

# Test full HTTP API (Flask must be running)
python backend/scripts/test_api.py

# Test AI pipeline on all saved uploads
python backend/scripts/test_pipeline.py
```

Expected output from `test_model_inference.py`:
```
  OK  YuNet model exists
  OK  detect_face() runs without error
  OK  ONNX session loads
  OK  label is REAL or SPOOF
  OK  Model loads
  OK  Age in plausible range 0–100
  OK  CLIP model loads
  OK  label is REAL or FAKE
  OK  run_verification() returns dict
  ALL TESTS PASSED
```

---

## Security Design

| Threat | Defense | Implementation |
|--------|---------|----------------|
| Printed photo attack | MiniFAS PAD | `pad_detector.py` |
| Screen replay attack | MiniFAS PAD | `pad_detector.py` |
| Deepfake / manipulation | CLIP deepfake detector | `manipulation_detector.py` |
| Minor bypassing age check | Age estimation + safety margin | `verification_pipeline.py` |
| Frontend bypass (`verified=true`) | Backend-only decisions | `session_service.is_access_granted()` |
| Cross-movie session reuse | Movie ID bound to session | `session["movieId"] != movie_id` check |
| Expired session reuse | 30-minute TTL | `session_service._is_expired()` |
| Multiple faces in frame | Rejection | `face_detector.py` |
| Camera-free bypass | Quality gate | `face_quality.py` |
| Unencrypted image transit | HTTPS | `npm run start:https` + self-signed cert |

**Critical security guarantee:** Age estimation never runs if liveness or deepfake detection fails.

---

## Movie Catalogue

| # | Title | Rating | Required Age | Restricted |
|---|-------|--------|-------------|-----------|
| 1 | Chhichhore | U | 0 | No |
| 2 | Interstellar | U/A 13+ | 13 | No |
| 3 | Dhurandhar | A (18+) | 18 | **Yes** |
| 4 | Animal | A (18+) | 18 | **Yes** |
| 5 | John Wick 4 | A (18+) | 18 | **Yes** |
| 6 | Kung Fu Panda | U | 0 | No |

---

## Limitations

- **Single-frame liveness** — no temporal/video-based PAD
- **Moderate CLIP confidence** — real selfies score 0.54–0.73 (threshold is permissive)
- **Age estimation accuracy** — val MAE ≈ 4.86 years; borderline ages trigger RECAPTURE
- **In-memory sessions** — lost on server restart; no database
- **Self-signed certificate** — requires manual one-time acceptance on each device
- **Single-process Flask** — not production-scalable

---

## Future Work

- Video-based liveness (blink detection, head movement)
- Larger and more diverse age estimation dataset
- Redis-backed persistent sessions
- Production WSGI deployment (Gunicorn + Nginx)
- Privacy-preserving image processing (delete after verification)
- Audit logging
- Cloud deployment

---

## Training

The ResNet18 age model was trained from scratch on UTKFace:

```bash
python backend/training/train.py
```

Training configuration: 20 epochs, AdamW optimizer, MSE loss, batch size 32, input 224×224, ImageNet normalization.

Best checkpoint saved to `backend/models/age_resnet18_best.pth`.

Evaluate on test set:
```bash
python backend/training/evaluate.py
```

---

## License

B.Tech Final Year Project — Academic use only.
