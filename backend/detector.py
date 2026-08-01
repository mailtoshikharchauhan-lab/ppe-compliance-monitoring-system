"""
PPE Detector - Main Pipeline Orchestrator

Responsibility:
--------------
Coordinates all components to process video frames:
1. Tracking (tracker.py)
2. PPE Association (association.py)
3. Worker State Management (worker_state.py)
4. Alert Generation (alert_manager.py)

This is the ONLY module that ties everything together.
Clean architecture with single responsibility for each module.
"""

import os
import cv2

from tracker import PPETracker
from association import PPEAssociator
from worker_state import WorkerStateManager, PPEState
from alert_manager import AlertManager
from id_consolidator import IDConsolidator
from database import insert_alert
from utils import extract_detections, draw_box, get_timestamp, resize_frame


class PPEDetector:
    """
    Industrial-grade PPE compliance monitoring system.
    
    Pipeline:
    1. Track persons in frame (YOLO + BoT-SORT)
    2. Detect helmets and vests
    3. Associate PPE to persons (Hungarian algorithm)
    4. Update persistent worker states (temporal smoothing)
    5. Generate alerts on state transitions
    6. Display annotated frame
    """

    def __init__(self, model_path):
        """
        Initialize all pipeline components.
        
        Args:
            model_path: Path to trained YOLO model
        """
        # Component 1: Tracking
        self.tracker = PPETracker(model_path)
        
        # Component 1.5: ID Consolidation (balanced - prevent false merges while handling re-IDs)
        self.id_consolidator = IDConsolidator(
            iou_threshold=0.15,      # Moderate IoU requirement
            distance_threshold=200,  # Moderate distance (allow some movement)
            max_frames_gap=120       # Allow re-identification within 4 seconds
        )
        
        # Component 2: Association
        self.associator = PPEAssociator()
        
        # Component 3: Worker State Management (very conservative on PPE presence)
        self.state_manager = WorkerStateManager(
            missing_threshold=12,   # Faster to confirm missing (12 frames = 0.4s)
            present_threshold=25,   # VERY slow to confirm present (25 frames = 0.8s) - strict
            max_missing_frames=90,  # Keep worker in memory for 90 frames (3 seconds)
            stabilization_frames=30 # Alert after 30 frames (1 second) of stable state
        )
        
        # Component 4: Alert Management
        self.alert_manager = AlertManager()
        
        # Ensure screenshots directory exists
        os.makedirs("screenshots", exist_ok=True)

    def process_video(self, video_path):
        """
        Process entire video through the PPE detection pipeline.
        
        Args:
            video_path: Path to input video file
            
        Returns:
            dict: Processing statistics
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
        
        frame_count = 0
        total_alerts = 0
        
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(video_path)}")
        print(f"{'='*60}\n")
        
        while True:
            success, frame = cap.read()
            
            if not success:
                break
            
            frame_count += 1
            
            # Keep clean copy for screenshots
            clean_frame = frame.copy()
            
            # ============================================
            # STEP 1: Track persons and detect PPE items
            # ============================================
            result = self.tracker.track(frame)
            
            persons, helmets, vests = extract_detections(
                result,
                self.tracker.model.names
            )
            
            # ============================================
            # STEP 2: Associate PPE to persons with ID consolidation
            # ============================================
            # Start new frame for ID consolidator
            self.id_consolidator.start_new_frame()
            
            # Build person list for association with consolidated IDs
            persons_for_association = []
            for person in persons:
                tracking_id = person.get("id")
                if tracking_id is not None:
                    # Get consolidated ID (maps unstable tracking IDs to stable worker IDs)
                    worker_id = self.id_consolidator.get_consolidated_id(
                        tracking_id,
                        person["box"]
                    )
                    
                    persons_for_association.append({
                        "id": worker_id,  # Use consolidated ID
                        "box": person["box"],
                        "confidence": person.get("confidence", 0)
                    })
            
            # Perform association
            association_results = self.associator.associate_ppe(
                persons_for_association,
                helmets,
                vests
            )
            
            # ============================================
            # STEP 3: Update worker states
            # ============================================
            for person_id, ppe_data in association_results.items():
                # Update worker state with current frame detections
                current_state, state_changed, is_stabilized = self.state_manager.update_worker(
                    worker_id=person_id,
                    frame_number=frame_count,
                    box=ppe_data['box'],
                    helmet_detected=ppe_data['helmet_detected'],
                    vest_detected=ppe_data['vest_detected']
                )
                
                # ============================================
                # STEP 4: Generate alerts on state transitions
                # ============================================
                if self.alert_manager.should_alert(
                    person_id, 
                    current_state, 
                    state_changed,
                    is_stabilized
                ):
                    # State changed to a violation - generate alert
                    violation_text = self.alert_manager.get_violation_text(current_state)
                    timestamp = get_timestamp()
                    
                    # Create screenshot filename
                    image_name = f"{person_id}_{timestamp.replace(':', '').replace(' ', '_').replace('-', '')}.jpg"
                    image_path = os.path.join("screenshots", image_name)
                    
                    # Prepare screenshot frame
                    screenshot_frame = clean_frame.copy()
                    
                    # Draw box on violating worker
                    frame_height, frame_width = screenshot_frame.shape[:2]
                    x1, y1, x2, y2 = ppe_data['box']
                    
                    # Ensure box is within bounds
                    x1 = max(0, min(int(x1), frame_width))
                    x2 = max(0, min(int(x2), frame_width))
                    y1 = max(0, min(int(y1), frame_height))
                    y2 = max(0, min(int(y2), frame_height))
                    
                    validated_box = (x1, y1, x2, y2)
                    
                    # Draw violation on screenshot
                    draw_box(
                        screenshot_frame,
                        validated_box,
                        (0, 0, 255),  # Red
                        f"Worker {person_id} | {violation_text}"
                    )
                    
                    # Save screenshot
                    cv2.imwrite(image_path, screenshot_frame)
                    
                    # Insert alert to database
                    insert_alert(timestamp, violation_text, image_name)
                    
                    total_alerts += 1
                    
                    print(f"[ALERT {total_alerts}] Frame {frame_count} | Worker {person_id} | {violation_text}")
            
            # ============================================
            # STEP 5: Cleanup stale workers
            # ============================================
            # Cleanup ID consolidator
            self.id_consolidator.cleanup_old_persons()
            
            # Cleanup worker state manager
            removed_workers = self.state_manager.cleanup_stale_workers(frame_count)
            if removed_workers:
                # Also cleanup from alert manager
                active_ids = self.state_manager.get_active_worker_ids()
                self.alert_manager.cleanup_stale_workers(active_ids)
            
            # ============================================
            # STEP 6: Draw annotations on display frame
            # ============================================
            for person_id, ppe_data in association_results.items():
                worker_state = self.state_manager.get_worker_state(person_id)
                
                if worker_state is None:
                    continue
                
                # Determine color and label based on current stable state
                current_state = worker_state.current_state
                
                # Handle undetermined state (still tracking)
                if current_state is None:
                    color = (128, 128, 128)  # Gray
                    label = f"Worker {person_id} | Tracking..."
                elif current_state == PPEState.SAFE:
                    color = (0, 255, 0)  # Green
                    label = f"Worker {person_id} | Safe"
                elif current_state == PPEState.NO_HELMET:
                    color = (0, 165, 255)  # Orange (BGR)
                    label = f"Worker {person_id} | No Helmet"
                elif current_state == PPEState.NO_VEST:
                    color = (0, 255, 255)  # Yellow (BGR)
                    label = f"Worker {person_id} | No Vest"
                else:  # NO_HELMET_NO_VEST
                    color = (0, 0, 255)  # Red
                    label = f"Worker {person_id} | No Helmet + No Vest"
                
                # Draw bounding box
                draw_box(frame, ppe_data['box'], color, label)
            
            # Display frame info
            cv2.putText(
                frame,
                f"Frame: {frame_count} | Workers: {len(association_results)} | Alerts: {total_alerts}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            # Show frame
            display = resize_frame(frame)
            cv2.imshow("PPE Compliance Monitoring", display)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Total Frames: {frame_count}")
        print(f"Total Alerts: {total_alerts}")
        print(f"{'='*60}\n")
        
        return {
            "total_alerts": total_alerts,
            "frames_processed": frame_count
        }
