"""
Probe the CLIP checkpoint's class mapping by testing on known real photos.
The checkpoint was trained for deepfake detection — we need to determine
which output index (0 or 1) corresponds to REAL vs FAKE.
Run: python backend/scripts/probe_clip_classes.py
"""
import sys, os, torch
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image
from collections import OrderedDict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from transformers import CLIPVisionModel, CLIPVisionConfig

CKPT = os.path.join(os.path.dirname(__file__), "..", "models", "clip_ckpt_best.pth")
UPLOADS = os.path.join(os.path.dirname(__file__), "..", "uploads")

config = CLIPVisionConfig(
    hidden_size=1024, intermediate_size=4096,
    num_hidden_layers=24, num_attention_heads=16,
    image_size=224, patch_size=14,
)

class Clf(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = CLIPVisionModel(config)
        self.head = nn.Linear(1024, 2)
    def forward(self, x):
        return self.head(self.backbone(pixel_values=x).pooler_output)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Clf().to(device)
sd = torch.load(CKPT, map_location=device, weights_only=False)
clean = OrderedDict((k[7:] if k.startswith("module.") else k, v) for k, v in sd.items())
model.load_state_dict(clean, strict=False)
model.eval()

transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize([0.48145466, 0.4578275, 0.40821073],
                [0.26862954, 0.26130258, 0.27577711]),
])

uploads = sorted([
    f for f in os.listdir(UPLOADS)
    if f.endswith(".jpg") and "_face" not in f and "gitkeep" not in f
])

print("Image | logit[0] | logit[1] | softmax[0] | softmax[1]")
print("-" * 70)

for fname in uploads[:6]:
    path = os.path.join(UPLOADS, fname)
    img = Image.open(path).convert("RGB")
    t = transform(img).unsqueeze(0).to(device)
    with torch.inference_mode():
        logits = model(t)[0]
        probs = torch.softmax(logits, dim=-1)
    print(f"{fname[:30]:30s}  {logits[0].item():+.3f}  {logits[1].item():+.3f}  "
          f"{probs[0].item():.4f}  {probs[1].item():.4f}")

print()
print("These are REAL photos from a phone camera.")
print("The higher-scoring class = REAL")
print("Head weight shape:", list(sd.values())[-2].shape)  # head.weight
