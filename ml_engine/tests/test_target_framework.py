import pytest
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from ml_engine.core.types import TaskType
from ml_engine.data.tensors.target_factory import TargetFactory
from ml_engine.training.loss_factory import LossFactory
from ml_engine.training.metrics_registry import MetricsRegistry
from ml_engine.inference.decoder import PredictionDecoder

class DummyTargetConfig:
    def __init__(self, task_type, target_type="CLASS", horizons=[1], primary_horizon=1, thresholds=[0.0]):
        self.task_type = task_type
        self.target_type = target_type
        self.horizons = horizons
        self.primary_horizon = primary_horizon
        self.thresholds = thresholds

def test_target_factory_binary():
    df = pd.DataFrame({"close": [100, 101, 102, 100]})
    config = DummyTargetConfig(TaskType.BINARY_CLASSIFICATION)
    df_out = TargetFactory.generate(df, config)
    assert "target" in df_out.columns
    assert len(df_out) == 3
    assert df_out["target"].iloc[0] == 1 # 101 > 100
    assert df_out["target"].iloc[-1] == 0 # 100 < 102

def test_loss_factory():
    loss_bin = LossFactory.get_loss(TaskType.BINARY_CLASSIFICATION)
    assert isinstance(loss_bin, nn.BCEWithLogitsLoss)
    
    loss_reg = LossFactory.get_loss(TaskType.REGRESSION)
    assert isinstance(loss_reg, nn.HuberLoss)

def test_metrics_registry():
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 1])
    metrics = MetricsRegistry.evaluate(TaskType.BINARY_CLASSIFICATION, y_true, y_pred, y_pred)
    assert metrics["accuracy"] == 1.0
    assert "f1" in metrics

def test_prediction_decoder():
    raw_logit = np.array([-1.0, 2.0]) # Class 1 wins
    decoded = PredictionDecoder.decode(raw_logit, TaskType.MULTICLASS_CLASSIFICATION)
    assert decoded["predicted_class"] == 1
    assert "class_probabilities" in decoded
