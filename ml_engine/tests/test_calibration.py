"""
ml_engine/tests/test_calibration.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for Milestone 20 – Production Confidence Calibration.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import numpy as np
import pytest
import torch

from ml_engine.calibration.calibrator import CalibrationManager, CalibratedModelWrapper
from ml_engine.calibration.methods import get_calibrator
from ml_engine.calibration.results import CalibrationMetrics, CalibrationResult
from ml_engine.calibration.report_builder import CalibrationReportBuilder
from ml_engine.calibration.visualizer import CalibrationVisualizer
from ml_engine.evaluation.metrics import compute_classification_metrics
from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2


# Dummy model for testing wrapper
class DummyModel:
    def predict(self, X, device="cpu"):
        # Return dummy logits and probs
        N = len(X)
        probs = np.zeros((N, 2))
        probs[:, 1] = np.linspace(0.1, 0.9, N)
        probs[:, 0] = 1 - probs[:, 1]
        logits = torch.tensor(np.log(probs / (1 - probs + 1e-9)))
        return logits, torch.tensor(probs, dtype=torch.float32)


@pytest.fixture
def dummy_data():
    np.random.seed(42)
    # Generate some uncalibrated probabilities and true labels
    N = 1000
    y_prob = np.random.beta(0.5, 0.5, N)
    # True labels somewhat related to probabilities but noisy
    y_true = (np.random.rand(N) < (y_prob ** 0.5)).astype(int)
    return y_prob, y_true


def test_platt_scaler(dummy_data):
    y_prob, y_true = dummy_data
    calibrator = get_calibrator("platt")
    
    calibrator.fit(y_prob, y_true)
    y_calib = calibrator.transform(y_prob)
    
    assert y_calib.shape == y_prob.shape
    assert np.all((y_calib >= 0) & (y_calib <= 1))


def test_isotonic_calibrator(dummy_data):
    y_prob, y_true = dummy_data
    calibrator = get_calibrator("isotonic")
    
    calibrator.fit(y_prob, y_true)
    y_calib = calibrator.transform(y_prob)
    
    assert y_calib.shape == y_prob.shape
    assert np.all((y_calib >= 0) & (y_calib <= 1))


def test_calibration_manager_serialization(dummy_data, tmp_path):
    y_prob, y_true = dummy_data
    manager = CalibrationManager("platt")
    manager.fit(y_prob, y_true)
    
    path = os.path.join(tmp_path, "calibrator.pkl")
    manager.save(path)
    
    loaded_manager = CalibrationManager.load(path)
    assert loaded_manager.method_name == "platt"
    assert loaded_manager._fitted is True
    
    y_calib_orig = manager.transform(y_prob)
    y_calib_loaded = loaded_manager.transform(y_prob)
    
    np.testing.assert_array_almost_equal(y_calib_orig, y_calib_loaded)


def test_calibrated_model_wrapper():
    base_model = DummyModel()
    manager = CalibrationManager("none")
    manager.fit(np.array([0.5]), np.array([1]))
    
    wrapper = CalibratedModelWrapper(base_model, manager)
    
    X_dummy = torch.randn(10, 5)
    logits, probs = wrapper.predict(X_dummy)
    
    assert probs.shape == (10, 2)
    assert isinstance(probs, torch.Tensor)
    
    # Check duck-typing compatibility with ProductionEvaluatorV2
    evaluator = ProductionEvaluatorV2(artifact_dir="dummy_dir", run_walk_forward=False)
    # Should not throw exception when we mock the save functions
    y_prob_2d, y_pred, y_prob_pos = evaluator._infer(wrapper, X_dummy.numpy(), 0.5)
    assert y_prob_2d.shape == (10, 2)


def test_report_builder(tmp_path):
    result = CalibrationResult(
        method="isotonic",
        before_metrics=CalibrationMetrics(ece=0.1, mce=0.2, brier_score=0.15, log_loss=0.5),
        after_metrics=CalibrationMetrics(ece=0.05, mce=0.1, brier_score=0.12, log_loss=0.4),
        execution_time_seconds=1.5,
        artifact_paths={}
    )
    
    builder = CalibrationReportBuilder(str(tmp_path))
    paths = builder.build(result)
    
    assert "json" in paths and os.path.exists(paths["json"])
    assert "markdown" in paths and os.path.exists(paths["markdown"])
    assert "csv" in paths and os.path.exists(paths["csv"])
    
    with open(paths["markdown"], "r", encoding="utf-8") as f:
        content = f.read()
        assert "Calibration Report" in content
        assert "✅" in content


def test_visualizer(dummy_data, tmp_path):
    y_prob, y_true = dummy_data
    calibrator = get_calibrator("isotonic")
    calibrator.fit(y_prob, y_true)
    y_calib = calibrator.transform(y_prob)
    
    vis = CalibrationVisualizer(str(tmp_path))
    paths = vis.generate_plots(y_true, y_prob, y_calib)
    
    assert "reliability_diagram" in paths and os.path.exists(paths["reliability_diagram"])
    assert "histogram" in paths and os.path.exists(paths["histogram"])
