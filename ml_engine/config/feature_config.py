from typing import Dict, Any


class FeatureConfig:
    """
    Configuration for technical indicators and feature engineering.
    All parameters are abstracted here to allow hyperparameter tuning later.
    """
    
    # RSI Parameters
    RSI_PERIOD: int = 14
    
    # MACD Parameters
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    
    # EMA Parameters
    EMA_SHORT: int = 20
    EMA_LONG: int = 50
    
    # Bollinger Bands Parameters
    BB_PERIOD: int = 20
    BB_STD_DEV: float = 2.0
    
    # ATR Parameters
    ATR_PERIOD: int = 14
    
    # ROC Parameters
    ROC_PERIOD: int = 10
    
    # Momentum Parameters
    MOMENTUM_PERIOD: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }


feature_config = FeatureConfig()
