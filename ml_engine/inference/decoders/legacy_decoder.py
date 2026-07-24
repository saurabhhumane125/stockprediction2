import pandas as pd
from ml_engine.inference.decoders.base import BaseInferenceDecoder
from ml_engine.inference.decoders.registry import DecoderRegistry

from typing import Dict, Any
import numpy as np

class LegacyInferenceDecoder(BaseInferenceDecoder):
    """
    Legacy Inference Decoder.
    Returns raw predictions untouched, maintaining backward compatibility for existing models.
    """
    
    @property
    def strategy_name(self) -> str:
        return "legacy"
        
    @property
    def strategy_version(self) -> str:
        return "1.0"

    def decode(self, raw_prediction: float, current_features: pd.Series, metadata: dict, calibrator: Any = None) -> Dict[str, Any]:
        """
        Legacy target output was raw numbers (e.g. floats representing exact % return).
        No un-scaling is required. Returns dictionary matching old PredictionDecoder.
        """
        from ml_engine.core.types import TaskType
        task_type_str = metadata.get("task_type", "BINARY_CLASSIFICATION")
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            task_type = TaskType.BINARY_CLASSIFICATION

        if isinstance(raw_prediction, (float, int, np.floating, np.integer)):
            raw_logits = np.array([raw_prediction])
        else:
            raw_logits = np.array(raw_prediction)
            
        result = {}
        
        if task_type == TaskType.BINARY_CLASSIFICATION:
            raw = float(raw_logits[0])
            calibrated = raw # Default
            if calibrator:
                if hasattr(calibrator, "predict_proba"):
                    calibrated = float(calibrator.predict_proba(raw_logits.reshape(-1, 1))[:, 1][0])
                else:
                    calibrated = float(calibrator.predict(raw_logits)[0])
            
            result["predicted_class"] = 1 if calibrated >= 0.5 else 0
            result["probability"] = calibrated
            result["raw_logit"] = raw
            
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
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

# Register the decoder
DecoderRegistry.register(LegacyInferenceDecoder)
