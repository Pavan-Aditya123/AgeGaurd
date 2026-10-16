"""
ai/pad_detector.py

PAD (Presentation Attack Detection) / Liveness model.
Model: backend/models/best_model_quantized.onnx (MiniFAS-based, quantized)

Verified specs:
  - Input:  [B, 3, 128, 128], float32, normalised with mean=[0.5,0.5,0.5] std=[0.5,0.5,0.5]
  - Output: [B, 2] raw logits
  - Class mapping: index 0 = SPOOF, index 1 = REAL
    (verified: dummy input yields output[-40.45, 40.49] → index 1 dominates)

Loads model ONCE at module level. Thread-safe for single-process Flask.
"""

import logging
import numpy as np
from PIL import Image
import torchvision.transforms as T

import onnxruntime as ort

from ai.config import (
    PAD_MODEL_PATH,
    PAD_INPUT_SIZE,
    PAD_MEAN,
    PAD_STD,
    PAD_REAL_CLASS,
    PAD_SPOOF_CLASS,
    PAD_REAL_THRESHOLD,
)

logger = logging.getLogger(__name__)

_session = None

_transform = T.Compose([
    T.Resize((PAD_INPUT_SIZE, PAD_INPUT_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=PAD_MEAN, std=PAD_STD),
])


def _get_session():
    global _session
    if _session is None:
        logger.info("[PAD] Loading ONNX model from %s", PAD_MODEL_PATH)
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        _session = ort.InferenceSession(
            PAD_MODEL_PATH,
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        logger.info("[PAD] ONNX model loaded")
    return _session


def _softmax(logits: np.ndarray) -> np.ndarray:
    e = np.exp(logits - logits.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def predict_pad(face_pil: Image.Image) -> dict:
    """
    Run PAD inference on a face crop.

    Args:
        face_pil: PIL Image (face crop, any size — resized internally)

    Returns:
        {
            "label": "REAL" | "SPOOF",
            "score": float (confidence of predicted class),
            "real_score": float,
            "spoof_score": float,
        }
    """
    session = _get_session()
    input_name = session.get_inputs()[0].name

    # Preprocess
    tensor = _transform(face_pil.convert("RGB")).unsqueeze(0).numpy()  # [1,3,128,128]

    # Inference
    logits = session.run(None, {input_name: tensor})[0]  # [1,2]
    probs = _softmax(logits)[0]  # [2]

    real_score = float(probs[PAD_REAL_CLASS])
    spoof_score = float(probs[PAD_SPOOF_CLASS])

    label = "REAL" if real_score >= PAD_REAL_THRESHOLD else "SPOOF"
    score = real_score if label == "REAL" else spoof_score

    logger.info("[PAD] %s %.4f (real=%.4f spoof=%.4f)", label, score, real_score, spoof_score)
    return {
        "label": label,
        "score": round(score, 4),
        "real_score": round(real_score, 4),
        "spoof_score": round(spoof_score, 4),
    }
