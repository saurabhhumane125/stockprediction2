"""
ml_engine/tests/test_optimization.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for Milestone 19 – Production Hyperparameter Optimization.
─────────────────────────────────────────────────────────────────────────────
"""
import json
import os
import sqlite3
import pytest
import optuna

from ml_engine.optimization.results import (
    OptimizationResult, TrialRecord, ParameterImportance
)
from ml_engine.optimization.search_space import (
    SearchSpaceConfig, suggest_hyperparameters, default_search_space
)
from ml_engine.optimization.callbacks import build_pruner, LoggingCallback
from ml_engine.optimization.study_manager import StudyManager
from ml_engine.optimization.report_builder import OptimizationReportBuilder


def test_results_serialization():
    result = OptimizationResult(
        study_name="test_study",
        n_trials=10,
        best_value=0.85,
        best_params={"LEARNING_RATE": 0.01},
        best_trial_number=5,
        top_n_trials=[
            TrialRecord(
                number=5,
                state="COMPLETE",
                value=0.85,
                datetime_start="2026-01-01T00:00:00",
                datetime_complete="2026-01-01T00:05:00",
                params={"LEARNING_RATE": 0.01},
                duration_seconds=300.0
            )
        ],
        parameter_importance=[
            ParameterImportance(name="LEARNING_RATE", importance=1.0)
        ]
    )
    d = result.to_dict()
    assert d["study_name"] == "test_study"
    assert len(d["top_n_trials"]) == 1
    assert len(d["parameter_importance"]) == 1
    # Check that it is JSON serializable
    json.dumps(d)


def test_search_space_suggests_valid_params():
    study = optuna.create_study()
    trial = study.ask()
    params = suggest_hyperparameters(trial, default_search_space)
    
    assert "MODEL_TYPE" in params
    assert params["MODEL_TYPE"] in default_search_space.model_types
    assert "LEARNING_RATE" in params
    assert default_search_space.learning_rate_range[0] <= params["LEARNING_RATE"] <= default_search_space.learning_rate_range[1]
    
    if params["MODEL_TYPE"] == "Transformer":
        assert "TRANSFORMER_HEADS" in params
        assert params["HIDDEN_SIZE"] % params["TRANSFORMER_HEADS"] == 0


def test_build_pruner():
    median = build_pruner("median")
    assert isinstance(median, optuna.pruners.MedianPruner)
    
    halving = build_pruner("SuccessiveHalving")
    assert isinstance(halving, optuna.pruners.SuccessiveHalvingPruner)
    
    hyperband = build_pruner("hyperband")
    assert isinstance(hyperband, optuna.pruners.HyperbandPruner)
    
    nop = build_pruner("invalid")
    assert isinstance(nop, optuna.pruners.NopPruner)


def test_study_manager_creation_and_resume(tmp_path):
    storage_path = os.path.join(tmp_path, "optuna.db")
    manager1 = StudyManager("test_study", storage_path, pruner_type="median")
    study1 = manager1.get_study()
    
    # Add a trial
    study1.enqueue_trial({"LEARNING_RATE": 0.01, "MODEL_TYPE": "GRU", "HIDDEN_SIZE": 64, "NUM_LAYERS": 2, "DROPOUT": 0.1, "ACTIVATION": "relu", "BATCH_SIZE": 32, "OPTIMIZER": "adam", "LR_SCHEDULER": "None", "WEIGHT_DECAY": 1e-4, "GRADIENT_CLIP_NORM": 1.0, "SEQUENCE_LENGTH": 48})
    study1.optimize(lambda t: suggest_hyperparameters(t) and 0.5, n_trials=1)
    
    assert len(study1.trials) == 1
    
    # Resume study
    manager2 = StudyManager("test_study", storage_path, pruner_type="median")
    study2 = manager2.get_study()
    
    assert len(study2.trials) == 1
    assert study2.study_name == "test_study"


def test_report_builder(tmp_path):
    result = OptimizationResult(
        study_name="test_report",
        n_trials=2,
        best_value=0.9,
        best_params={"lr": 0.01},
        best_trial_number=1,
        failed_trials=[
            TrialRecord(
                number=0,
                state="FAIL",
                value=None,
                datetime_start="2026-01-01T00:00:00",
                datetime_complete=None,
                params={"lr": 0.1},
                duration_seconds=10.0
            )
        ]
    )
    
    builder = OptimizationReportBuilder(str(tmp_path))
    paths = builder.build(result)
    
    assert "json" in paths and os.path.exists(paths["json"])
    assert "markdown" in paths and os.path.exists(paths["markdown"])
    assert "csv" in paths and os.path.exists(paths["csv"])
    
    with open(paths["markdown"], "r", encoding="utf-8") as f:
        content = f.read()
        assert "Optimization Report – test_report" in content
        assert "Failed Trials" in content
        assert "- **Count:** 1" in content
