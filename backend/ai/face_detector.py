"""
ai/face_detector.py

Robust face detection using OpenCV YuNet (cv2.FaceDetectorYN).
YuNet handles phone selfies, varying angles, and lighting far better than Haar.

Model: backend/models/face_detection_yunet.onnx (232 KB, downloaded once)

Returns bounding box, confidence, and a padded face crop as PIL Image.
Rejects: no face, multiple faces, face too small.
"""

import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import logging
import os

from ai.config import FACE_MIN_SIZE_PX, FACE_PADDING_RATIO, FACE_YUNET_MODEL_PATH

logger = logging.getLogger(__name__)

YUNET_MODEL_PATH = FACE_YUNET_MODEL_PATH

_detector_cache: dict = {}   # keyed by (width, height)


def _get_detector(width: int, height: int):
    """Get or create a YuNet detector for the given image size."""
    key = (width, height)
    if key not in _detector_cache:
        _detector_cache.clear()   # avoid unbounded growth
        _detector_cache[key] = cv2.FaceDetectorYN_create(
            YUNET_MODEL_PATH, "", (width, height),
            score_threshold=0.40,
            nms_threshold=0.30,
            top_k=10,
        )
    return _detector_cache[key]


def _load_image(image_input) -> np.ndarray:
    """Load image from path, bytes, or PIL Image → BGR numpy array."""
    if isinstance(image_input, bytes):
        nparr = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif isinstance(image_input, Image.Image):
        img = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
    else:
        img = cv2.imread(str(image_input))
    if img is None:
        raise ValueError("Could not load image")
    return img


def detect_face(image_input) -> dict:
    """
    Detect exactly one face using YuNet.

    Returns on success:
        {
            "success": True,
            "bbox": (x, y, w, h),
            "confidence": float,
            "face_pil": PIL.Image (padded crop, RGB),
            "num_faces": int,
        }
    Returns on failure:
        {
            "success": False,
            "reason": str,
            "num_faces": int,
        }
    """
    try:
        img_bgr = _load_image(image_input)
    except Exception as e:
        logger.error("[FACE] Image load error: %s", e)
        return {"success": False, "reason": "Could not load image.", "num_faces": 0}

    h, w = img_bgr.shape[:2]
    detector = _get_detector(w, h)
    _, faces = detector.detect(img_bgr)

    num_faces = len(faces) if faces is not None else 0

    if num_faces == 0:
        logger.info("[FACE] No face detected (YuNet)")
        return {"success": False, "reason": "No face detected. Please look directly at the camera.", "num_faces": 0}

    if num_faces > 1:
        logger.info("[FACE] Multiple faces: %d", num_faces)
        return {
            "success": False,
            "reason": "Multiple faces detected. Please ensure only one face is visible.",
            "num_faces": num_faces,
        }

    # faces[i] = [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm, score]
    face = faces[0]
    fx, fy, fw, fh = int(face[0]), int(face[1]), int(face[2]), int(face[3])
    confidence = float(face[14])

    if fw < FACE_MIN_SIZE_PX or fh < FACE_MIN_SIZE_PX:
        logger.info("[FACE] Too small: %dx%d", fw, fh)
        return {
            "success": False,
            "reason": "Face is too small. Please move closer to the camera.",
            "num_faces": 1,
        }

    # Padded crop
    pad_x = int(fw * FACE_PADDING_RATIO)
    pad_y = int(fh * FACE_PADDING_RATIO)
    x1 = max(0, fx - pad_x)
    y1 = max(0, fy - pad_y)
    x2 = min(w, fx + fw + pad_x)
    y2 = min(h, fy + fh + pad_y)

    face_bgr = img_bgr[y1:y2, x1:x2]
    face_pil = Image.fromarray(cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB))

    logger.info("[FACE] detected bbox=(%d,%d,%d,%d) conf=%.3f", fx, fy, fw, fh, confidence)
    return {
        "success": True,
        "bbox": (fx, fy, fw, fh),
        "confidence": round(confidence, 3),
        "face_pil": face_pil,
        "num_faces": 1,
    }
