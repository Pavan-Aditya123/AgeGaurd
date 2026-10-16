# AgeGuard — Setup & Run Guide

## Files Changed / Added

### Backend — New AI Pipeline
| File | Description |
|------|-------------|
| `backend/ai/__init__.py` | Package marker |
| `backend/ai/config.py` | **All thresholds & model paths in one place** |
| `backend/ai/face_detector.py` | YuNet face detection (robust on phone selfies) |
| `backend/ai/face_quality.py` | Blur / brightness / size quality checks |
| `backend/ai/pad_detector.py` | PAD liveness — `best_model_quantized.onnx` |
| `backend/ai/manipulation_detector.py` | Deepfake detection — `clip_ckpt_best.pth` (CLIP ViT-L/14) |
| `backend/ai/age_estimator.py` | Age estimation — `age_resnet18_best.pth` (ResNet18) |
| `backend/ai/authenticity_gate.py` | PAD + manipulation score fusion |
| `backend/ai/verification_pipeline.py` | **Full pipeline: face → quality → PAD → manip → auth → age → decision** |

### Backend — Updated
| File | Change |
|------|--------|
| `backend/app.py` | Pre-loads all 3 models at startup, auto-downloads YuNet |
| `backend/routes/verification_routes.py` | Uses full AI pipeline, returns ALLOW/RECAPTURE/RESTRICT |
| `backend/services/session_service.py` | Added `decision`, `reason`, `pad`, `manipulation` fields |
| `backend/services/age_estimation_service.py` | Delegates to new ResNet18 estimator |
| `backend/services/face_detection_service.py` | Delegates to new YuNet detector |
| `backend/requirements.txt` | Added `onnxruntime`, `transformers` |

### Frontend — Updated
| File | Change |
|------|--------|
| `frontend/src/pages/MobileVerificationPage.jsx` | Stage messages, handles ALLOW/RESTRICT/RECAPTURE |
| `frontend/src/pages/VerificationPage.jsx` | Polls for recapture status, Try Again button |
| `frontend/src/services/verificationService.js` | Passes all new response fields |

### Models Successfully Loaded
| Model | File | Status |
|-------|------|--------|
| PAD/Liveness | `best_model_quantized.onnx` | ✅ ONNX Runtime |
| Age Estimation | `age_resnet18_best.pth` | ✅ ResNet18 (val MAE 4.86 yrs) |
| Manipulation/Deepfake | `clip_ckpt_best.pth` | ✅ CLIP ViT-L/14 + Linear head |
| Face Detection | `face_detection_yunet.onnx` | ✅ Auto-downloaded (232 KB) |

---

## Run Commands

### 1. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start backend (from project root)
```bash
python backend/app.py
```
Flask starts on `http://0.0.0.0:5000`  
All 3 AI models load at startup (~15 seconds on first run).

### 3. Start frontend (new terminal)
```bash
cd frontend
npm install        # first time only
npm run start      # desktop browser at http://localhost:3000
```

### For mobile QR scanning (phone must be on same Wi-Fi):
```bash
cd frontend
npm run update-network   # auto-detects your LAN IP, updates .env
npm run start:https      # HTTPS server for camera access on phone
```
Then scan the QR code. On first scan, accept the HTTPS security warning.

---

## Verification Pipeline

```
Camera Image
  ↓ Face Detection (YuNet)
  ↓ Face Quality Check (blur / brightness / size)
  ↓ PAD / Liveness (MiniFAS ONNX)
  ↓ Manipulation / Deepfake (CLIP ViT-L/14)
  ↓ Authenticity Gate (PAD score + MANIP score fusion)
  ↓ Age Estimation (ResNet18)  ← ONLY if authentic
  ↓ Age + Safety Margin check
  ↓ ALLOW / RECAPTURE / RESTRICT
```

**Security guarantee:** Age estimation never runs if PAD or manipulation check fails.

---

## Backend Logs (console output during demo)

```
[FACE]          detected bbox=(201,402,390,510) conf=0.879
[QUALITY]       passed size=584x764 brightness=111.6 blur=13.8
[PAD]           REAL 1.0000
[MANIPULATION]  REAL 0.5490
[AUTHENTICITY]  PASSED combined=0.7745
[AGE]           23.44
[MOVIE]         required age 18
[DECISION]      ALLOW
```

---

## Configurable Thresholds (`backend/ai/config.py`)

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `PAD_REAL_THRESHOLD` | 0.60 | Min liveness score to pass |
| `MANIP_REAL_THRESHOLD` | 0.50 | Min authenticity score to pass |
| `AUTHENTICITY_THRESHOLD` | 0.55 | Min combined (PAD+MANIP)/2 |
| `AGE_MARGIN` | 1.5 yrs | ±boundary zone → RECAPTURE |

---

## Smoke Test

```bash
# Test all models independently
python backend/scripts/test_model_inference.py

# Test full HTTP API (backend must be running)
python backend/scripts/test_api.py
```

---

## Known Limitations

- Single-frame PAD (no temporal aggregation across frames) — sufficient for demo
- CLIP real score on phone photos is ~0.54–0.73 (correct class, moderate confidence) — the model was trained on deepfake datasets, not verified on this specific phone
- YuNet misses ~1/8 test photos (very dark/blurred image with no frontal face)
- In-memory sessions — restart clears all sessions (acceptable for demo)
