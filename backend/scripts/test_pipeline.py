"""
Test the full AgeGuard AI pipeline on all uploaded images.
Run from project root: python backend/scripts/test_pipeline.py
"""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO, format="%(message)s")

from ai.verification_pipeline import run_verification

UPLOADS = os.path.join(os.path.dirname(__file__), "..", "uploads")

uploads = sorted([
    f for f in os.listdir(UPLOADS)
    if f.endswith(".jpg") and "_face" not in f and "gitkeep" not in f
])

print("=" * 60)
print("AGEGUARD PIPELINE — END-TO-END TEST")
print("=" * 60)

for fname in uploads:
    path = os.path.join(UPLOADS, fname)
    print(f"\n--- {fname} ---")
    try:
        result = run_verification(path, required_age=18)
        print(f"  DECISION : {result.get('decision')}")
        print(f"  REASON   : {result.get('reason')}")
        if result.get("predicted_age") is not None:
            print(f"  AGE      : {result.get('predicted_age')}")
        if result.get("pad"):
            p = result["pad"]
            print(f"  PAD      : {p['label']} {p['score']}")
        if result.get("manipulation"):
            m = result["manipulation"]
            print(f"  MANIP    : {m['label']} {m['score']}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
