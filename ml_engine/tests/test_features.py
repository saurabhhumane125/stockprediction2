import pandas as pd
import numpy as np
import pytest

from ml_engine.data.features.generator import FeatureGenerator


@pytest.fixture
def clean_dataframe():
    # 60 periods to allow indicators like EMA50 to compute properly
    periods = 60
    dates = pd.date_range("2023-01-01", periods=periods, freq="D")
    
    # Generate some synthetic trend data
    close = np.linspace(100, 150, periods) + np.sin(np.linspace(0, 10, periods)) * 5
    high = close + 2
    low = close - 2
    open_p = close - 1
    vol = np.random.randint(1000, 5000, periods)
    
    df = pd.DataFrame({
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": vol
    }, index=dates)
    return df


def test_feature_generator_execution(clean_dataframe):
    generator = FeatureGenerator()
    df_feat = generator.generate_all_features(clean_dataframe)
    
    # Check that rows with NaNs (due to lookback periods like EMA50) were dropped
    assert len(df_feat) < len(clean_dataframe)
    
    # Check that no NaNs remain
    assert df_feat.isna().sum().sum() == 0
    
    # Ensure all approved features are present
    expected_features = [
        "daily_return", "ema_short", "ema_long", "rsi", 
        "macd_line", "macd_signal", "macd_histogram",
        "bb_upper", "bb_lower", "bb_width",
        "atr", "adx", "roc", "momentum", "volatility", "volume_change"
    ]
    for feat in expected_features:
        assert feat in df_feat.columns
        
    # Check metadata was generated
    assert len(generator.metadata) > 0
    meta_names = [m["feature_name"] for m in generator.metadata]
    for feat in expected_features:
        assert feat in meta_names


def test_individual_rsi(clean_dataframe):
    generator = FeatureGenerator()
    df = generator.add_rsi(clean_dataframe.copy(), period=14)
    assert "rsi" in df.columns
    # RSI for a strong uptrend should be generally > 50
    assert df["rsi"].iloc[-1] > 50


def test_individual_macd(clean_dataframe):
    generator = FeatureGenerator()
    df = generator.add_macd(clean_dataframe.copy(), 12, 26, 9)
    assert "macd_line" in df.columns
    assert "macd_signal" in df.columns
    assert "macd_histogram" in df.columns


def test_individual_bb(clean_dataframe):
    generator = FeatureGenerator()
    df = generator.add_bollinger_bands(clean_dataframe.copy(), 20, 2.0)
    assert "bb_upper" in df.columns
    assert "bb_width" in df.columns
    # Upper band > lower band
    assert (df["bb_upper"].dropna() > df["bb_lower"].dropna()).all()
