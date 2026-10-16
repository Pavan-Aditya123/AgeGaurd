"""
services/face_detection_service.py

Thin wrapper that delegates to ai/face_detector.py (YuNet-based).
Kept for backward compatibility with verification_routes.py debug face-save.
"""

from ai.face_detector import detect_face


def detect_and_crop_face(image_path_or_bytes, padding_ratio=0.25):
    """
    Detect and crop the primary face from an image.

    Args:
        image_path_or_bytes: File path (str) or raw bytes
        padding_ratio: ignored — handled by ai/config.py FACE_PADDING_RATIO

    Returns:
        PIL.Image of face crop, or None if no face found
    """
    result = detect_face(image_path_or_bytes)
    if result["success"]:
        return result["face_pil"]
    return None
