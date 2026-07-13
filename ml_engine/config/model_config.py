from typing import Dict, Any


class ModelConfig:
    """
    Configuration for ML Model Architectures.
    """
    
    # GRU Settings
    GRU_HIDDEN_DIM: int = 64
    GRU_LAYERS: int = 2
    GRU_DROPOUT: float = 0.2
    
    # BiGRU Settings
    BIGRU_HIDDEN_DIM: int = 128
    BIGRU_LAYERS: int = 2
    BIGRU_DROPOUT: float = 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }


model_config = ModelConfig()
