from typing import Dict, Any

class EvaluationConfig:
    """
    Configuration properties strictly for model evaluation and artifact generation.
    """
    
    # Classification Thresholds
    DECISION_THRESHOLD: float = 0.5
    
    # Plotting Settings
    PLOT_DPI: int = 300
    PLOT_STYLE: str = "seaborn-v0_8-whitegrid"
    COLOR_PALETTE: str = "viridis"
    
    # Advanced Metric Configuration
    NUM_CALIBRATION_BINS: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }

evaluation_config = EvaluationConfig()
