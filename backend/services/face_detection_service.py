"""
services/face_detection_service.py

Face detection service using MediaPipe.
Detects faces in images and crops them for age estimation.
"""

import cv2
import numpy as np
from PIL import Image
from io import BytesIO


class FaceDetectionService:
    """Service for detecting and cropping faces from images."""
    
    def __init__(self, min_detection_confidence=0.5):
        """
        Initialize the face detection service using OpenCV Haar cascade.
        
        Args:
            min_detection_confidence: Minimum confidence for face detection (0.0-1.0)
        """
        self.min_detection_confidence = min_detection_confidence
        # Load Haar cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_and_crop_face(self, image_path_or_bytes, padding_ratio=0.2):
        """
        Detect face in image and return cropped face image using OpenCV Haar cascade.
        
        Args:
            image_path_or_bytes: Path to image file or image bytes
            padding_ratio: Padding around detected face (0.0-1.0)
            
        Returns:
            PIL.Image: Cropped face image, or None if no face detected
        """
        # Load image
        if isinstance(image_path_or_bytes, bytes):
            image = Image.open(BytesIO(image_path_or_bytes)).convert('RGB')
        else:
            image = Image.open(image_path_or_bytes).convert('RGB')
        
        # Convert to numpy array for OpenCV
        image_np = np.array(image)
        
        # Convert RGB to grayscale for Haar cascade
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            image_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return None
        
        # Get the largest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, width, height = largest_face
        
        # Add padding
        padding_x = int(width * padding_ratio)
        padding_y = int(height * padding_ratio)
        
        x = max(0, x - padding_x)
        y = max(0, y - padding_y)
        x2 = min(image_np.shape[1], x + width + 2 * padding_x)
        y2 = min(image_np.shape[0], y + height + 2 * padding_y)
        
        # Crop face
        face_crop = image_np[y:y2, x:x2]
        
        # Convert back to PIL Image
        face_image = Image.fromarray(face_crop)
        
        return face_image
    
    def detect_all_faces(self, image_path_or_bytes):
        """
        Detect all faces in image and return their bounding boxes using OpenCV Haar cascade.
        
        Args:
            image_path_or_bytes: Path to image file or image bytes
            
        Returns:
            list: List of tuples (x, y, width, height) for each detected face
        """
        # Load image
        if isinstance(image_path_or_bytes, bytes):
            image = Image.open(BytesIO(image_path_or_bytes)).convert('RGB')
        else:
            image = Image.open(image_path_or_bytes).convert('RGB')
        
        # Convert to numpy array for OpenCV
        image_np = np.array(image)
        
        # Convert RGB to grayscale for Haar cascade
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            image_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return [(x, y, width, height) for (x, y, width, height) in faces]


# Global instance
_face_detector = None


def get_face_detector():
    """Get or create the global face detector instance."""
    global _face_detector
    if _face_detector is None:
        _face_detector = FaceDetectionService()
    return _face_detector


def detect_and_crop_face(image_path_or_bytes, padding_ratio=0.2):
    """
    Convenience function to detect and crop face from image.
    
    Args:
        image_path_or_bytes: Path to image file or image bytes
        padding_ratio: Padding around detected face (0.0-1.0)
        
    Returns:
        PIL.Image: Cropped face image, or None if no face detected
    """
    detector = get_face_detector()
    return detector.detect_and_crop_face(image_path_or_bytes, padding_ratio)
