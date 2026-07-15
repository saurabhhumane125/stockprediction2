import pytest
from app.services.vision.lifecycle_manager import vision_lifecycle_manager
from app.schemas import VisionLifecycleState

def test_vision_lifecycle_manager_transition():
    trace_id = "lifecycle_test_123"
    
    # 1. UPLOADED
    vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.UPLOADED, {"filename": "img.png"})
    
    assert vision_lifecycle_manager.get_state(trace_id) == VisionLifecycleState.UPLOADED
    ctx = vision_lifecycle_manager.get_context(trace_id)
    assert ctx["filename"] == "img.png"
    
    # 2. FEATURE_GENERATION
    vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.FEATURE_GENERATION, {"time": 100})
    
    assert vision_lifecycle_manager.get_state(trace_id) == VisionLifecycleState.FEATURE_GENERATION
    ctx = vision_lifecycle_manager.get_context(trace_id)
    # Context should merge
    assert ctx["filename"] == "img.png"
    assert ctx["time"] == 100
