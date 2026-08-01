"""
PPE Association Module

Responsibility:
--------------
Match helmets and vests to tracked persons using Hungarian algorithm.

Returns ONLY the association results - no state management or alert logic.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment


class PPEAssociator:
    """
    Associates helmets and vests to tracked persons using optimal assignment.
    
    Uses Hungarian algorithm with cost function combining:
    - IoU (overlap)
    - Euclidean distance
    - ROI constraints (helmets in head region, vests in torso)
    """
    
    def __init__(self):
        # Body region definitions (percentage of person box)
        self.head_height = 0.40  # Top 40% for head
        self.torso_start = 0.25  # Torso starts at 25% from top
        self.torso_end = 0.80    # Torso ends at 80% from top
        
        # Cost function weights
        self.iou_weight = 0.5
        self.distance_weight = 0.3
        self.roi_weight = 0.2
        
        # Maximum acceptable matching cost
        self.max_cost_helmet = 0.7
        self.max_cost_vest = 0.7
    
    def associate_ppe(self, persons: list, helmets: list, vests: list) -> dict:
        """
        Associate PPE items to persons.
        
        Args:
            persons: List of person detections with 'id' and 'box'
            helmets: List of helmet detections with 'box'
            vests: List of vest detections with 'box'
        
        Returns:
            dict: {
                person_id: {
                    'helmet_detected': bool,
                    'vest_detected': bool,
                    'box': tuple
                }
            }
        """
        if not persons:
            return {}
        
        # Match helmets to persons
        helmet_matches = self._match_ppe_to_persons(
            persons,
            helmets,
            self._get_head_region,
            self.max_cost_helmet
        )
        
        # Match vests to persons
        vest_matches = self._match_ppe_to_persons(
            persons,
            vests,
            self._get_torso_region,
            self.max_cost_vest
        )
        
        # Build results
        results = {}
        for idx, person in enumerate(persons):
            person_id = person['id']
            results[person_id] = {
                'helmet_detected': helmet_matches[idx] is not None,
                'vest_detected': vest_matches[idx] is not None,
                'box': person['box']
            }
        
        return results
    
    def _match_ppe_to_persons(self,
                              persons: list,
                              ppe_items: list,
                              region_func,
                              max_cost: float) -> dict:
        """
        Perform optimal one-to-one matching using Hungarian algorithm.
        
        Returns:
            dict: {person_idx: ppe_idx or None}
        """
        if not persons or not ppe_items:
            return {i: None for i in range(len(persons))}
        
        n_persons = len(persons)
        n_ppe = len(ppe_items)
        
        # Build cost matrix
        cost_matrix = np.full((n_persons, n_ppe), 1e9)
        
        for person_idx, person in enumerate(persons):
            person_box = person['box']
            region = region_func(person_box)
            
            for ppe_idx, ppe_item in enumerate(ppe_items):
                ppe_box = ppe_item['box']
                cost = self._calculate_cost(ppe_box, region, person_box)
                cost_matrix[person_idx, ppe_idx] = cost
        
        # Apply Hungarian algorithm
        person_indices, ppe_indices = linear_sum_assignment(cost_matrix)
        
        # Build result with cost filtering
        matches = {i: None for i in range(n_persons)}
        
        for person_idx, ppe_idx in zip(person_indices, ppe_indices):
            if cost_matrix[person_idx, ppe_idx] <= max_cost:
                matches[person_idx] = ppe_idx
        
        return matches
    
    def _calculate_cost(self, ppe_box: tuple, region_box: tuple, person_box: tuple) -> float:
        """
        Calculate matching cost between PPE and person region.
        Lower cost = better match.
        """
        # IoU component (inverted: 1 - IoU)
        iou = self._calculate_iou(ppe_box, region_box)
        iou_cost = 1.0 - iou
        
        # Distance component (normalized by person size)
        ppe_center = self._get_center(ppe_box)
        region_center = self._get_center(region_box)
        distance = self._euclidean_distance(ppe_center, region_center)
        
        # Normalize by person diagonal
        x1, y1, x2, y2 = person_box
        person_diagonal = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        normalized_distance = distance / (person_diagonal + 1e-6)
        distance_cost = min(normalized_distance, 1.0)
        
        # ROI constraint (penalize if PPE center outside region)
        roi_cost = 0.0 if self._point_in_box(ppe_center, region_box) else 1.0
        
        # Weighted combination
        total_cost = (
            self.iou_weight * iou_cost +
            self.distance_weight * distance_cost +
            self.roi_weight * roi_cost
        )
        
        return total_cost
    
    def _get_head_region(self, person_box: tuple) -> tuple:
        """Get head region (top portion of person box)"""
        x1, y1, x2, y2 = person_box
        width = x2 - x1
        height = y2 - y1
        
        return (
            x1 + int(width * 0.15),
            y1,
            x2 - int(width * 0.15),
            y1 + int(height * self.head_height)
        )
    
    def _get_torso_region(self, person_box: tuple) -> tuple:
        """Get torso region (middle portion of person box)"""
        x1, y1, x2, y2 = person_box
        width = x2 - x1
        height = y2 - y1
        
        return (
            x1 + int(width * 0.05),
            y1 + int(height * self.torso_start),
            x2 - int(width * 0.05),
            y1 + int(height * self.torso_end)
        )
    
    @staticmethod
    def _calculate_iou(box1: tuple, box2: tuple) -> float:
        """Calculate Intersection over Union"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def _get_center(box: tuple) -> tuple:
        """Get center point of box"""
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    @staticmethod
    def _euclidean_distance(point1: tuple, point2: tuple) -> float:
        """Calculate Euclidean distance"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    @staticmethod
    def _point_in_box(point: tuple, box: tuple) -> bool:
        """Check if point is inside box"""
        px, py = point
        x1, y1, x2, y2 = box
        return x1 <= px <= x2 and y1 <= py <= y2