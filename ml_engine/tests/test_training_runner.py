"""
ml_engine/tests/test_training_runner.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for ProductionTrainingRunner and Callbacks.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from ml_engine.training.runner import ProductionTrainingRunner
from ml_engine.training.callbacks import ExperimentTrackingCallback
from ml_engine.experiments.tracker import ExperimentTracker


@patch("ml_engine.training.runner.RegistryManager")
@patch("ml_engine.training.runner.ModelFactory")
def test_production_training_runner_dry_run(mock_factory, mock_registry):
    mock_reg_instance = MagicMock()
    mock_registry.return_value = mock_reg_instance
    
    mock_reg_instance.register_candidate.return_value = {"model_version": "v1"}
    
    runner = ProductionTrainingRunner(
        dataset_version="CORE/v1.0",
        experiment_name="TestExp",
        model_type="GRU",
        dry_run=True
    )
    
    results = runner.run()
    
    assert "version" in results
    assert "eval_metrics" in results
    assert "GRU" in results["version"]
    assert mock_reg_instance.register_candidate.called


def test_experiment_tracking_callback(tmp_path):
    db_path = str(tmp_path / "tracking.db")
    tracker = ExperimentTracker("CallbackExp", "Run-1", db_path=db_path)
    
    callback = ExperimentTrackingCallback(tracker)
    
    # Simulate training loop
    callback.on_train_begin({"lr": 0.01})
    
    callback.on_epoch_begin(0)
    callback.on_epoch_end(0, {"loss": 0.5})
    
    callback.on_train_end({"f1": 0.9}, "artifacts/model.pt")
    
    # Assert tracker was updated
    assert tracker.run.status == "COMPLETED"
    assert tracker.run.parameters["lr"] == 0.01
    assert "epoch_duration_s" in tracker.run.metrics
    assert tracker.run.metrics["loss"] == 0.5
    assert tracker.run.metrics["f1"] == 0.9
    assert tracker.run.artifacts["best_model"] == "artifacts/model.pt"
