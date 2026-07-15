"""
ml_engine/tests/test_experiments.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for the Experiment Tracking System.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import pytest

from ml_engine.experiments.tracker import ExperimentTracker
from ml_engine.experiments.manager import ExperimentManager
from ml_engine.experiments.report_builder import ExperimentReportBuilder


@pytest.fixture
def temp_db(tmp_path):
    db_path = str(tmp_path / "tracking.db")
    yield db_path
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass


def test_tracker_lifecycle(temp_db):
    tracker = ExperimentTracker("Test-Exp", "Run-1", db_path=temp_db)
    
    # Log some data
    tracker.log_parameters({"learning_rate": 0.01, "epochs": 50})
    tracker.log_metrics({"f1_score": 0.85, "accuracy": 0.90})
    tracker.log_artifacts({"model": "models/v1.pkl"})
    
    tracker.end_run("COMPLETED")
    
    # Verify via Manager
    manager = ExperimentManager(temp_db)
    
    # Check Experiments
    exps = manager.list_experiments()
    assert len(exps) == 1
    assert exps[0].name == "Test-Exp"
    
    # Check Runs
    runs = manager.list_runs("Test-Exp")
    assert len(runs) == 1
    run = runs[0]
    
    assert run.run_name == "Run-1"
    assert run.status == "COMPLETED"
    
    assert run.parameters["learning_rate"] == "0.01"
    assert run.metrics["f1_score"] == 0.85
    assert run.artifacts["model"] == "models/v1.pkl"
    assert "os" in run.metadata


def test_leaderboard(temp_db):
    t1 = ExperimentTracker("LB-Exp", "Run-Bad", db_path=temp_db)
    t1.log_metrics({"f1": 0.5})
    t1.end_run()
    
    t2 = ExperimentTracker("LB-Exp", "Run-Good", db_path=temp_db)
    t2.log_metrics({"f1": 0.9})
    t2.end_run()
    
    manager = ExperimentManager(temp_db)
    leaderboard = manager.get_leaderboard("LB-Exp", "f1", descending=True)
    
    assert len(leaderboard) == 2
    assert leaderboard[0].run_name == "Run-Good"
    assert leaderboard[1].run_name == "Run-Bad"


def test_comparison_report(temp_db):
    t1 = ExperimentTracker("Comp", "R1", db_path=temp_db)
    t1.log_metrics({"val_loss": 0.2})
    t1.log_parameters({"lr": 0.1})
    t1.end_run()
    
    t2 = ExperimentTracker("Comp", "R2", db_path=temp_db)
    t2.log_metrics({"val_loss": 0.1})
    t2.log_parameters({"lr": 0.01})
    t2.end_run()
    
    manager = ExperimentManager(temp_db)
    runs = [manager.get_run(t1.run.run_id), manager.get_run(t2.run.run_id)]
    
    md = ExperimentReportBuilder.build_comparison_markdown(runs)
    assert "R1" in md
    assert "R2" in md
    assert "0.2" in md
    assert "0.1" in md
    
    csv_out = ExperimentReportBuilder.export_csv(runs)
    assert "metric_val_loss" in csv_out
    assert "param_lr" in csv_out
