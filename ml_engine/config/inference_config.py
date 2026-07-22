from typing import Dict, Any

class InferenceConfig:
    """
    Configuration properties strictly for the Inference Engine.
    """
    
    # Class Decision Threshold
    DECISION_THRESHOLD: float = 0.5
    
    # Feature Input Dimensions
    MAX_BATCH_SIZE: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }

inference_config = InferenceConfig()
