"""
ml_engine/tests/test_tensors.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for Tensor Dataset Generation logic.
─────────────────────────────────────────────────────────────────────────────
"""
import pytest
import numpy as np
import pandas as pd
from ml_engine.data.tensors.window_generator import WindowGenerator
from ml_engine.data.tensors.validator import TensorValidator
from ml_engine.data.tensors.utils import add_target_column
from ml_engine.config.training_config import training_config


def test_add_target_column():
    df = pd.DataFrame({
        "close": [100, 102, 101, 105, 104]
    })
    training_config.FORECAST_HORIZON = 1
    training_config.RETURN_THRESHOLD_BPS = 0.0
    
    out = add_target_column(df)
    
    assert "target" in out.columns
    assert len(out) == 4
    # (102-100)/100 > 0 -> 1
    # (101-102)/102 < 0 -> 0
    # (105-101)/101 > 0 -> 1
    # (104-105)/105 < 0 -> 0
    assert out["target"].tolist() == [1, 0, 1, 0]


def test_window_generator():
    df = pd.DataFrame({
        "f1": [1, 2, 3, 4, 5],
        "f2": [5, 4, 3, 2, 1],
        "target": [0, 1, 0, 1, 0]
    })
    training_config.SEQUENCE_LENGTH = 3
    
    X, y = WindowGenerator.generate(df, ["f1", "f2"])
    
    assert X.shape == (3, 3, 2)
    assert y.shape == (3,)
    
    # First window target should align with the end of the window (idx 2 => target[2] = 0)
    assert y[0] == 0
    assert y[1] == 1
    assert y[2] == 0


def test_tensor_validator():
    X_good = np.random.rand(10, 5, 2)
    y_good = np.random.randint(0, 2, size=10)
    
    assert TensorValidator.validate(X_good, y_good, 2, 5) is True
    
    # Bad labels
    y_bad = np.array([0, 1, 2, 1, 0, 1, 0, 1, 0, 1])
    assert TensorValidator.validate(X_good, y_bad, 2, 5) is False
    
    # Bad dims
    assert TensorValidator.validate(X_good, y_good, 3, 5) is False
