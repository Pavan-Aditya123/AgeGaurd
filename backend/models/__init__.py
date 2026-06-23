"""
models/

This package will hold AI model wrappers in future phases:

  Phase 5: age_estimator.py
    - Loads ResNet18 trained on UTKFace dataset
    - Provides predict_age(image_bytes) -> int

  Phase 4: liveness_detector.py
    - Wraps MediaPipe face mesh
    - Provides check_liveness(frame_bytes) -> bool
"""
