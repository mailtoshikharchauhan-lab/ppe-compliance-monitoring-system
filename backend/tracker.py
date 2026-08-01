"""
PPE Tracker

Responsibility:
--------------
1. Load YOLO model
2. Run object detection on frames
3. Assign stable tracking IDs using BoT-SORT

This module ONLY handles tracking, not PPE association or state management.
"""

from ultralytics import YOLO


class PPETracker:
    """
    YOLO + BoT-SORT Tracker
    
    Provides stable person tracking across frames.
    """

    def __init__(self, model_path):
        """
        Initialize YOLO model for detection and tracking.
        
        Args:
            model_path: Path to trained YOLO model weights
        """
        self.model = YOLO(model_path)

    def track(self, frame):
        """
        Run detection and tracking on a single frame.
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            YOLO result object with detections and tracking IDs
        """
        results = self.model.track(
            source=frame,
            
            # Tracking persistence
            persist=True,
            tracker="botsort.yaml",
            
            # Detection thresholds
            conf=0.25,  # Lower to detect more helmets/vests
            iou=0.40,   # NMS threshold
            
            # Max detections per frame
            max_det=20,  # Support up to 20 persons in frame
            
            verbose=False
        )

        return results[0]