import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split
import glob


class UTKFaceDataset(Dataset):
    def __init__(self, image_paths, transform=None):
        self.image_paths = image_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        
        # Parse age from filename: age_gender_race_timestamp.jpg
        filename = os.path.basename(image_path)
        age = int(filename.split('_')[0])
        
        if self.transform:
            image = self.transform(image)
        
        return image, age


def get_data_splits(data_dir, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    image_paths = glob.glob(os.path.join(data_dir, '*.jpg')) + glob.glob(os.path.join(data_dir, '*.chip.jpg'))
    
    # Ensure ratios sum to 1
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"
    
    # First split: train vs (val + test)
    train_paths, temp_paths = train_test_split(
        image_paths, 
        train_size=train_ratio, 
        random_state=42
    )
    
    # Second split: val vs test
    val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
    val_paths, test_paths = train_test_split(
        temp_paths, 
        train_size=val_ratio_adjusted, 
        random_state=42
    )
    
    print(f"Total images: {len(image_paths)}")
    print(f"Train: {len(train_paths)}")
    print(f"Validation: {len(val_paths)}")
    print(f"Test: {len(test_paths)}")
    
    return train_paths, val_paths, test_paths


def get_transforms():
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]
    
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std)
    ])
    
    val_test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std)
    ])
    
    return train_transform, val_test_transform


def get_dataloaders(data_dir, batch_size=32, num_workers=4, pin_memory=True):
    train_paths, val_paths, test_paths = get_data_splits(data_dir)
    train_transform, val_test_transform = get_transforms()
    
    train_dataset = UTKFaceDataset(train_paths, transform=train_transform)
    val_dataset = UTKFaceDataset(val_paths, transform=val_test_transform)
    test_dataset = UTKFaceDataset(test_paths, transform=val_test_transform)
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=True
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=True
    )
    
    test_loader = DataLoader(
        test_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=True
    )
    
    return train_loader, val_loader, test_loader


if __name__ == '__main__':
    data_dir = 'backend/datasets/UTKFace'
    train_loader, val_loader, test_loader = get_dataloaders(data_dir, batch_size=32)
    
    print(f"Train batches: {len(train_loader)}")
    print(f"Validation batches: {len(val_loader)}")
    print(f"Test batches: {len(test_loader)}")
