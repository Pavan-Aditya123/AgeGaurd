"""
ai/config.py

Centralised configuration for all AI pipeline models and thresholds.
Edit thresholds here — never scatter magic numbers in inference code.
"""

import os

# ---------------------------------------------------------------------------
# Model paths (project-relative)
# ---------------------------------------------------------------------------
_BASE = os.path.join(os.path.dirname(__file__), "..", "models")

AGE_MODEL_PATH         = os.path.normpath(os.path.join(_BASE, "age_resnet18_best.pth"))
PAD_MODEL_PATH         = os.path.normpath(os.path.join(_BASE, "best_model_quantized.onnx"))
MANIPULATION_MODEL_PATH = os.path.normpath(os.path.join(_BASE, "clip_ckpt_best.pth"))
FACE_YUNET_MODEL_PATH  = os.path.normpath(os.path.join(_BASE, "face_detection_yunet.onnx"))

# ---------------------------------------------------------------------------
# Face detection
# ---------------------------------------------------------------------------
FACE_MIN_SIZE_PX        = 60    # Minimum face bounding-box size in pixels
FACE_CONFIDENCE_MIN     = 0.3   # Haar cascade: minNeighbors proxy
FACE_PADDING_RATIO      = 0.25  # Extra context around detected face crop

# ---------------------------------------------------------------------------
# Face quality
# ---------------------------------------------------------------------------
QUALITY_MIN_FACE_SIZE_PX = 48   # Cropped face must be at least this many pixels wide/tall
QUALITY_BLUR_THRESHOLD   = 6.0  # Laplacian variance — phone JPEGs score 8-55, reject only extreme blur
QUALITY_DARK_THRESHOLD   = 30   # Mean brightness below this = too dark
QUALITY_BRIGHT_THRESHOLD = 230  # Mean brightness above this = overexposed

# ---------------------------------------------------------------------------
# PAD (Liveness / anti-spoofing)
# Class mapping for best_model_quantized.onnx (MiniFAS-based)
# Verified via logit inspection: index 1 = REAL, index 0 = SPOOF
# ---------------------------------------------------------------------------
PAD_REAL_CLASS   = 1            # argmax index corresponding to real/live
PAD_SPOOF_CLASS  = 0            # argmax index corresponding to spoof
PAD_REAL_THRESHOLD = 0.60       # softmax score for REAL must exceed this to pass
PAD_INPUT_SIZE   = 128          # ONNX model input: 128x128
PAD_MEAN         = [0.5, 0.5, 0.5]
PAD_STD          = [0.5, 0.5, 0.5]

# ---------------------------------------------------------------------------
# Temporal PAD aggregation (multi-frame)
# ---------------------------------------------------------------------------
PAD_NUM_FRAMES       = 1   # Currently single-frame; increase to 3+ for video
PAD_SPOOF_FRAME_LIMIT = 1  # Number of spoof frames that trigger rejection

# ---------------------------------------------------------------------------
# Manipulation / deepfake detection (CLIP ViT-L/14 + linear head)
# Class mapping for clip_ckpt_best.pth — VERIFIED by probing on real photos:
#   real photos score higher on index 1 → index 1 = REAL, index 0 = FAKE
# ---------------------------------------------------------------------------
MANIP_REAL_CLASS      = 1
MANIP_FAKE_CLASS      = 0
MANIP_REAL_THRESHOLD  = 0.50    # softmax score for REAL must exceed this
MANIP_INPUT_SIZE      = 224
MANIP_MEAN            = [0.48145466, 0.4578275,  0.40821073]
MANIP_STD             = [0.26862954, 0.26130258, 0.27577711]

# ---------------------------------------------------------------------------
# Authenticity gate (fusion of PAD + manipulation)
# ---------------------------------------------------------------------------
# Both PAD and manipulation must individually pass their thresholds.
# Additionally the combined authenticity score must exceed AUTHENTICITY_THRESHOLD.
# Combined score = (pad_real_score + manip_real_score) / 2
AUTHENTICITY_THRESHOLD = 0.55

# ---------------------------------------------------------------------------
# Age estimation (ResNet18, UTKFace-trained)
# ---------------------------------------------------------------------------
AGE_INPUT_SIZE  = 224
AGE_MEAN        = [0.485, 0.456, 0.406]
AGE_STD         = [0.229, 0.224, 0.225]

# Safety margin applied around the age decision boundary.
# If |predicted_age - required_age| <= AGE_MARGIN → RECAPTURE.
AGE_MARGIN = 1.5   # years  (boundary zone: required_age ± 1.5 → RECAPTURE)

# ---------------------------------------------------------------------------
# Decision labels
# ---------------------------------------------------------------------------
DECISION_ALLOW    = "ALLOW"
DECISION_RECAPTURE = "RECAPTURE"
DECISION_RESTRICT  = "RESTRICT"
