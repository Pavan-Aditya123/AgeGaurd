import torch
import torch.nn as nn
from tqdm import tqdm
import math


def evaluate_model(model, data_loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_predictions = []
    all_targets = []
    
    with torch.no_grad():
        pbar = tqdm(data_loader, desc='Evaluating')
        for images, ages in pbar:
            images = images.to(device)
            ages = ages.float().unsqueeze(1).to(device)
            
            outputs = model(images)
            loss = criterion(outputs, ages)
            
            running_loss += loss.item()
            
            all_predictions.extend(outputs.cpu().numpy().flatten())
            all_targets.extend(ages.cpu().numpy().flatten())
    
    # Calculate metrics
    avg_loss = running_loss / len(data_loader)
    
    all_predictions = torch.tensor(all_predictions)
    all_targets = torch.tensor(all_targets)
    
    # MAE (Mean Absolute Error)
    mae = torch.mean(torch.abs(all_predictions - all_targets)).item()
    
    # RMSE (Root Mean Square Error)
    mse = torch.mean((all_predictions - all_targets) ** 2).item()
    rmse = math.sqrt(mse)
    
    return avg_loss, mae, rmse


def evaluate_from_checkpoint(model_path, data_dir, batch_size=32):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load data
    from training.dataset import get_dataloaders
    _, _, test_loader = get_dataloaders(data_dir, batch_size=batch_size)
    
    # Load model
    from training.model import get_model
    model = get_model(pretrained=False).to(device)
    
    checkpoint = torch.load(model_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    print(f"Loaded checkpoint from epoch {checkpoint['epoch']}")
    
    # Evaluate
    criterion = nn.MSELoss()
    test_loss, test_mae, test_rmse = evaluate_model(model, test_loader, criterion, device)
    
    print(f"\nTest Results:")
    print(f"Loss: {test_loss:.4f}")
    print(f"MAE: {test_mae:.4f}")
    print(f"RMSE: {test_rmse:.4f}")
    
    return test_loss, test_mae, test_rmse


if __name__ == '__main__':
    model_path = 'models/age_model.pth'
    data_dir = 'datasets/UTKFace'
    
    evaluate_from_checkpoint(model_path, data_dir, batch_size=32)
