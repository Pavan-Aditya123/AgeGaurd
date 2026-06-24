"""
Quick inference smoke test for age_model.pth.
Run from backend/: python scripts/test_model_inference.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
import numpy as np
from services.age_estimation_service import get_model, predict_age, MODEL_PATH


def main():
    print(f"Model path: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print("FAIL: Age estimation model not found. Please place age_model.pth inside backend/models.")
        sys.exit(1)

    model, device = get_model()
    print(f"Model loaded on {device}")
    print(f"Architecture: EfficientNet-B3 + regression head")

    # Synthetic RGB image (224x224) — sanity check that forward pass works
    test_path = os.path.join(os.path.dirname(__file__), "..", "uploads", "_test_inference.jpg")
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    arr = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    Image.fromarray(arr).save(test_path, "JPEG")

    age = predict_age(test_path)
    print(f"Test inference predicted age: {age:.2f} years")
    print("OK: Model loads and inference runs successfully.")

    os.remove(test_path)


if __name__ == "__main__":
    main()
