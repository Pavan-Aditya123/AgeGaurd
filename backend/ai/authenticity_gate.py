"""
ai/authenticity_gate.py

Fusion of PAD and manipulation scores to decide whether the face is authentic.

Rules:
  1. If PAD strongly indicates SPOOF → FAIL (don't run age)
  2. If manipulation strongly indicates FAKE → FAIL (don't run age)
  3. If combined score is below AUTHENTICITY_THRESHOLD → FAIL
  4. Otherwise → PASS (proceed to age estimation)
"""

import logging
from ai.config import (
    PAD_REAL_THRESHOLD,
    MANIP_REAL_THRESHOLD,
    AUTHENTICITY_THRESHOLD,
    DECISION_RECAPTURE,
    DECISION_RESTRICT,
)

logger = logging.getLogger(__name__)


def evaluate_authenticity(pad_result: dict, manip_result: dict) -> dict:
    """
    Determine overall authenticity.

    Args:
        pad_result:   output of pad_detector.predict_pad()
        manip_result: output of manipulation_detector.predict_manipulation()

    Returns:
        {
            "passed": bool,
            "decision": "RECAPTURE" | "RESTRICT",  # only present if not passed
            "reason": str,
            "combined_score": float,
        }
    """
    pad_real_score   = pad_result.get("real_score", 0.0)
    manip_real_score = manip_result.get("real_score", 0.0)

    pad_label   = pad_result.get("label", "SPOOF")
    manip_label = manip_result.get("label", "FAKE")

    combined_score = (pad_real_score + manip_real_score) / 2.0

    # --- Strong spoof signal ---
    if pad_label == "SPOOF":
        reason = "Face appears to be spoofed. Please use a real face."
        logger.info("[AUTHENTICITY] FAILED PAD=SPOOF pad_score=%.4f", pad_real_score)
        return {
            "passed": False,
            "decision": DECISION_RESTRICT,
            "reason": reason,
            "combined_score": round(combined_score, 4),
        }

    # --- Strong manipulation/deepfake signal ---
    if manip_label == "FAKE":
        reason = "Image appears manipulated or is a deepfake."
        logger.info("[AUTHENTICITY] FAILED MANIP=FAKE manip_score=%.4f", manip_real_score)
        return {
            "passed": False,
            "decision": DECISION_RESTRICT,
            "reason": reason,
            "combined_score": round(combined_score, 4),
        }

    # --- Combined score check (catches borderline cases) ---
    if combined_score < AUTHENTICITY_THRESHOLD:
        reason = "Could not confirm face authenticity. Please recapture."
        logger.info(
            "[AUTHENTICITY] FAILED combined=%.4f < threshold=%.4f",
            combined_score, AUTHENTICITY_THRESHOLD,
        )
        return {
            "passed": False,
            "decision": DECISION_RECAPTURE,
            "reason": reason,
            "combined_score": round(combined_score, 4),
        }

    logger.info(
        "[AUTHENTICITY] PASSED pad=%.4f manip=%.4f combined=%.4f",
        pad_real_score, manip_real_score, combined_score,
    )
    return {
        "passed": True,
        "combined_score": round(combined_score, 4),
    }
