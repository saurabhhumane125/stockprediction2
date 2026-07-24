import pandas as pd
from ml_engine.inference.decoders.base import BaseInferenceDecoder
from ml_engine.inference.decoders.registry import DecoderRegistry

from typing import Dict, Any
import numpy as np

class VolatilityAdjustedInferenceDecoder(BaseInferenceDecoder):
    """
    Volatility-Adjusted Inference Decoder.
    Reverses the scaling to return absolute expected returns.
    """
    
    @property
    def strategy_name(self) -> str:
        return "volatility_adjusted"
        
    @property
    def strategy_version(self) -> str:
        return "1.0"

    def decode(self, raw_prediction: float, current_features: np.ndarray, metadata: dict, calibrator: Any = None) -> Dict[str, Any]:
        """
        Un-scales the predicted volatility-adjusted return to actual return.
        current_features is expected to be a 2D numpy array containing the raw features for the sequence.
        """
        result = {}
        
        raw_val = float(raw_prediction) if isinstance(raw_prediction, (float, int, np.floating, np.integer)) else float(raw_prediction[0])
        
        vol_20d = None
        
        # current_features is a 2D numpy array of shape (sequence_length, feature_count).
        # We need the close prices to compute rolling volatility.
        # The target strategy calculates 20-day volatility requiring 20 days of returns.
        # Since 1-day returns consume 1 price data point, we strictly require a sequence length >= 21.
        if current_features.shape[0] < 21:
            from ml_engine.core.exceptions import ConfigurationError
            raise ConfigurationError(
                f"VolatilityAdjustedInferenceDecoder requires SEQUENCE_LENGTH >= 21 to compute Vol_20d. "
                f"Received sequence of length {current_features.shape[0]}."
            )
            
        feature_names = metadata.get("features", {}).get("order", [])
        if "close" in feature_names:
            close_idx = feature_names.index("close")
            close_prices = current_features[:, close_idx]
            close_series = pd.Series(close_prices)
            daily_returns = close_series.pct_change(1)
            # Use exactly 20 days of returns to match the target strategy math perfectly.
            last_20_returns = daily_returns.iloc[-20:]
            vol_20d = last_20_returns.std(ddof=1)
        
        if vol_20d is None or pd.isna(vol_20d):
            raise ValueError("VolatilityAdjustedInferenceDecoder failed to compute Vol_20d. Ensure 'close' feature is present.")
            
        vol_clipped = max(vol_20d, 1e-8)
        unscaled_return = raw_val * vol_clipped
        
        result["predicted_value"] = unscaled_return
        result["raw_vol_adj_prediction"] = raw_val
        result["calculated_vol_20d"] = vol_20d
        
        return result

# Register the decoder
DecoderRegistry.register(VolatilityAdjustedInferenceDecoder)
