import torch
import torch.nn as nn
import torchvision.models as models
import timm


class AgeEstimationModel(nn.Module):
    def __init__(self, pretrained=True):
        super(AgeEstimationModel, self).__init__()
        
        # Load EfficientNet-B3 with pretrained weights (faster, lighter than ConvNeXt-Tiny)
        self.backbone = timm.create_model('efficientnet_b3', pretrained=pretrained, num_classes=0)
        
        # Add regression head
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


def get_model(pretrained=True):
    model = AgeEstimationModel(pretrained=pretrained)
    return model


if __name__ == '__main__':
    model = get_model(pretrained=True)
    
    # Print model architecture
    print(model)
    
    # Test with dummy input
    dummy_input = torch.randn(2, 3, 224, 224)
    output = model(dummy_input)
    print(f"\nInput shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
