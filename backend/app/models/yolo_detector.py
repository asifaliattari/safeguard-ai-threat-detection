"""
YOLOv8 Object Detector
Simplified for MVP - Real-time detection
"""

from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict
import os


class YOLODetector:
    """YOLOv8 nano detector for real-time object detection"""

    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize YOLOv8 detector

        Args:
            model_path: Path to YOLOv8 weights (will auto-download if not found)
        """
        print(f"Loading YOLOv8 model from {model_path}...")

        # YOLOv8 will auto-download if model not found
        self.model = YOLO(model_path)

        # Dangerous objects to highlight
        self.dangerous_classes = {
            'knife', 'scissors', 'gun', 'rifle',
            'baseball bat', 'fire', 'flame'
        }

        print("YOLOv8 model loaded successfully!")

    def detect(self, frame: np.ndarray, confidence: float = 0.4) -> List[Dict]:
        """
        Run detection on a single frame

        Args:
            frame: Input image as numpy array (BGR format)
            confidence: Minimum confidence threshold

        Returns:
            List of detections with format:
            {
                'type': 'person',
                'confidence': 0.85,
                'bbox': [x1, y1, x2, y2],
                'timestamp': time.time()
            }
        """
        import time

        # Run inference
        results = self.model.predict(
            frame,
            conf=confidence,
            verbose=False,  # Suppress output
            device='cpu'    # Use CPU for MVP (GPU optional)
        )

        detections = []

        # Process results
        if len(results) > 0:
            result = results[0]

            # Extract boxes
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    # Get class ID and name
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]

                    # Get confidence
                    conf = float(box.conf[0])

                    # Get bounding box (xyxy format)
                    bbox = box.xyxy[0].cpu().numpy().tolist()

                    detections.append({
                        'type': class_name,
                        'confidence': conf,
                        'bbox': bbox,
                        'timestamp': time.time()
                    })

        return detections

    def is_dangerous(self, detection: Dict) -> bool:
        """Check if detection is a dangerous object"""
        obj_type = detection['type'].lower()
        return any(dangerous in obj_type for dangerous in self.dangerous_classes)


# Global detector instance (loaded once)
_detector = None


def get_detector() -> YOLODetector:
    """Get or create global detector instance"""
    global _detector

    if _detector is None:
        _detector = YOLODetector()

    return _detector
