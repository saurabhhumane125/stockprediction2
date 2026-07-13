from typing import Dict, Any


class TrainingConfig:
    """
    Configuration for dataset building, splitting, and training loops.
    """
    
    # Dataset generation
    SEQUENCE_LENGTH: int = 48
    FORECAST_HORIZON: int = 1
    
    # Target definition (e.g., threshold for a BUY classification)
    RETURN_THRESHOLD_BPS: float = 0.0  # 0 basis points (strictly positive return)
    
    # Temporal splitting (Years based, or fraction)
    # E.g., 2014-01-01 to 2021-12-31 for Train
    TRAIN_END_DATE: str = "2021-12-31"
    VAL_END_DATE: str = "2023-06-30"
    
    # Training Loop
    BATCH_SIZE: int = 64
    EPOCHS: int = 100
    EARLY_STOPPING_PATIENCE: int = 15
    LEARNING_RATE: float = 1e-3
    
    # Model Architecture
    OPTIMIZER: str = "adam"
    DROPOUT: float = 0.2
    HIDDEN_SIZE: int = 64
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }


training_config = TrainingConfig()
