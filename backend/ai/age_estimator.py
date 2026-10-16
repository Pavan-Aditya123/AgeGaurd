"""
ai/age_estimator.py

Age estimation using the trained ResNet18 model.
Model: backend/models/age_resnet18_best.pth

Verified specs (from checkpoint):
  - Architecture: torchvision ResNet18, fc = Linear(512, 1)
  - img_size: 224
  - mean: [0.485, 0.456, 0.406]  (ImageNet)
  - std:  [0.229, 0.224, 0.225]
  - Output: scalar age (float)
  - Checkpoint keys: model_name, model_state_dict, epoch, val_mae, img_size, mean, std

Loads model ONCE at startup.
"""

import logging
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image

from ai.config import (
    AGE_MODEL_PATH,
    AGE_INPUT_SIZE,
    AGE_MEAN,
    AGE_STD,
)

logger = logging.getLogger(__name__)

_model = None
_device = None

_transform = T.Compose([
    T.Resize((AGE_INPUT_SIZE, AGE_INPUT_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=AGE_MEAN, std=AGE_STD),
])


def _build_model() -> nn.Module:
    """Build ResNet18 with single-output regression head matching the checkpoint."""
    net = models.resnet18(weights=None)
    # Replace the standard 1000-class head with a regression head outputting 1 value
    net.fc = nn.Linear(512, 1)
    return net


def _load_model():
    global _model, _device
    logger.info("[AGE] Loading ResNet18 age model from %s", AGE_MODEL_PATH)
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    _model = _build_model().to(_device)
    checkpoint = torch.load(AGE_MODEL_PATH, map_location=_device, weights_only=False)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    _model.load_state_dict(state_dict)
    _model.eval()

    epoch = checkpoint.get("epoch", "?")
    val_mae = checkpoint.get("val_mae", "?")
    logger.info("[AGE] Model loaded (epoch=%s, val_mae=%s) on %s", epoch, val_mae, _device)
    return _model, _device


def _get_model():
    global _model, _device
    if _model is None:
        _load_model()
    return _model, _device


def predict_age(face_pil: Image.Image) -> float:
    """
    Predict age from a face PIL Image.

    Args:
        face_pil: PIL Image (face crop, already detected and quality-checked)

    Returns:
        float: Predicted age in years (clamped to 0–100)
    """
    model, device = _get_model()
    tensor = _transform(face_pil.convert("RGB")).unsqueeze(0).to(device)

    with torch.inference_mode():
        output = model(tensor)
        age = output.item()

    age = max(0.0, min(100.0, age))
    logger.info("[AGE] %.2f", age)
    return round(age, 2)
