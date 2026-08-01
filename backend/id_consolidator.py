"""
ID Consolidator - Maps multiple tracking IDs to the same physical person.

This handles tracking instabilities where the same person gets different IDs.
"""

import numpy as np


class IDConsolidator:
    """
    Consolidates tracking IDs that likely belong to the same person.
    Uses both IoU and spatial proximity for more aggressive consolidation.
    """
    
    def __init__(self, iou_threshold=0.2, distance_threshold=150, max_frames_gap=10):
        """
        Args:
            iou_threshold: IoU threshold to consider boxes as same person
            distance_threshold: Maximum distance (pixels) between box centers to merge
            max_frames_gap: Maximum frames a person can disappear before being considered new
        """
        self.iou_threshold = iou_threshold
        self.distance_threshold = distance_threshold
        self.max_frames_gap = max_frames_gap
        
        # Map: tracking_id -> consolidated_id
        self.id_mapping = {}
        
        # Track last seen frame and box for each consolidated ID
        # consolidated_id -> {"frame": int, "box": tuple, "tracking_ids": set, "center": tuple, "is_active": bool}
        self.consolidated_persons = {}
        
        # Current frame counter
        self.frame_count = 0
        
        # Next consolidated ID to assign
        self.next_consolidated_id = 1
        
        # Track which consolidated IDs are active in current frame (to prevent merging simultaneously visible people)
        self.active_in_current_frame = set()
    
    def calculate_iou(self, box1, box2):
        """Calculate IoU between two boxes."""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2

        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)

        union_area = box1_area + box2_area - intersection_area

        if union_area == 0:
            return 0.0

        return intersection_area / union_area
    
    def calculate_distance(self, center1, center2):
        """Calculate Euclidean distance between two centers."""
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def get_center(self, box):
        """Get center point of a box."""
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def start_new_frame(self):
        """
        Call this at the start of each frame to reset frame-level tracking.
        """
        self.frame_count += 1
        self.active_in_current_frame.clear()
    
    def get_consolidated_id(self, tracking_id, box):
        """
        Get the consolidated ID for a tracking ID and box.
        
        CRITICAL: This method prevents merging two tracking IDs that are simultaneously
        visible in the same frame. Consolidation only applies to stale IDs being re-linked
        to new IDs that appear later.
        
        Args:
            tracking_id: Original tracking ID from tracker
            box: Bounding box (x1, y1, x2, y2)
        
        Returns:
            consolidated_id: Integer representing the consolidated person ID
        """
        
        # Calculate box center
        center = self.get_center(box)
        
        # If we've seen this tracking ID before, use its consolidated ID
        if tracking_id in self.id_mapping:
            consolidated_id = self.id_mapping[tracking_id]
            
            # Update the consolidated person info
            if consolidated_id in self.consolidated_persons:
                self.consolidated_persons[consolidated_id]["frame"] = self.frame_count
                self.consolidated_persons[consolidated_id]["box"] = box
                self.consolidated_persons[consolidated_id]["center"] = center
                self.consolidated_persons[consolidated_id]["tracking_ids"].add(tracking_id)
                self.consolidated_persons[consolidated_id]["is_active"] = True
            
            # Mark this consolidated ID as active in current frame
            self.active_in_current_frame.add(consolidated_id)
            
            return consolidated_id
        
        # New tracking ID - check if it matches any existing consolidated person
        # STRICT: Only consider consolidated persons that are NOT currently active in this frame
        best_match_id = None
        best_score = 0.0
        
        for cons_id, info in list(self.consolidated_persons.items()):
            # STRICT CHECK: Skip if this consolidated person is already active in current frame
            # This prevents merging two simultaneously visible people
            if cons_id in self.active_in_current_frame:
                continue
            
            # Skip if too old (person has been gone for too many frames)
            if self.frame_count - info["frame"] > self.max_frames_gap:
                continue
            
            # Calculate IoU with last known box
            iou = self.calculate_iou(box, info["box"])
            
            # Calculate distance between centers
            distance = self.calculate_distance(center, info["center"])
            
            # Use a combined score: IoU + distance proximity
            # High IoU or close distance indicates same person
            score = 0.0
            
            if iou >= self.iou_threshold:
                score = iou
            elif distance <= self.distance_threshold:
                # Convert distance to a score (closer = higher score)
                score = max(0, 1.0 - (distance / self.distance_threshold))
            
            if score > best_score and score > 0.2:
                best_score = score
                best_match_id = cons_id
        
        if best_match_id is not None:
            # Found a match - map this tracking ID to existing consolidated ID
            consolidated_id = best_match_id
            self.id_mapping[tracking_id] = consolidated_id
            self.consolidated_persons[consolidated_id]["frame"] = self.frame_count
            self.consolidated_persons[consolidated_id]["box"] = box
            self.consolidated_persons[consolidated_id]["center"] = center
            self.consolidated_persons[consolidated_id]["tracking_ids"].add(tracking_id)
            self.consolidated_persons[consolidated_id]["is_active"] = True
        else:
            # No match found - create new consolidated ID
            consolidated_id = self.next_consolidated_id
            self.next_consolidated_id += 1
            
            self.id_mapping[tracking_id] = consolidated_id
            self.consolidated_persons[consolidated_id] = {
                "frame": self.frame_count,
                "box": box,
                "center": center,
                "tracking_ids": {tracking_id},
                "is_active": True
            }
        
        # Mark this consolidated ID as active in current frame
        self.active_in_current_frame.add(consolidated_id)
        
        return consolidated_id
    
    def cleanup_old_persons(self):
        """
        Remove consolidated persons that haven't been seen recently.
        Also mark all persons as inactive (will be marked active again in next frame if they appear).
        """
        to_remove = []
        
        # Mark all persons as inactive
        for cons_id, info in self.consolidated_persons.items():
            info["is_active"] = False
            
            # Check if should be removed
            if self.frame_count - info["frame"] > self.max_frames_gap:
                to_remove.append(cons_id)
        
        for cons_id in to_remove:
            # Remove the consolidated person
            tracking_ids = self.consolidated_persons[cons_id]["tracking_ids"]
            del self.consolidated_persons[cons_id]
            
            # Remove ID mappings
            for tid in tracking_ids:
                if tid in self.id_mapping:
                    del self.id_mapping[tid]
    
    def get_stats(self):
        """Get statistics about ID consolidation."""
        return {
            "total_tracking_ids": len(self.id_mapping),
            "consolidated_persons": len(self.consolidated_persons),
            "current_frame": self.frame_count
        }
