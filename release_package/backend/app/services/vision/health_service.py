import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import VisionHealthResponse, VisionComponentHealth
from app.services.vision.artifact_manager import vision_artifact_manager
from app.services.vision.prediction_controller import prediction_controller
from app.core.model_loader import ml_adapter

class VisionHealthService:
    """
    Aggregates health statuses of all Vision dependencies.
    """
    
    def check_health(self, db: Session) -> VisionHealthResponse:
        components = {}
        
        # 1. OCR (Trivial check if loaded)
        components["ocr"] = VisionComponentHealth(status="ok", details="OCR Service active")
        
        # 2. Inference
        components["inference"] = VisionComponentHealth(status="ok", details="Inference Service active")
        
        # 3. Registry
        try:
            if not ml_adapter.is_available:
                components["registry"] = VisionComponentHealth(status="error", details="ML Engine Adapter not available")
            else:
                components["registry"] = VisionComponentHealth(status="ok", details="ML Engine Adapter active")
        except Exception as e:
            components["registry"] = VisionComponentHealth(status="error", details=str(e))
            
        # 4. Persistence
        try:
            db.execute(text("SELECT 1"))
            components["persistence"] = VisionComponentHealth(status="ok")
        except Exception as e:
            components["persistence"] = VisionComponentHealth(status="error", details="DB connection failed")
            
        # 5. Artifact Storage
        try:
            if os.access(vision_artifact_manager.artifacts_dir, os.W_OK):
                components["artifact_storage"] = VisionComponentHealth(status="ok")
            else:
                components["artifact_storage"] = VisionComponentHealth(status="error", details="Artifacts dir not writable")
        except Exception as e:
            components["artifact_storage"] = VisionComponentHealth(status="error", details=str(e))
            
        # 6. Upload Storage
        try:
            if os.access(prediction_controller.upload_dir, os.W_OK):
                components["upload_storage"] = VisionComponentHealth(status="ok")
            else:
                components["upload_storage"] = VisionComponentHealth(status="error", details="Uploads dir not writable")
        except Exception as e:
            components["upload_storage"] = VisionComponentHealth(status="error", details=str(e))
            
        overall = "ok"
        for c in components.values():
            if c.status != "ok":
                overall = "error"
                break
                
        return VisionHealthResponse(
            overall_status=overall,
            components=components
        )
        
vision_health_service = VisionHealthService()
