"""
ai/face_quality.py

Lightweight face quality checks before running AI models.
Checks blur, brightness, and face crop size.
Does NOT reject normal faces aggressively.
"""

import cv2
import numpy as np
from PIL import Image
import logging

from ai.config import (
    QUALITY_MIN_FACE_SIZE_PX,
    QUALITY_BLUR_THRESHOLD,
    QUALITY_DARK_THRESHOLD,
    QUALITY_BRIGHT_THRESHOLD,
)

logger = logging.getLogger(__name__)


def check_quality(face_pil: Image.Image):
    """
    Run quality checks on a face crop (PIL Image).

    Returns:
        {"passed": True}
        or
        {"passed": False, "reason": str}
    """
    img_np = np.array(face_pil.convert("RGB"))
    h, w = img_np.shape[:2]

    # --- Size check ---
    if w < QUALITY_MIN_FACE_SIZE_PX or h < QUALITY_MIN_FACE_SIZE_PX:
        reason = "Face is too small. Please move closer to the camera."
        logger.info("[QUALITY] FAIL size=%dx%d", w, h)
        return {"passed": False, "reason": reason}

    # --- Brightness check ---
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    mean_brightness = float(np.mean(gray))

    if mean_brightness < QUALITY_DARK_THRESHOLD:
        reason = "Lighting is too dark. Please move to a brighter location."
        logger.info("[QUALITY] FAIL brightness=%.1f (too dark)", mean_brightness)
        return {"passed": False, "reason": reason}

    if mean_brightness > QUALITY_BRIGHT_THRESHOLD:
        reason = "Image is overexposed. Please avoid direct light sources."
        logger.info("[QUALITY] FAIL brightness=%.1f (too bright)", mean_brightness)
        return {"passed": False, "reason": reason}

    # --- Blur check (Laplacian variance) ---
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < QUALITY_BLUR_THRESHOLD:
        reason = "Image is too blurry. Please hold still and ensure camera is focused."
        logger.info("[QUALITY] FAIL blur=%.1f (threshold=%.1f)", laplacian_var, QUALITY_BLUR_THRESHOLD)
        return {"passed": False, "reason": reason}

    logger.info(
        "[QUALITY] passed size=%dx%d brightness=%.1f blur=%.1f",
        w, h, mean_brightness, laplacian_var,
    )
    return {"passed": True}
