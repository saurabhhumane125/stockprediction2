import logging
import time
from datetime import datetime
import numpy as np

from app.schemas import VisionSession, VisionFeatureSet, VisionInferenceTrace, VisionPredictionResponse
from app.core.model_loader import ml_adapter

logger = logging.getLogger(__name__)

class VisionInferenceService:
    def predict(self, session: VisionSession, feature_set: VisionFeatureSet) -> VisionPredictionResponse:
        start_time = time.time()
        
        if not ml_adapter.is_available or not ml_adapter.inference_engine:
            raise RuntimeError("ProductionInferenceEngine is not available for Vision Inference.")
            
        if not feature_set.is_valid:
            raise ValueError(f"Cannot run inference on invalid feature set. Warnings: {feature_set.warnings}")

        try:
            # Ensure the feature array is 2D float
            features_array = np.array(feature_set.features, dtype=float)
            
            # Predict using the native ProductionInferenceEngine
            results = ml_adapter.inference_engine.predict(features_array)
            
            if not results:
                raise ValueError("Inference engine returned no predictions for the provided sequence.")
                
            latest_result = results[-1]
            
        except Exception as e:
            logger.error(f"Vision inference failed: {e}")
            raise ValueError(f"Vision inference failed: {str(e)}")
            
        latency_ms = (time.time() - start_time) * 1000.0
        
        # Build the immutable inference trace
        trace = VisionInferenceTrace(
            request_id=session.request_id,
            vision_session_id=session.request_id,
            feature_hash=feature_set.feature_hash,
            model_version=latest_result.get("Model Version", "unknown"),
            registry_version="v1",
            calibration_version="v1",
            prediction_timestamp=latest_result.get("Inference Timestamp", datetime.utcnow().isoformat()),
            inference_latency_ms=latency_ms
        )
        
        # Extract Prediction metrics
        pred_class_id = latest_result.get("Predicted Class", 0)
        prediction_str = "UP" if pred_class_id == 1 else "DOWN"
        
        prob = latest_result.get("Calibrated Probability", 0.0)
        prob_buy = prob
        prob_sell = 1.0 - prob
        
        stock_symbol = "UNKNOWN"
        if session.ocr_metadata and session.ocr_metadata.symbol and session.ocr_metadata.symbol.value:
            stock_symbol = session.ocr_metadata.symbol.value
            
        return VisionPredictionResponse(
            trace=trace,
            prediction=prediction_str,
            confidence=latest_result.get("Confidence", 0.0),
            probability_buy=prob_buy,
            probability_sell=prob_sell,
            class_id=pred_class_id,
            stock=stock_symbol
        )

inference_service = VisionInferenceService()
