"""
Worker State Manager

Responsibility:
--------------
Maintains persistent PPE state for each tracked worker across frames.
Handles temporary detection failures (occlusion, blur, bending) and ensures
stable state transitions. This is the CORE of the industrial-grade solution.

Key Features:
- Temporal smoothing with consecutive frame counters
- Stable state transitions (not frame-based)
- One stable state per worker at any time
- Ignores temporary missed detections
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class PPEState(Enum):
    """Worker PPE compliance states - exactly one state per worker"""
    SAFE = "Safe"
    NO_HELMET = "No Helmet"
    NO_VEST = "No Vest"
    NO_HELMET_NO_VEST = "No Helmet + No Vest"


@dataclass
class WorkerState:
    """
    Persistent state for a single tracked worker.
    
    Maintains frame-by-frame PPE detection history with counters
    to handle temporary missed detections robustly.
    """
    worker_id: int
    
    # Stable PPE state (starts as None = unknown, confirmed after threshold)
    has_helmet: Optional[bool] = None
    has_vest: Optional[bool] = None
    
    # Missing detection counters (increases when NOT detected)
    helmet_missing_count: int = 0
    vest_missing_count: int = 0
    
    # Present detection counters (increases when detected)
    helmet_present_count: int = 0
    vest_present_count: int = 0
    
    # Tracking metadata
    last_seen_frame: int = 0
    last_box: tuple = (0, 0, 0, 0)
    
    # State tracking (starts as None = uninitialized)
    current_state: Optional[PPEState] = None
    previous_state: Optional[PPEState] = None
    
    # Stabilization period - prevent alerts during first N frames
    frames_tracked: int = 0
    
    def __repr__(self):
        return (f"Worker({self.worker_id}) State={self.current_state.value if self.current_state else 'Unknown'} "
                f"Helmet={self.has_helmet} Vest={self.has_vest}")


class WorkerStateManager:
    """
    Manages persistent PPE states for ALL tracked workers.
    
    Industrial-grade behavior:
    - Workers maintain state across frames
    - Temporary missed detections are ignored
    - State only changes after N consecutive frames
    - One stable state per worker
    """
    
    def __init__(self,
                 missing_threshold: int = 12,
                 present_threshold: int = 25,
                 max_missing_frames: int = 90,
                 stabilization_frames: int = 30):
        """
        Args:
            missing_threshold: Consecutive frames PPE must be missing to mark as absent (default: 12)
            present_threshold: Consecutive frames PPE must be detected to mark as present (default: 25)
            max_missing_frames: Max frames worker can be untracked before removal (default: 90)
            stabilization_frames: Frames before worker state is considered stable (default: 30)
        """
        self.missing_threshold = missing_threshold
        self.present_threshold = present_threshold
        self.max_missing_frames = max_missing_frames
        self.stabilization_frames = stabilization_frames
        
        # All tracked workers {worker_id: WorkerState}
        self.workers = {}
    
    def update_worker(self,
                     worker_id: int,
                     frame_number: int,
                     box: tuple,
                     helmet_detected: bool,
                     vest_detected: bool) -> tuple:
        """
        Update worker's PPE state based on current frame detection.
        
        This is called ONCE per worker per frame with association results.
        
        Args:
            worker_id: Unique worker ID from tracker
            frame_number: Current frame number
            box: Bounding box (x1, y1, x2, y2)
            helmet_detected: Whether helmet was associated to this worker THIS frame
            vest_detected: Whether vest was associated to this worker THIS frame
            
        Returns:
            (current_state: PPEState, state_changed: bool, is_stabilized: bool)
        """
        # Initialize new worker
        if worker_id not in self.workers:
            self.workers[worker_id] = WorkerState(worker_id=worker_id)
        
        worker = self.workers[worker_id]
        
        # Update tracking metadata
        worker.last_seen_frame = frame_number
        worker.last_box = box
        worker.frames_tracked += 1
        
        # Store previous state before update
        previous_state = worker.current_state
        
        # Update helmet and vest states with temporal logic
        self._update_helmet_state(worker, helmet_detected)
        self._update_vest_state(worker, vest_detected)
        
        # Determine current stable PPE state
        new_state = self._determine_ppe_state(worker)
        
        # Only update if state has been determined
        if new_state is not None:
            worker.current_state = new_state
        
        # Detect state transition (only if both states are determined)
        state_changed = False
        if worker.current_state is not None and worker.previous_state is not None:
            state_changed = (worker.current_state != worker.previous_state)
        elif worker.current_state is not None and worker.previous_state is None:
            # First time state is determined
            state_changed = True
        
        # Check if worker has stabilized (been tracked long enough)
        is_stabilized = worker.frames_tracked >= self.stabilization_frames
        
        if state_changed and worker.current_state is not None:
            worker.previous_state = worker.current_state
        
        return worker.current_state, state_changed, is_stabilized
    
    def _update_helmet_state(self, worker: WorkerState, detected: bool):
        """
        Update helmet state with temporal smoothing.
        
        Logic:
        - If detected: increase present counter, reset missing counter
        - If NOT detected: increase missing counter, reset present counter
        - Confirm present after consecutive detections
        - Confirm missing after consecutive non-detections
        - Maintains None (unknown) until threshold met
        """
        if detected:
            # Helmet detected in THIS frame
            worker.helmet_present_count += 1
            worker.helmet_missing_count = 0
            
            # Confirm helmet present after consecutive detections
            if worker.helmet_present_count >= self.present_threshold:
                worker.has_helmet = True
        else:
            # Helmet NOT detected in THIS frame
            worker.helmet_missing_count += 1
            worker.helmet_present_count = 0
            
            # Confirm helmet missing after sustained absence
            if worker.helmet_missing_count >= self.missing_threshold:
                worker.has_helmet = False
    
    def _update_vest_state(self, worker: WorkerState, detected: bool):
        """
        Update vest state with temporal smoothing.
        
        Same logic as helmet - requires consecutive frames to confirm state.
        Maintains None (unknown) until threshold met.
        """
        if detected:
            # Vest detected in THIS frame
            worker.vest_present_count += 1
            worker.vest_missing_count = 0
            
            # Confirm vest present after consecutive detections
            if worker.vest_present_count >= self.present_threshold:
                worker.has_vest = True
        else:
            # Vest NOT detected in THIS frame
            worker.vest_missing_count += 1
            worker.vest_present_count = 0
            
            # Confirm vest missing after sustained absence
            if worker.vest_missing_count >= self.missing_threshold:
                worker.has_vest = False
    
    def _determine_ppe_state(self, worker: WorkerState) -> Optional[PPEState]:
        """
        Determine worker's current stable PPE state.
        
        Returns None if state not yet determined (early tracking).
        
        EXACTLY ONE state per worker (once determined):
        - Safe: has both helmet and vest
        - No Helmet: missing helmet only
        - No Vest: missing vest only
        - No Helmet + No Vest: missing both
        """
        # If either PPE status is still unknown, return None (not yet determined)
        if worker.has_helmet is None or worker.has_vest is None:
            return None
        
        # Both statuses are now determined
        if worker.has_helmet and worker.has_vest:
            return PPEState.SAFE
        elif not worker.has_helmet and not worker.has_vest:
            return PPEState.NO_HELMET_NO_VEST
        elif not worker.has_helmet:
            return PPEState.NO_HELMET
        else:  # not worker.has_vest
            return PPEState.NO_VEST
    
    def get_worker_state(self, worker_id: int) -> Optional[WorkerState]:
        """Get current state for a specific worker"""
        return self.workers.get(worker_id)
    
    def get_all_workers(self) -> dict:
        """Get all tracked workers"""
        return self.workers
    
    def get_active_worker_ids(self) -> set:
        """Get set of all currently tracked worker IDs"""
        return set(self.workers.keys())
    
    def cleanup_stale_workers(self, current_frame: int) -> list:
        """
        Remove workers that haven't been seen for too long.
        
        Returns:
            List of removed worker IDs
        """
        stale_workers = []
        
        for worker_id, worker in list(self.workers.items()):
            frames_since_seen = current_frame - worker.last_seen_frame
            if frames_since_seen > self.max_missing_frames:
                stale_workers.append(worker_id)
                del self.workers[worker_id]
        
        return stale_workers
    
    def get_statistics(self) -> dict:
        """Get statistics about tracked workers"""
        total = len(self.workers)
        safe = sum(1 for w in self.workers.values() if w.current_state == PPEState.SAFE)
        violations = total - safe
        
        state_counts = {
            PPEState.SAFE: 0,
            PPEState.NO_HELMET: 0,
            PPEState.NO_VEST: 0,
            PPEState.NO_HELMET_NO_VEST: 0
        }
        
        for worker in self.workers.values():
            state_counts[worker.current_state] += 1
        
        return {
            "total_workers": total,
            "safe_workers": safe,
            "workers_with_violations": violations,
            "state_breakdown": {
                "safe": state_counts[PPEState.SAFE],
                "no_helmet": state_counts[PPEState.NO_HELMET],
                "no_vest": state_counts[PPEState.NO_VEST],
                "no_helmet_no_vest": state_counts[PPEState.NO_HELMET_NO_VEST]
            }
        }
