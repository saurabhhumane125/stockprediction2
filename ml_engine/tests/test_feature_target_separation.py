import pytest
import pandas as pd
import numpy as np
from typing import List

from ml_engine.core.types import TaskType
from ml_engine.data.tensors.validator import TensorValidator
from ml_engine.data.tensors.metadata import MetadataGenerator
from ml_engine.data.tensors.targets.manager import TargetManager

class DummyTargetConfig:
    def __init__(self, task_type, target_type, horizons, primary_horizon):
        self.task_type = task_type
        self.target_type = target_type
        self.horizons = horizons
        self.primary_horizon = primary_horizon
        self.thresholds = [0.0]
        self.strategy_name = "legacy"
        self.strategy_version = "1.0"

class DummyRegressionConfig:
    target = DummyTargetConfig(TaskType.REGRESSION, "RETURN", [5], 5)

class DummyBinaryConfig:
    target = DummyTargetConfig(TaskType.BINARY_CLASSIFICATION, "CLASS", [1], 1)

class DummyMultiOutputConfig:
    target = DummyTargetConfig(TaskType.MULTI_OUTPUT_REGRESSION, "RETURN", [1, 3, 5, 10], 5)

def test_target_factory_explicit_cols():
    reg_strategy = TargetManager.get_strategy(DummyRegressionConfig)
    assert reg_strategy.get_target_cols(DummyRegressionConfig.target) == ["return_5d"]

    bin_strategy = TargetManager.get_strategy(DummyBinaryConfig)
    assert bin_strategy.get_target_cols(DummyBinaryConfig.target) == ["target"]

    multi_strategy = TargetManager.get_strategy(DummyMultiOutputConfig)
    assert multi_strategy.get_target_cols(DummyMultiOutputConfig.target) == ["return_1d", "return_3d", "return_5d", "return_10d"]

def test_feature_target_separation_with_return_lags():
    # Construct a sample dataframe with engineered return_lag features and close prices
    data = {
        "ticker": ["RELIANCE.NS"] * 10,
        "close": [100.0, 102.0, 101.0, 105.0, 107.0, 108.0, 110.0, 112.0, 115.0, 118.0],
        "return_lag_1": [0.01, 0.02, -0.01, 0.04, 0.02, 0.01, 0.02, 0.02, 0.03, 0.03],
        "return_lag_2": [0.01, 0.02, 0.01, 0.03, 0.05, 0.03, 0.03, 0.04, 0.05, 0.06],
        "return_lag_3": [0.00, 0.01, 0.02, 0.02, 0.04, 0.06, 0.04, 0.05, 0.06, 0.07],
        "return_lag_5": [0.00, 0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
        "volume": [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    }
    df = pd.DataFrame(data)

    reg_strategy = TargetManager.get_strategy(DummyRegressionConfig)
    df_out, target_cols = reg_strategy.generate(df, DummyRegressionConfig.target)

    # 1. Target columns must be exactly ["return_5d"]
    assert target_cols == ["return_5d"]
    assert "return_5d" in df_out.columns

    # 2. Exclude ticker and target_cols to get feature_cols
    exclude = {"ticker"}.union(set(target_cols))
    feature_cols = [c for c in df_out.columns if c not in exclude]

    # 3. Verify return_lag_* columns remain in feature_cols
    assert "return_lag_1" in feature_cols
    assert "return_lag_2" in feature_cols
    assert "return_lag_3" in feature_cols
    assert "return_lag_5" in feature_cols
    assert "volume" in feature_cols
    assert "return_5d" not in feature_cols


def test_validator_with_explicit_targets():
    X = np.random.randn(20, 48, 10)
    y_single = np.random.randn(20, 1)
    y_multi = np.random.randn(20, 4)

    assert TensorValidator.validate(X, y_single, 10, 48, TaskType.REGRESSION, expected_targets=1) is True
    assert TensorValidator.validate(X, y_multi, 10, 48, TaskType.MULTI_OUTPUT_REGRESSION, expected_targets=4) is True
    assert TensorValidator.validate(X, y_multi, 10, 48, TaskType.REGRESSION, expected_targets=1) is False


def test_metadata_generator_explicit_fields():
    feature_cols = ["return_lag_1", "return_lag_2", "volume"]
    target_cols = ["return_5d"]
    meta = MetadataGenerator.generate(
        dataset_version="NIFTY50/v3.0",
        feature_cols=feature_cols,
        train_shape=(100, 48, 3),
        val_shape=(20, 48, 3),
        test_shape=(10, 48, 3),
        y_train_dist={},
        scaler_info={"scaler_type": "StandardScaler"},
        target_cols=target_cols
    )

    assert meta["feature_columns"] == feature_cols
    assert meta["target_columns"] == target_cols
    assert meta["feature_count"] == 3
    assert meta["target_count"] == 1
    assert meta["output_schema"]["shape"] == [1]
