"""
Smoke test for all three AgeGuard AI models.
Run from project root: python backend/scripts/test_model_inference.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from PIL import Image

def banner(title):
    print(f"\n{'='*55}\n  {title}\n{'='*55}")

def check(label, value):
    print(f"  {'OK' if value else 'FAIL'}  {label}")
    return value

all_ok = True

# ── 1. Face Detector ────────────────────────────────────────────
banner("1. Face Detector (YuNet)")
try:
    from ai.face_detector import detect_face
    from ai.config import FACE_YUNET_MODEL_PATH
    exists = os.path.exists(FACE_YUNET_MODEL_PATH)
    all_ok &= check(f"YuNet model exists at {FACE_YUNET_MODEL_PATH}", exists)
    if exists:
        # Synthetic bright image — likely no face, but should not crash
        img = Image.fromarray(np.random.randint(80, 180, (480, 640, 3), dtype=np.uint8))
        r = detect_face(img)
        all_ok &= check("detect_face() runs without error", True)
        print(f"  INFO  Result: {r['success']} — {r.get('reason','')}")
except Exception as e:
    print(f"  FAIL  Exception: {e}")
    all_ok = False

# ── 2. PAD Model ────────────────────────────────────────────────
banner("2. PAD / Liveness (ONNX MiniFAS)")
try:
    from ai.pad_detector import _get_session, predict_pad
    from ai.config import PAD_MODEL_PATH
    all_ok &= check(f"ONNX model exists at {PAD_MODEL_PATH}", os.path.exists(PAD_MODEL_PATH))
    _get_session()
    all_ok &= check("ONNX session loads", True)
    face = Image.fromarray(np.random.randint(80, 180, (128, 128, 3), dtype=np.uint8))
    res = predict_pad(face)
    all_ok &= check("predict_pad() returns dict", isinstance(res, dict))
    all_ok &= check("label is REAL or SPOOF", res.get("label") in ("REAL", "SPOOF"))
    print(f"  INFO  {res}")
except Exception as e:
    print(f"  FAIL  Exception: {e}")
    all_ok = False

# ── 3. Age Model ─────────────────────────────────────────────────
banner("3. Age Estimator (ResNet18)")
try:
    from ai.age_estimator import _get_model, predict_age
    from ai.config import AGE_MODEL_PATH
    all_ok &= check(f"Checkpoint exists at {AGE_MODEL_PATH}", os.path.exists(AGE_MODEL_PATH))
    _get_model()
    all_ok &= check("Model loads", True)
    face = Image.fromarray(np.random.randint(80, 180, (224, 224, 3), dtype=np.uint8))
    age = predict_age(face)
    all_ok &= check("predict_age() returns float", isinstance(age, float))
    all_ok &= check("Age in plausible range 0–100", 0 <= age <= 100)
    print(f"  INFO  Predicted age: {age:.2f}")
except Exception as e:
    print(f"  FAIL  Exception: {e}")
    all_ok = False

# ── 4. Manipulation Detector ─────────────────────────────────────
banner("4. Manipulation / Deepfake (CLIP ViT-L/14)")
try:
    from ai.manipulation_detector import _get_model, predict_manipulation
    from ai.config import MANIPULATION_MODEL_PATH
    all_ok &= check(f"Checkpoint exists at {MANIPULATION_MODEL_PATH}", os.path.exists(MANIPULATION_MODEL_PATH))
    _get_model()
    all_ok &= check("CLIP model loads", True)
    face = Image.fromarray(np.random.randint(80, 180, (224, 224, 3), dtype=np.uint8))
    res = predict_manipulation(face)
    all_ok &= check("predict_manipulation() returns dict", isinstance(res, dict))
    all_ok &= check("label is REAL or FAKE", res.get("label") in ("REAL", "FAKE"))
    print(f"  INFO  {res}")
except Exception as e:
    print(f"  FAIL  Exception: {e}")
    all_ok = False

# ── 5. Full Pipeline ─────────────────────────────────────────────
banner("5. Full Verification Pipeline")
try:
    from ai.verification_pipeline import run_verification
    img = Image.fromarray(np.random.randint(80, 180, (480, 640, 3), dtype=np.uint8))
    result = run_verification(img, required_age=18)
    all_ok &= check("run_verification() returns dict", isinstance(result, dict))
    all_ok &= check("decision field present", "decision" in result)
    all_ok &= check("status field present", "status" in result)
    print(f"  INFO  decision={result['decision']}  reason={result['reason']}")
except Exception as e:
    print(f"  FAIL  Exception: {e}")
    all_ok = False

# ── Summary ──────────────────────────────────────────────────────
print(f"\n{'='*55}")
if all_ok:
    print("  ALL TESTS PASSED")
else:
    print("  SOME TESTS FAILED — check output above")
print("="*55)
sys.exit(0 if all_ok else 1)
