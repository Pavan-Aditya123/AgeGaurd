"""
services/age_estimation_service.py

Backward-compatibility shim — delegates to ai/age_estimator.py (ResNet18).
The new verification pipeline (ai/verification_pipeline.py) uses ai/age_estimator
directly; this file is kept so any legacy code imports still work.
"""

import os
from PIL import Image

# Re-export the model path that health-check / smoke-tests reference
MODEL_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "models", "age_resnet18_best.pth")
)


def get_model():
    """Return (model, device) from the canonical age estimator."""
    from ai.age_estimator import _get_model
    return _get_model()


def predict_age(image_path: str) -> float:
    """
    Predict age from an image file path.
    Runs face detection first; falls back to full image if no face found.
    """
    from ai.face_detector import detect_face
    from ai.age_estimator import predict_age as _predict

    result = detect_face(image_path)
    if result["success"]:
        face_pil = result["face_pil"]
    else:
        face_pil = Image.open(image_path).convert("RGB")

    return _predict(face_pil)
