import pytest
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from ml_engine.core.types import TaskType
from ml_engine.data.tensors.targets.manager import TargetManager
from ml_engine.data.tensors.targets.strategies.legacy import LegacyTargetStrategy
from ml_engine.inference.decoders.legacy_decoder import LegacyInferenceDecoder
from ml_engine.training.loss_factory import LossFactory
from ml_engine.training.metrics_registry import MetricsRegistry

class DummyTargetConfig:
    def __init__(self, task_type, target_type="CLASS", horizons=[1], primary_horizon=1, thresholds=[0.0]):
        self.task_type = task_type
        self.target_type = target_type
        self.horizons = horizons
        self.primary_horizon = primary_horizon
        self.thresholds = thresholds
        self.strategy_name = "legacy"
        self.strategy_version = "1.0"

class DummyConfig:
    def __init__(self, task_type):
        self.target = DummyTargetConfig(task_type)

def test_target_factory_binary():
    df = pd.DataFrame({"close": [100, 101, 102, 100]})
    config = DummyConfig(TaskType.BINARY_CLASSIFICATION)
    target_strategy = TargetManager.get_strategy(config)
    df_out, target_cols = target_strategy.generate(df, config.target)
    assert target_cols == ["target"]
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
    metadata = {"strategy_name": "legacy", "strategy_version": "1.0", "task_type": "MULTICLASS_CLASSIFICATION"}
    decoder = TargetManager.get_decoder(metadata)
    decoded = decoder.decode(raw_logit, None, metadata)
    assert decoded["predicted_class"] == 1
    assert "class_probabilities" in decoded
