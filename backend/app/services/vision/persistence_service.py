import logging
import json
from sqlalchemy.orm import Session
from typing import Optional, Tuple

from app.models import VisionPredictionHistory
from app.schemas import VisionPredictionResponse, VisionSession, VisionInferenceTrace
from app.services.vision.artifact_manager import vision_artifact_manager

logger = logging.getLogger(__name__)

class VisionPersistenceService:
    """
    Handles Database inserts and Idempotency logic for Vision AI.
    """
    
    def get_idempotent_prediction(
        self,
        db: Session,
        user_id: int,
        image_hash: str,
        pipeline_version: str
    ) -> Optional[VisionPredictionResponse]:
        """
        Looks for an exact match of user_id, image_hash and pipeline_version.
        If found, retrieves the PredictionResponse.
        """
        history = (
            db.query(VisionPredictionHistory)
            .filter_by(
                user_id=user_id,
                image_hash=image_hash,
                pipeline_version=pipeline_version
            )
            .order_by(VisionPredictionHistory.created_at.desc())
            .first()
        )
        
        if not history:
            return None
            
        # Reconstruct Response
        trace = VisionInferenceTrace(
            request_id="IDEMPOTENT_HIT",
            vision_session_id=history.pipeline_version,
            feature_hash=history.feature_hash or "recovered-hash",
            model_version=history.model_version or "unknown",
            registry_version=history.registry_version or "unknown",
            calibration_version=history.calibration_version or "unknown",
            prediction_timestamp=str(history.created_at),
            inference_latency_ms=0.0
        )
        
        return VisionPredictionResponse(
            trace=trace,
            prediction=history.prediction,
            confidence=history.confidence,
            probability_buy=None,
            probability_sell=None,
            class_id=None,
            stock=history.prediction # For backward compat or dummy
        )

    def persist_prediction(
        self,
        db: Session,
        user_id: int,
        image_hash: str,
        active_model_name: str,
        pipeline_version: str,
        response: VisionPredictionResponse,
        vision_session: VisionSession
    ) -> VisionPredictionHistory:
        """
        Writes the prediction history into the DB and saves large JSON files to disk.
        """
        
        # 1. Save massive JSON traces to disk
        vision_artifact_manager.save_artifacts(
            image_hash=image_hash,
            vision_session=vision_session,
            inference_trace=response.trace
        )
        
        # 2. Write to DB
        history = VisionPredictionHistory(
            user_id=user_id,
            image_hash=image_hash,
            active_model=active_model_name,
            pipeline_version=pipeline_version,
            prediction=response.prediction,
            confidence=response.confidence,
            ocr_version=None,
            feature_generator_version=None,
            sequence_builder_version=None,
            registry_version=response.trace.registry_version,
            model_version=response.trace.model_version,
            calibration_version=response.trace.calibration_version,
            hash_algorithm="SHA256",
            prediction_version="v1",
            feature_hash=response.trace.feature_hash,
            ocr_output_json=json.dumps(vision_session.ocr_metadata.model_dump()),
            vision_session_json=None, # Already persisted as file
            inference_trace_json=None # Already persisted as file
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return history
        
vision_persistence_service = VisionPersistenceService()
