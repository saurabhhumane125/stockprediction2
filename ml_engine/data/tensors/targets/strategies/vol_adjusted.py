import pandas as pd
import numpy as np
from typing import List, Tuple
from ml_engine.data.tensors.targets.base import BaseTargetStrategy
from ml_engine.data.tensors.targets.registry import StrategyRegistry

class VolatilityAdjustedTargetStrategy(BaseTargetStrategy):
    """
    Volatility-Adjusted Target Strategy.
    Target = Return_5d / Max(Vol_20d, Epsilon)
    Where Vol_20d is the rolling standard deviation of 1-day returns over 20 days.
    """
    
    @property
    def strategy_name(self) -> str:
        return "volatility_adjusted"
        
    @property
    def strategy_version(self) -> str:
        return "1.0"

    def get_target_cols(self, target_config: type) -> List[str]:
        """
        Returns the explicit list of target column names generated for the configuration.
        """
        return ["return_5d_vol_adj"]

    def generate(self, df: pd.DataFrame, target_config: type) -> Tuple[pd.DataFrame, List[str]]:
        """
        Applies the volatility-adjusted target logic to the DataFrame.
        """
        df = df.copy()
        
        target_cols = self.get_target_cols(target_config)
        target_col = target_cols[0]
        
        # Calculate 1-day returns for historical volatility (t-19 to t)
        df["daily_return"] = df["close"].pct_change(1)
        
        # Calculate Vol_20d using ddof=1 and min_periods=20
        df["vol_20d"] = df["daily_return"].rolling(window=20, min_periods=20).std(ddof=1)
        
        # Calculate Return_5d
        df["return_5d"] = (df["close"].shift(-5) - df["close"]) / df["close"]
        
        # Calculate Target = Return_5d / Max(Vol_20d, 1e-8)
        # We enforce a floor of 1e-8 on volatility to prevent divide-by-zero or extreme spikes.
        vol_clipped = np.clip(df["vol_20d"], 1e-8, np.inf)
        df[target_col] = df["return_5d"] / vol_clipped
        
        # Drop rows where target is NaN (due to either missing future return or missing past volatility)
        df = df.dropna(subset=[target_col])
        
        # Drop intermediate columns
        df = df.drop(columns=["daily_return", "vol_20d", "return_5d"])
        
        return df, target_cols

# Register the strategy
StrategyRegistry.register(VolatilityAdjustedTargetStrategy)
