import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.schemas import VisionLifecycleState

logger = logging.getLogger(__name__)

class VisionLifecycleManager:
    """
    Manages state transitions and provides structured audit logging for the Vision Prediction pipeline.
    Ready for future async migrations (e.g., Celery/Redis).
    """
    def __init__(self):
        # In-memory dictionary for current offline state tracking.
        # Future state: migrate to Redis or Postgres table.
        self._state_store: Dict[str, VisionLifecycleState] = {}
        self._context_store: Dict[str, Dict[str, Any]] = {}

    def transition(self, trace_id: str, new_state: VisionLifecycleState, details: Optional[Dict[str, Any]] = None):
        """
        Transition a trace_id to a new state and emit an audit log.
        """
        old_state = self._state_store.get(trace_id, None)
        self._state_store[trace_id] = new_state
        
        if details is None:
            details = {}
            
        if trace_id not in self._context_store:
            self._context_store[trace_id] = {}
            
        self._context_store[trace_id].update(details)
        
        # Structured Audit Log
        audit_log = {
            "trace_id": trace_id,
            "event": "lifecycle_transition",
            "old_state": old_state.value if old_state else None,
            "new_state": new_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        logger.info(f"AUDIT_LOG: {audit_log}")

    def get_state(self, trace_id: str) -> Optional[VisionLifecycleState]:
        """
        Retrieve current state for a trace_id.
        """
        return self._state_store.get(trace_id)
        
    def get_context(self, trace_id: str) -> Dict[str, Any]:
        """
        Retrieve execution context for a trace_id.
        """
        return self._context_store.get(trace_id, {})

vision_lifecycle_manager = VisionLifecycleManager()
