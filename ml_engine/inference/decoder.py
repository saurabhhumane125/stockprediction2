import numpy as np
from typing import Dict, Any, Union, List
from ml_engine.core.types import TaskType

class PredictionDecoder:
    """
    Production Prediction Decoder layer.
    Decouples raw logic output processing from the backend Decision Engine.
    """

    @staticmethod
    def decode(raw_logits: Union[np.ndarray, float], task_type: TaskType, calibrator: Any = None) -> Dict[str, Any]:
        """
        Converts raw model predictions into a structured dictionary payload.
        """
        # Ensure it's a numpy array
        if isinstance(raw_logits, (float, int, np.floating, np.integer)):
            raw_logits = np.array([raw_logits])
            
        result = {}
        
        if task_type == TaskType.BINARY_CLASSIFICATION:
            raw = float(raw_logits[0])
            calibrated = raw # Default
            if calibrator:
                if hasattr(calibrator, "predict_proba"):
                    calibrated = float(calibrator.predict_proba(raw_logits.reshape(-1, 1))[:, 1][0])
                else:
                    calibrated = float(calibrator.predict(raw_logits)[0])
            
            # Usually we use 0.5 as threshold, but if backend uses inference_config, we do it there?
            # Or we just return probs and let decision engine decide.
            # But prompt says "PredictionDecoder only returns predictions" and "PredictionDecoder responsibilities: Binary -> Probability"
            result["predicted_class"] = 1 if calibrated >= 0.5 else 0
            result["probability"] = calibrated
            result["raw_logit"] = raw
            
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
            # Assuming raw_logits is [C]
            probs = np.exp(raw_logits) / np.sum(np.exp(raw_logits), axis=-1, keepdims=True)
            pred_class = int(np.argmax(probs))
            result["predicted_class"] = pred_class
            result["class_probabilities"] = probs.tolist()
            result["raw_logits"] = raw_logits.tolist()
            
        elif task_type == TaskType.REGRESSION:
            val = float(raw_logits[0])
            result["predicted_value"] = val
            
        elif task_type == TaskType.MULTI_OUTPUT_REGRESSION:
            result["predicted_values"] = raw_logits.tolist()
            
        else:
            result["raw"] = raw_logits.tolist()
            
        return result
