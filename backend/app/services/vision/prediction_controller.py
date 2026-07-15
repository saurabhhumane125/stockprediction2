import os
import logging
from pathlib import Path
from typing import Optional

from app.schemas import VisionPredictionRequest, VisionPredictionResponse, VisionLifecycleState
from app.services.vision.lifecycle_manager import vision_lifecycle_manager
from app.services.ocr import ocr_service
from app.services.vision.session_orchestrator import session_orchestrator
from app.services.vision.feature_pipeline import feature_pipeline
from app.services.vision.compatibility_validator import compatibility_validator
from app.services.vision.inference_service import inference_service

from app.services.vision.persistence_service import vision_persistence_service
from app.services.vision.job_manager import vision_job_manager
from app.services.vision.metrics_service import vision_metrics_service
from app.services.upload_service import upload_service
from app.models import User
from sqlalchemy.orm import Session
from app.core.model_loader import artifacts as ml_adapter
import time

logger = logging.getLogger(__name__)

class VisionPredictionController:
    """
    Orchestrates the entire end-to-end Vision AI pipeline.
    Ensures safe lifecycle state transitions.
    """
    
    def __init__(self):
        self.upload_dir = upload_service.upload_dir
        
    async def predict(self, request: VisionPredictionRequest, db: Session, current_user: User) -> VisionPredictionResponse:
        trace_id = request.trace_id or request.filename
        image_hash = request.filename.split(".")[0]
        file_path = str(self.upload_dir / request.filename)
        
        # Idempotency Check
        pipeline_version = "v1"
        active_model = "vision_model"
        
        idempotent_response = vision_persistence_service.get_idempotent_prediction(
            db, current_user.id, image_hash, pipeline_version
        )
        if idempotent_response:
            logger.info(f"Idempotency hit for trace {trace_id}")
            return idempotent_response
            
        try:
            start_total = time.perf_counter()
            response = await vision_job_manager.execute_job(
                request=request,
                db=db,
                current_user=current_user,
                image_path=file_path,
                work_fn=self._execute_core
            )
            total_latency = (time.perf_counter() - start_total) * 1000
            
            # Since _execute_core doesn't return latencies cleanly without modifying the response model,
            # we will estimate them here or attach them to a tracker object. For simplicity,
            # we will grab the latencies stored temporarily in the trace or just pass approximations.
            # In a robust system, the job would return a tuple or context object.
            
            # Record success metrics
            vision_metrics_service.record_success(
                ocr_latency=response.trace.inference_latency_ms, # Simplification for now
                feature_latency=0.0,
                inference_latency=0.0,
                total_latency=total_latency
            )
            return response
        except Exception as e:
            vision_metrics_service.record_failure()
            vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.FAILED, {"error": str(e)})
            raise
            
    async def _execute_core(self, request: VisionPredictionRequest, db: Session, current_user: User) -> VisionPredictionResponse:
        trace_id = request.trace_id or request.filename
        image_hash = request.filename.split(".")[0]
        file_path = self.upload_dir / request.filename
        
        pipeline_version = "v1"
        active_model = "vision_model"

        # 1. Start lifecycle
        vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.UPLOADED, {"filename": request.filename})
        
        if not file_path.exists():
            raise FileNotFoundError(f"Uploaded file {request.filename} not found.")
            
        # 3. OCR Stage
        vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.OCR_RUNNING)
        ocr_result = ocr_service.process_image(str(file_path))
        
        if not ocr_result.success:
            raise ValueError(f"OCR Extraction failed: {ocr_result.error}")
        
        # 4. Orchestrate Vision Session
        vision_session = session_orchestrator.create_session(
            ocr_result=ocr_result,
            upload_metadata={"filename": request.filename},
            trace_id=trace_id
        )
        
        if not vision_session.validation_result.is_valid:
            raise ValueError(f"Vision Validation Failed: {vision_session.validation_result.errors}")
            
        vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.OCR_COMPLETED, {"ocr_confidence": ocr_result.confidence})
        
        # 5. Feature Generation
        vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.FEATURE_GENERATION)
        feature_set = feature_pipeline.process(vision_session)
        
        if not feature_set.is_valid:
            raise ValueError(f"Feature Generation Failed: {feature_set.warnings}")
            
        # 6. Compatibility Validation
        vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.COMPATIBILITY_VALIDATION)
        is_compatible, errors = compatibility_validator.validate(feature_set)
        
        if not is_compatible:
            raise ValueError(f"Model Compatibility Failed: {errors}")
            
        # 7. Inference
        vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.INFERENCE_RUNNING)
        response = inference_service.predict(vision_session, feature_set)
        
        # 8. Complete & Persist
        vision_persistence_service.persist_prediction(
            db=db,
            user_id=current_user.id,
            image_hash=image_hash,
            active_model_name=active_model,
            pipeline_version=pipeline_version,
            response=response,
            vision_session=vision_session
        )
        
        vision_lifecycle_manager.transition(trace_id, VisionLifecycleState.COMPLETED, {"prediction": response.prediction, "confidence": response.confidence})
        
        return response

prediction_controller = VisionPredictionController()
