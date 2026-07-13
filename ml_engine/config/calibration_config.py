from typing import Dict, Any

class CalibrationConfig:
    """
    Configuration properties strictly for probability calibration.
    """
    
    # ECE Calculation
    NUM_BINS: int = 10
    
    # Isotonic Regression Settings
    ISOTONIC_OUT_OF_BOUNDS: str = "clip"
    
    # Plotting Settings
    PLOT_DPI: int = 300
    PLOT_STYLE: str = "seaborn-v0_8-whitegrid"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }

calibration_config = CalibrationConfig()
