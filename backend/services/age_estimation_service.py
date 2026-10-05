"""
services/age_estimation_service.py

Age estimation inference service using the trained EfficientNet-B3 model.
Loads the pre-trained model and provides age prediction for face images.
"""

import os
import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms as transforms
import timm

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "age_model.pth")

# ImageNet normalization (same as used during training)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Preprocessing transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
])


class AgeEstimationModel(nn.Module):
    """EfficientNet-B3 model with regression head (matches training architecture)."""
    def __init__(self, pretrained=False):
        super(AgeEstimationModel, self).__init__()
        self.backbone = timm.create_model('efficientnet_b3', pretrained=pretrained, num_classes=0)
        self.regressor = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(self.backbone.num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 1)
        )
    
    def forward(self, x):
        features = self.backbone(x)
        return self.regressor(features)


_model = None
_device = None


def _load_model():
    """Load the trained model from disk."""
    global _model, _device
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Age estimation model not found. Please place age_model.pth inside backend/models."
        )
    
    _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    _model = AgeEstimationModel(pretrained=False).to(_device)
    
    try:
        checkpoint = torch.load(MODEL_PATH, map_location=_device, weights_only=False)
    except TypeError:
        checkpoint = torch.load(MODEL_PATH, map_location=_device)

    state_dict = checkpoint.get("model_state_dict", checkpoint)
    _model.load_state_dict(state_dict)
    _model.eval()
    
    return _model, _device


def get_model():
    """Get the loaded model (lazy loading)."""
    global _model, _device
    if _model is None:
        _model, _device = _load_model()
    return _model, _device


def predict_age(image_path):
    """
    Predict age from a face image.
    
    Args:
        image_path: Path to the face image file
        
    Returns:
        float: Predicted age in years
        
    Raises:
        FileNotFoundError: If model file is missing
        Exception: If image processing or prediction fails
    """
    from services.face_detection_service import detect_and_crop_face
    
    model, device = get_model()
    
    # Detect and crop face from image
    face_image = detect_and_crop_face(image_path)
    
    if face_image is None:
        # Fallback: use original image if no face detected
        face_image = Image.open(image_path).convert('RGB')
    
    # Preprocess image
    image_tensor = transform(face_image).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        output = model(image_tensor)
        predicted_age = output.item()
    
    # Ensure age is non-negative
    predicted_age = max(0, predicted_age)
    
    return predicted_age


def predict_age_from_bytes(image_bytes):
    """
    Predict age from image bytes (useful for base64 decoded data).
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        float: Predicted age in years
    """
    from io import BytesIO
    from services.face_detection_service import detect_and_crop_face
    
    # Detect and crop face from image bytes
    face_image = detect_and_crop_face(image_bytes)
    
    if face_image is None:
        # Fallback: use original image if no face detected
        face_image = Image.open(BytesIO(image_bytes)).convert('RGB')
    
    image_tensor = transform(face_image).unsqueeze(0).to(get_model()[1])
    
    with torch.no_grad():
        output = get_model()[0](image_tensor)
        predicted_age = max(0, output.item())
    
    return predicted_age
