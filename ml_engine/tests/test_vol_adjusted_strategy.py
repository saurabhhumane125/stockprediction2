import pytest
import pandas as pd
import numpy as np
from ml_engine.data.tensors.targets.strategies.vol_adjusted import VolatilityAdjustedTargetStrategy
from ml_engine.inference.decoders.vol_adjusted_decoder import VolatilityAdjustedInferenceDecoder
from ml_engine.data.tensors.targets.manager import TargetManager

class DummyTargetConfig:
    def __init__(self):
        self.strategy_name = "volatility_adjusted"
        self.strategy_version = "1.0"

class DummyConfig:
    def __init__(self):
        self.target = DummyTargetConfig()

def test_volatility_adjusted_target_math():
    # 25 days of data to allow 20 day rolling + 5 day future shift
    # Make a price series that goes up exactly 1% every day
    # So close = 100 * (1.01)^t
    prices = [100 * (1.01)**i for i in range(30)]
    df = pd.DataFrame({"close": prices})
    
    config = DummyConfig()
    strategy = VolatilityAdjustedTargetStrategy()
    df_out, target_cols = strategy.generate(df, config.target)
    
    assert target_cols == ["return_5d_vol_adj"]
    assert "return_5d_vol_adj" in df_out.columns
    
    # 20 days min period means first 20 rows are NaN. Future 5 days shift means last 5 rows are NaN.
    # Total valid rows = 30 - 20 - 5 = 5 (indices 20 to 24)
    assert len(df_out) == 5
    
    # Check Math for index 20
    # Returns are constant at ~0.01. So std is 0. 
    # Target should be return_5d / epsilon
    # return_5d = (close[25] - close[20]) / close[20] = 1.01^5 - 1 ~ 0.051
    # vol_20d is 0, clipped to 1e-8.
    # So target is huge. 
    target = df_out.loc[20, "return_5d_vol_adj"]
    assert target > 1000 # Due to 1e-8 epsilon scaling
    
    # Let's test with a non-zero vol series
    np.random.seed(42)
    returns = np.random.normal(0, 0.02, 30)
    prices2 = [100]
    for r in returns:
        prices2.append(prices2[-1] * (1 + r))
        
    df2 = pd.DataFrame({"close": prices2})
    df_out2, _ = strategy.generate(df2, config.target)
    
    idx = 22
    ret_5d = (prices2[idx+5] - prices2[idx]) / prices2[idx]
    
    # manual vol
    daily_rets = pd.Series(prices2).pct_change(1)
    vol = daily_rets.iloc[idx-19:idx+1].std(ddof=1)
    
    expected = ret_5d / vol
    np.testing.assert_almost_equal(df_out2.loc[idx, "return_5d_vol_adj"], expected)

def test_volatility_adjusted_decoder():
    decoder = VolatilityAdjustedInferenceDecoder()
    
    # 21 days of prices
    prices = [100 * (1.02)**i for i in range(21)]
    # Feature 0 is something else, Feature 1 is close
    features = np.zeros((21, 2))
    features[:, 1] = prices
    
    metadata = {"features": {"order": ["other", "close"]}, "strategy_name": "volatility_adjusted", "strategy_version": "1.0"}
    
    raw_prediction = 2.5 # meaning expected return is 2.5 * vol
    
    decoded = decoder.decode(raw_prediction, features, metadata)
    
    # Volatility should be 0 (constant 2% return) -> clipped to 1e-8
    assert decoded["calculated_vol_20d"] < 1e-10
    
    unscaled = decoded["predicted_value"]
    np.testing.assert_almost_equal(unscaled, 2.5 * 1e-8)
