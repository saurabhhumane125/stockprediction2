"""
ml_engine/data/tensors/utils.py
─────────────────────────────────────────────────────────────────────────────
Shared utilities for tensor generation, including target calculations.
─────────────────────────────────────────────────────────────────────────────
"""
import pandas as pd
from typing import Tuple
from ml_engine.config.training_config import training_config


def add_target_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the production target definition to the dataframe.
    Target: 1 if future return > threshold, else 0.
    """
    df = df.copy()
    future_return = df["close"].pct_change(periods=training_config.FORECAST_HORIZON).shift(-training_config.FORECAST_HORIZON)
    df["future_return"] = future_return
    # Drop rows where target is NaN (typically the end of the time series)
    df = df.dropna(subset=["future_return"])
    df["target"] = (df["future_return"] > (training_config.RETURN_THRESHOLD_BPS / 10000.0)).astype(int)
    df = df.drop(columns=["future_return"])
    return df
