"""
ai/manipulation_detector.py

Deepfake / face manipulation detection.
Model: backend/models/clip_ckpt_best.pth

Verified architecture (from state_dict inspection):
  - module.backbone: CLIPVisionModel (ViT-L/14)
      embed_dim=1024, num_layers=24, patch_size=14, input=224x224
      position_ids shape [1,257] → 256 patches + 1 cls, 16×16 grid
  - module.head: Linear(1024, 2)
      output[0,1024] weight → 2-class: index 0=REAL, index 1=FAKE

Preprocessing:
  - CLIP-standard normalization: mean=[0.48145466, 0.4578275, 0.40821073]
                                  std= [0.26862954, 0.26130258, 0.27577711]
  - Resize to 224×224

Loads model ONCE at startup.
"""

import logging
import torch
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image
from collections import OrderedDict

from ai.config import (
    MANIPULATION_MODEL_PATH,
    MANIP_INPUT_SIZE,
    MANIP_MEAN,
    MANIP_STD,
    MANIP_REAL_CLASS,
    MANIP_FAKE_CLASS,
    MANIP_REAL_THRESHOLD,
)

logger = logging.getLogger(__name__)

_model = None
_device = None

_transform = T.Compose([
    T.Resize((MANIP_INPUT_SIZE, MANIP_INPUT_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=MANIP_MEAN, std=MANIP_STD),
])


class CLIPDeepfakeClassifier(nn.Module):
    """
    Matches the architecture of clip_ckpt_best.pth:
      backbone = CLIPVisionModel (ViT-L/14, embed_dim=1024)
      head     = Linear(1024, 2)
    Wrapped in DataParallel during training → keys prefixed 'module.'
    """

    def __init__(self):
        super().__init__()
        from transformers import CLIPVisionModel, CLIPVisionConfig
        # ViT-L/14 config matching the checkpoint
        config = CLIPVisionConfig(
            hidden_size=1024,
            intermediate_size=4096,
            num_hidden_layers=24,
            num_attention_heads=16,
            image_size=224,
            patch_size=14,
        )
        self.backbone = CLIPVisionModel(config)
        self.head = nn.Linear(1024, 2)

    def forward(self, x):
        outputs = self.backbone(pixel_values=x)
        # pooler_output = CLS token representation [B, 1024]
        features = outputs.pooler_output
        return self.head(features)


def _strip_module_prefix(state_dict: OrderedDict) -> OrderedDict:
    """Remove 'module.' prefix added by DataParallel."""
    new_sd = OrderedDict()
    for k, v in state_dict.items():
        new_key = k[len("module."):] if k.startswith("module.") else k
        new_sd[new_key] = v
    return new_sd


def _load_model():
    global _model, _device
    logger.info("[MANIPULATION] Loading CLIP deepfake model from %s", MANIPULATION_MODEL_PATH)
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    _model = CLIPDeepfakeClassifier().to(_device)

    state_dict = torch.load(MANIPULATION_MODEL_PATH, map_location=_device, weights_only=False)
    state_dict = _strip_module_prefix(state_dict)
    # strict=False: position_ids is saved as a persistent buffer in the checkpoint
    # but newer transformers registers it as non-persistent — harmless to skip.
    missing, unexpected = _model.load_state_dict(state_dict, strict=False)
    if missing:
        logger.warning("[MANIPULATION] Missing keys: %s", missing[:5])
    if unexpected:
        logger.info("[MANIPULATION] Ignored checkpoint-only keys: %s", unexpected[:5])
    _model.eval()
    logger.info("[MANIPULATION] CLIP model loaded on %s", _device)
    return _model, _device


def _get_model():
    global _model, _device
    if _model is None:
        _load_model()
    return _model, _device


def predict_manipulation(face_pil: Image.Image) -> dict:
    """
    Run deepfake/manipulation detection on a face crop.

    Args:
        face_pil: PIL Image (face crop)

    Returns:
        {
            "label": "REAL" | "FAKE",
            "score": float (confidence of predicted class),
            "real_score": float,
            "fake_score": float,
        }
    """
    model, device = _get_model()
    tensor = _transform(face_pil.convert("RGB")).unsqueeze(0).to(device)

    with torch.inference_mode():
        logits = model(tensor)           # [1, 2]
        probs = torch.softmax(logits, dim=-1)[0]  # [2]

    real_score = float(probs[MANIP_REAL_CLASS])
    fake_score = float(probs[MANIP_FAKE_CLASS])

    label = "REAL" if real_score >= MANIP_REAL_THRESHOLD else "FAKE"
    score = real_score if label == "REAL" else fake_score

    logger.info("[MANIPULATION] %s %.4f (real=%.4f fake=%.4f)", label, score, real_score, fake_score)
    return {
        "label": label,
        "score": round(score, 4),
        "real_score": round(real_score, 4),
        "fake_score": round(fake_score, 4),
    }
