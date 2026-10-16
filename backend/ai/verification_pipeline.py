"""
ai/verification_pipeline.py

Complete AgeGuard verification pipeline.

Pipeline:
  Camera Image
    → Face Detection
    → Face Quality Check
    → PAD / Liveness
    → Manipulation / Deepfake Detection
    → Authenticity Gate
    → Age Estimation       (ONLY if authentic)
    → Age + Safety Margin
    → Movie Age Requirement
    → ALLOW / RECAPTURE / RESTRICT

Security guarantee: age estimation NEVER runs if PAD or manipulation fail.
"""

import logging
from PIL import Image
from io import BytesIO

from ai.face_detector import detect_face
from ai.face_quality import check_quality
from ai.pad_detector import predict_pad
from ai.manipulation_detector import predict_manipulation
from ai.authenticity_gate import evaluate_authenticity
from ai.age_estimator import predict_age
from ai.config import (
    AGE_MARGIN,
    DECISION_ALLOW,
    DECISION_RECAPTURE,
    DECISION_RESTRICT,
)

logger = logging.getLogger(__name__)


def _load_image(image_input):
    """Load image from path, bytes, or PIL Image."""
    if isinstance(image_input, Image.Image):
        return image_input
    if isinstance(image_input, bytes):
        return Image.open(BytesIO(image_input)).convert("RGB")
    return Image.open(image_input).convert("RGB")


def run_verification(image_input, required_age: int) -> dict:
    """
    Run the full AgeGuard verification pipeline.

    Args:
        image_input:  file path (str), raw bytes, or PIL Image
        required_age: minimum age required to access the movie (int)

    Returns:
        Full verification result dict (see schema below).
    """

    # ------------------------------------------------------------------ #
    # STEP 1 – Face Detection
    # ------------------------------------------------------------------ #
    face_result = detect_face(image_input)

    if not face_result["success"]:
        logger.info("[PIPELINE] FACE DETECTION FAILED: %s", face_result["reason"])
        return _build_result(
            status="failed",
            decision=DECISION_RECAPTURE,
            reason=face_result["reason"],
            face_quality={"passed": False},
        )

    face_pil = face_result["face_pil"]
    logger.info("[FACE] detected (conf=%.2f)", face_result["confidence"])

    # ------------------------------------------------------------------ #
    # STEP 2 – Face Quality Check
    # ------------------------------------------------------------------ #
    quality_result = check_quality(face_pil)

    if not quality_result["passed"]:
        logger.info("[PIPELINE] QUALITY FAILED: %s", quality_result["reason"])
        return _build_result(
            status="failed",
            decision=DECISION_RECAPTURE,
            reason=quality_result["reason"],
            face_quality=quality_result,
        )

    logger.info("[QUALITY] passed")

    # ------------------------------------------------------------------ #
    # STEP 3 – PAD / Liveness
    # ------------------------------------------------------------------ #
    try:
        pad_result = predict_pad(face_pil)
    except Exception as e:
        logger.error("[PAD] Inference error: %s", e)
        return _build_result(
            status="error",
            decision=DECISION_RECAPTURE,
            reason="Liveness check failed due to a system error. Please try again.",
            face_quality=quality_result,
        )

    logger.info("[PAD] %s %.4f", pad_result["label"], pad_result["score"])

    # ------------------------------------------------------------------ #
    # STEP 4 – Manipulation / Deepfake Detection
    # ------------------------------------------------------------------ #
    try:
        manip_result = predict_manipulation(face_pil)
    except Exception as e:
        logger.error("[MANIPULATION] Inference error: %s", e)
        return _build_result(
            status="error",
            decision=DECISION_RECAPTURE,
            reason="Authenticity check failed due to a system error. Please try again.",
            face_quality=quality_result,
            pad=pad_result,
        )

    logger.info("[MANIPULATION] %s %.4f", manip_result["label"], manip_result["score"])

    # ------------------------------------------------------------------ #
    # STEP 5 – Authenticity Gate
    # ------------------------------------------------------------------ #
    auth_result = evaluate_authenticity(pad_result, manip_result)

    if not auth_result["passed"]:
        logger.info("[AUTHENTICITY] FAILED — age estimation skipped")
        logger.info("[AGE] SKIPPED")
        logger.info("[DECISION] %s", auth_result["decision"])
        return _build_result(
            status="failed",
            decision=auth_result["decision"],
            reason=auth_result["reason"],
            face_quality=quality_result,
            pad={"label": pad_result["label"], "score": pad_result["score"]},
            manipulation={"label": manip_result["label"], "score": manip_result["score"]},
        )

    logger.info("[AUTHENTICITY] PASSED combined=%.4f", auth_result["combined_score"])

    # ------------------------------------------------------------------ #
    # STEP 6 – Age Estimation (only reached if authentic)
    # ------------------------------------------------------------------ #
    try:
        predicted_age = predict_age(face_pil)
    except Exception as e:
        logger.error("[AGE] Inference error: %s", e)
        return _build_result(
            status="error",
            decision=DECISION_RECAPTURE,
            reason="Age estimation failed. Please try again.",
            face_quality=quality_result,
            pad={"label": pad_result["label"], "score": pad_result["score"]},
            manipulation={"label": manip_result["label"], "score": manip_result["score"]},
        )

    logger.info("[AGE] %.2f", predicted_age)

    # ------------------------------------------------------------------ #
    # STEP 7 – Age Decision with Safety Margin
    # ------------------------------------------------------------------ #
    logger.info("[MOVIE] required age %d", required_age)

    decision, reason = _age_decision(predicted_age, required_age)

    logger.info("[DECISION] %s", decision)

    return _build_result(
        status="verified" if decision == DECISION_ALLOW else "failed",
        decision=decision,
        reason=reason,
        predicted_age=predicted_age,
        required_age=required_age,
        face_quality=quality_result,
        pad={"label": pad_result["label"], "score": pad_result["score"]},
        manipulation={"label": manip_result["label"], "score": manip_result["score"]},
    )


def _age_decision(predicted_age: float, required_age: int):
    """
    Apply safety-margin logic to the age decision.

    Returns:
        (decision, reason) tuple
    """
    if required_age == 0:
        return DECISION_ALLOW, "No age restriction for this title."

    diff = predicted_age - required_age

    if diff < -AGE_MARGIN:
        # Clearly below threshold
        return (
            DECISION_RESTRICT,
            f"Age requirement not satisfied (estimated {predicted_age:.0f}, required {required_age}+).",
        )
    elif -AGE_MARGIN <= diff <= AGE_MARGIN:
        # Near the boundary — uncertain
        return (
            DECISION_RECAPTURE,
            "Age could not be determined with sufficient confidence. Please recapture.",
        )
    else:
        # Clearly above threshold
        return DECISION_ALLOW, "Age requirement satisfied."


def _build_result(
    *,
    status: str,
    decision: str,
    reason: str,
    predicted_age: float = None,
    required_age: int = None,
    face_quality: dict = None,
    pad: dict = None,
    manipulation: dict = None,
) -> dict:
    """Assemble the standardised verification result dict."""
    result = {
        "status": status,
        "decision": decision,
        "reason": reason,
        "face_quality": face_quality or {},
    }
    if predicted_age is not None:
        result["predicted_age"] = round(predicted_age, 1)
    if required_age is not None:
        result["required_age"] = required_age
    if pad is not None:
        result["pad"] = pad
    if manipulation is not None:
        result["manipulation"] = manipulation
    return result
