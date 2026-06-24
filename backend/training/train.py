import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import autocast, GradScaler
from tqdm import tqdm
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.dataset import get_dataloaders
from training.model import get_model
from training.evaluate import evaluate_model


def train_epoch(model, train_loader, criterion, optimizer, device, scaler):
    model.train()
    running_loss = 0.0
    
    pbar = tqdm(train_loader, desc='Training')
    for images, ages in pbar:
        images = images.to(device, non_blocking=True)
        ages = ages.float().unsqueeze(1).to(device, non_blocking=True)
        
        optimizer.zero_grad()
        
        if scaler is not None:
            with autocast('cuda'):
                outputs = model(images)
                loss = criterion(outputs, ages)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, ages)
            loss.backward()
            optimizer.step()
        
        running_loss += loss.item()
        pbar.set_postfix({'loss': loss.item()})
    
    return running_loss / len(train_loader)


def train_model(data_dir, num_epochs=20, batch_size=32, learning_rate=1e-4, save_path='models/age_model.pth'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Enable cudnn benchmark for optimized conv operations
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
    
    # Create save directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Load data with pin_memory enabled for GPU
    print("Loading data...")
    use_pin_memory = torch.cuda.is_available()
    train_loader, val_loader, test_loader = get_dataloaders(data_dir, batch_size=batch_size, pin_memory=use_pin_memory)
    
    # Initialize model
    print("Initializing model...")
    model = get_model(pretrained=True).to(device)
    
    # Loss function
    criterion = nn.MSELoss()
    
    # Optimizer
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)
    
    # AMP scaler for mixed precision training
    scaler = GradScaler('cuda') if torch.cuda.is_available() else None
    
    # Training loop
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch + 1}/{num_epochs}")
        print("-" * 50)
        
        # Train
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device, scaler)
        print(f"Training Loss: {train_loss:.4f}")
        
        # Validate
        val_loss, val_mae, val_rmse = evaluate_model(model, val_loader, criterion, device)
        print(f"Validation Loss: {val_loss:.4f}")
        print(f"Validation MAE: {val_mae:.4f}")
        print(f"Validation RMSE: {val_rmse:.4f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_mae': val_mae,
                'val_rmse': val_rmse
            }, save_path)
            print(f"Best model saved to {save_path}")
    
    print("\nTraining completed!")
    print(f"Best validation loss: {best_val_loss:.4f}")
    
    # Load best model and evaluate on test set
    print("\nEvaluating on test set...")
    checkpoint = torch.load(save_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    test_loss, test_mae, test_rmse = evaluate_model(model, test_loader, criterion, device)
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test MAE: {test_mae:.4f}")
    print(f"Test RMSE: {test_rmse:.4f}")
    
    return model


if __name__ == '__main__':
    data_dir = 'datasets/UTKFace'
    save_path = 'models/age_model.pth'
    
    train_model(
        data_dir=data_dir,
        num_epochs=20,
        batch_size=32,
        learning_rate=1e-4,
        save_path=save_path
    )
