"""
Alert Manager

Responsibility:
--------------
Manages alert generation based on worker state transitions.

Key Principle: ONE alert per worker EVER (strictest policy)

Rules:
1. Alert when worker FIRST transitions to ANY violation state
2. NEVER alert again for that worker, regardless of state changes
3. Alert cleared only when worker leaves tracking entirely
"""

import time
from typing import Optional
from worker_state import PPEState


class AlertManager:
    """
    Manages alert generation with STRICT one-alert-per-worker policy.
    
    Once a worker has been alerted, they will NEVER trigger another alert
    until they leave the scene and return (new tracking ID).
    """

    def __init__(self):
        # Track which workers have EVER been alerted
        # worker_id -> {
        #     "first_violation_state": PPEState,
        #     "alert_time": float,
        # }
        self.alerted_workers = {}

    def should_alert(self, worker_id: int, current_state: Optional[PPEState], state_changed: bool, is_stabilized: bool) -> bool:
        """
        Determine if alert should be created.
        
        STRICT RULE: One alert per worker, ever.
        
        Alert Rules:
        1. Worker state must be determined (not None)
        2. Worker is in violation state (not Safe)
        3. Worker has NEVER been alerted before  
        4. Worker state has stabilized
        5. Either state just changed OR this is first stabilized violation frame
        
        Args:
            worker_id: Worker's tracking ID
            current_state: Worker's current stable PPE state (can be None)
            state_changed: Whether state just changed this frame
            is_stabilized: Whether worker has been tracked long enough
            
        Returns:
            bool: True if alert should be generated (ONLY ONCE per worker)
        """
        
        # Check if this worker has already been alerted
        if worker_id in self.alerted_workers:
            # Already alerted - NEVER alert again
            return False
        
        # State not yet determined - wait
        if current_state is None:
            return False
        
        # Worker is Safe - no alert
        if current_state == PPEState.SAFE:
            return False
        
        # Worker must be stabilized before alerting
        if not is_stabilized:
            return False
        
        # Worker has a violation, is stabilized, and hasn't been alerted
        # Alert on first stable violation detection
        self.alerted_workers[worker_id] = {
            "first_violation_state": current_state,
            "alert_time": time.time()
        }
        return True
    
    def get_violation_text(self, state: PPEState) -> str:
        """Convert PPEState to violation text for database"""
        return state.value
    
    def cleanup_stale_workers(self, active_worker_ids: set):
        """
        Remove alerts for workers no longer being tracked.
        This allows them to trigger new alert if they return with different ID.
        
        Args:
            active_worker_ids: Set of currently active worker IDs
        """
        stale_workers = [
            worker_id for worker_id in self.alerted_workers.keys()
            if worker_id not in active_worker_ids
        ]
        
        for worker_id in stale_workers:
            del self.alerted_workers[worker_id]
    
    def get_statistics(self) -> dict:
        """Get alert statistics"""
        return {
            "total_workers_alerted": len(self.alerted_workers)
        }