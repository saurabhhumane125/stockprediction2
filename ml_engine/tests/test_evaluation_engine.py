"""
ml_engine/tests/test_evaluation_engine.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for Milestone 18 – Production Evaluation Engine.

Coverage:
  • EvaluationConfig         – required fields, JSON serialisability
  • ClassificationMetrics    – dataclass fields, to_dict
  • compute_classification_metrics – accuracy/F1/ROC guards
  • compute_confusion_matrix  – raw/normalised values, TN/FP/FN/TP
  • compute_calibration       – ECE/MCE bounds, single-class guard
  • WalkForwardResult         – correct fold count, min-samples guard
  • ProductionDecision        – PASS/FAIL logic for each threshold
  • Visualizer                – files created on disk
  • ReportBuilder             – JSON/MD/CSV output content
  • ModelComparator           – ranking, serialisation
  • ProductionEvaluatorV2     – end-to-end pipeline with mock model
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
import pytest

try:
    import torch
    import torch.nn as nn
    TORCH_OK = True
except ImportError:
    TORCH_OK = False

skip_torch = pytest.mark.skipif(not TORCH_OK, reason="torch not installed")

# ── Shared fixtures ────────────────────────────────────────────────────────

N = 120         # samples
SEQ = 20
FEAT = 10
CLASSES = 2


def _binary_arrays(n: int = N, balanced: bool = True):
    """Return (y_true, y_pred, y_prob) with two classes."""
    rng = np.random.default_rng(42)
    y_true = np.tile([0, 1], n // 2)[:n]
    y_prob = np.clip(rng.normal(0.5, 0.2, size=n), 0, 1)
    y_pred = (y_prob >= 0.5).astype(int)
    return y_true, y_pred, y_prob


def _single_class_arrays(n: int = N):
    """Return arrays where all labels are 0."""
    y_true = np.zeros(n, dtype=int)
    y_pred = np.zeros(n, dtype=int)
    y_prob = np.full(n, 0.1)
    return y_true, y_pred, y_prob


# ── EvaluationConfig ──────────────────────────────────────────────────────

class TestEvaluationConfig:
    def test_required_fields(self):
        from ml_engine.config.evaluation_config import evaluation_config
        d = evaluation_config.to_dict()
        for field in [
            "DECISION_THRESHOLD", "PLOT_DPI", "PLOT_STYLE", "COLOR_PALETTE",
            "NUM_CALIBRATION_BINS",
            "MIN_ROC_AUC", "MIN_F1", "MIN_ACCURACY", "MIN_PR_AUC",
            "MAX_LOG_LOSS", "MAX_BRIER_SCORE", "MAX_ECE",
            "WALK_FORWARD_WINDOW", "WALK_FORWARD_STEP", "WALK_FORWARD_MIN_SAMPLES",
            "COMPARATOR_PRIMARY_METRIC", "COMPARATOR_METRICS",
        ]:
            assert field in d, f"Missing: {field}"

    def test_json_serialisable(self):
        from ml_engine.config.evaluation_config import evaluation_config
        json.dumps(evaluation_config.to_dict(), default=str)


# ── Results dataclasses ───────────────────────────────────────────────────

class TestResultDataclasses:
    def test_classification_metrics_to_dict_has_all_keys(self):
        from ml_engine.evaluation.results import ClassificationMetrics
        m = ClassificationMetrics(accuracy=0.9, f1=0.88)
        d = m.to_dict()
        for key in ["accuracy", "balanced_accuracy", "precision", "recall",
                    "f1", "roc_auc", "pr_auc", "mcc", "cohen_kappa",
                    "log_loss", "brier_score"]:
            assert key in d

    def test_evaluation_result_to_dict_json_safe(self):
        from ml_engine.evaluation.results import EvaluationResult
        r = EvaluationResult(model_name="test", model_version="v1")
        json.dumps(r.to_dict(), default=str)

    def test_production_decision_passed_property(self):
        from ml_engine.evaluation.results import ProductionDecision
        d = ProductionDecision(verdict="PASS")
        assert d.passed is True
        d2 = ProductionDecision(verdict="FAIL")
        assert d2.passed is False


# ── Metrics engine ────────────────────────────────────────────────────────

class TestMetricsEngine:
    def test_accuracy_correct(self):
        from ml_engine.evaluation.metrics import compute_classification_metrics
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0])
        y_prob = np.array([0.1, 0.9, 0.2, 0.4])
        m = compute_classification_metrics(y_true, y_pred, y_prob)
        assert m.accuracy == pytest.approx(0.75)

    def test_roc_auc_between_0_and_1(self):
        from ml_engine.evaluation.metrics import compute_classification_metrics
        y_true, y_pred, y_prob = _binary_arrays()
        m = compute_classification_metrics(y_true, y_pred, y_prob)
        assert 0 <= m.roc_auc <= 1

    def test_single_class_nan_guard(self):
        from ml_engine.evaluation.metrics import compute_classification_metrics
        y_true, y_pred, y_prob = _single_class_arrays()
        m = compute_classification_metrics(y_true, y_pred, y_prob)
        assert math.isnan(m.roc_auc)
        assert math.isnan(m.pr_auc)
        assert math.isnan(m.log_loss)

    def test_brier_between_0_and_1(self):
        from ml_engine.evaluation.metrics import compute_classification_metrics
        y_true, y_pred, y_prob = _binary_arrays()
        m = compute_classification_metrics(y_true, y_pred, y_prob)
        assert 0 <= m.brier_score <= 1

    def test_mcc_range(self):
        from ml_engine.evaluation.metrics import compute_classification_metrics
        y_true, y_pred, y_prob = _binary_arrays()
        m = compute_classification_metrics(y_true, y_pred, y_prob)
        assert -1 <= m.mcc <= 1


# ── Confusion matrix ──────────────────────────────────────────────────────

class TestConfusionMatrix:
    def test_raw_sum_equals_n(self):
        from ml_engine.evaluation.confusion import compute_confusion_matrix
        y_true, y_pred, _ = _binary_arrays(60)
        result = compute_confusion_matrix(y_true, y_pred)
        total = sum(sum(row) for row in result.raw)
        assert total == 60

    def test_normalised_rows_sum_to_1(self):
        from ml_engine.evaluation.confusion import compute_confusion_matrix
        y_true, y_pred, _ = _binary_arrays(60)
        result = compute_confusion_matrix(y_true, y_pred)
        for row in result.normalized:
            assert abs(sum(row) - 1.0) < 1e-3, f"Row sum != 1: {row}"

    def test_tn_fp_fn_tp_sum_to_total(self):
        from ml_engine.evaluation.confusion import compute_confusion_matrix
        y_true, y_pred, _ = _binary_arrays(60)
        r = compute_confusion_matrix(y_true, y_pred)
        assert r.tn + r.fp + r.fn + r.tp == 60

    def test_json_export(self, tmp_path):
        from ml_engine.evaluation.confusion import compute_confusion_matrix, save_confusion_matrix_json
        y_true, y_pred, _ = _binary_arrays(40)
        result = compute_confusion_matrix(y_true, y_pred)
        path = str(tmp_path / "cm.json")
        save_confusion_matrix_json(result, path)
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "raw" in data


# ── Calibration ───────────────────────────────────────────────────────────

class TestCalibration:
    def test_ece_between_0_and_1(self):
        from ml_engine.evaluation.calibration import compute_calibration
        y_true, _, y_prob = _binary_arrays()
        result = compute_calibration(y_true, y_prob)
        assert 0 <= result.ece <= 1

    def test_mce_between_0_and_1(self):
        from ml_engine.evaluation.calibration import compute_calibration
        y_true, _, y_prob = _binary_arrays()
        result = compute_calibration(y_true, y_prob)
        assert 0 <= result.mce <= 1

    def test_single_class_returns_nan(self):
        from ml_engine.evaluation.calibration import compute_calibration
        y_true, _, y_prob = _single_class_arrays()
        result = compute_calibration(y_true, y_prob)
        assert math.isnan(result.ece)
        assert math.isnan(result.mce)

    def test_perfect_predictor_low_ece(self):
        from ml_engine.evaluation.calibration import compute_calibration
        n = 200
        y_true = np.tile([0, 1], n // 2)
        y_prob = np.where(y_true == 1, 0.95, 0.05)
        result = compute_calibration(y_true, y_prob)
        assert result.ece < 0.15, f"ECE too high for near-perfect predictor: {result.ece}"


# ── Walk-forward ──────────────────────────────────────────────────────────

class TestWalkForward:
    def _simple_metric_fn(self, y_true, y_pred, y_prob):
        from sklearn.metrics import accuracy_score
        return {"accuracy": float(accuracy_score(y_true, y_pred))}

    def test_fold_count(self):
        from ml_engine.evaluation.walk_forward import run_walk_forward
        y_true, y_pred, y_prob = _binary_arrays(120)
        result = run_walk_forward(y_true, y_pred, y_prob, self._simple_metric_fn, window=40, step=10)
        assert result.n_folds > 0

    def test_mean_accuracy_in_range(self):
        from ml_engine.evaluation.walk_forward import run_walk_forward
        y_true, y_pred, y_prob = _binary_arrays(100)
        result = run_walk_forward(y_true, y_pred, y_prob, self._simple_metric_fn, window=30, step=15)
        acc = result.mean_metrics.get("accuracy", float("nan"))
        assert not math.isnan(acc)
        assert 0 <= acc <= 1

    def test_too_small_dataset_returns_empty(self):
        from ml_engine.evaluation.walk_forward import run_walk_forward
        y_true = np.array([0, 1])
        y_pred = np.array([0, 1])
        y_prob = np.array([0.1, 0.9])
        result = run_walk_forward(y_true, y_pred, y_prob, self._simple_metric_fn, window=50, step=10)
        assert result.n_folds == 0

    def test_to_dict_structure(self):
        from ml_engine.evaluation.walk_forward import run_walk_forward
        y_true, y_pred, y_prob = _binary_arrays(80)
        result = run_walk_forward(y_true, y_pred, y_prob, self._simple_metric_fn, window=30, step=15)
        d = result.to_dict()
        assert "n_folds" in d
        assert "mean_metrics" in d
        assert "folds" in d


# ── Decision Gate ─────────────────────────────────────────────────────────

class TestDecisionGate:
    def _good_metrics(self):
        from ml_engine.evaluation.results import ClassificationMetrics
        return ClassificationMetrics(
            accuracy=0.75, balanced_accuracy=0.74, precision=0.73,
            recall=0.72, f1=0.72, roc_auc=0.78, pr_auc=0.70,
            mcc=0.45, cohen_kappa=0.40, log_loss=0.50, brier_score=0.15,
        )

    def _bad_metrics(self):
        from ml_engine.evaluation.results import ClassificationMetrics
        return ClassificationMetrics(
            accuracy=0.40, balanced_accuracy=0.39, precision=0.38,
            recall=0.35, f1=0.36, roc_auc=0.45, pr_auc=0.30,
            mcc=-0.1, cohen_kappa=-0.05, log_loss=0.95, brier_score=0.40,
        )

    def _good_calibration(self):
        from ml_engine.evaluation.results import CalibrationResult
        return CalibrationResult(ece=0.05, mce=0.08)

    def _bad_calibration(self):
        from ml_engine.evaluation.results import CalibrationResult
        return CalibrationResult(ece=0.30, mce=0.50)

    def test_pass_when_all_thresholds_met(self):
        from ml_engine.evaluation.decision_gate import evaluate_production_readiness
        decision = evaluate_production_readiness(self._good_metrics(), self._good_calibration())
        assert decision.verdict == "PASS"
        assert decision.passed is True
        assert len(decision.failed_checks) == 0

    def test_fail_when_roc_too_low(self):
        from ml_engine.evaluation.decision_gate import evaluate_production_readiness
        decision = evaluate_production_readiness(self._bad_metrics(), self._good_calibration())
        assert decision.verdict == "FAIL"
        assert "ROC-AUC" in decision.failed_checks

    def test_fail_when_ece_too_high(self):
        from ml_engine.evaluation.decision_gate import evaluate_production_readiness
        decision = evaluate_production_readiness(self._good_metrics(), self._bad_calibration())
        assert decision.verdict == "FAIL"
        assert "ECE" in decision.failed_checks

    def test_nan_metric_causes_fail(self):
        from ml_engine.evaluation.results import ClassificationMetrics, CalibrationResult
        from ml_engine.evaluation.decision_gate import evaluate_production_readiness
        m = ClassificationMetrics(roc_auc=float("nan"), f1=0.9, accuracy=0.9, pr_auc=0.9, log_loss=0.3, brier_score=0.1)
        c = CalibrationResult(ece=0.05, mce=0.08)
        decision = evaluate_production_readiness(m, c)
        assert decision.verdict == "FAIL"
        assert "ROC-AUC" in decision.failed_checks

    def test_reasons_populated_on_fail(self):
        from ml_engine.evaluation.decision_gate import evaluate_production_readiness
        decision = evaluate_production_readiness(self._bad_metrics(), self._bad_calibration())
        assert len(decision.reasons) > 0


# ── Visualizer ────────────────────────────────────────────────────────────

class TestVisualizer:
    def test_confusion_matrix_png_created(self, tmp_path):
        from ml_engine.evaluation.confusion import compute_confusion_matrix
        from ml_engine.evaluation.visualizer import plot_confusion_matrix
        y_true, y_pred, _ = _binary_arrays(40)
        cm = compute_confusion_matrix(y_true, y_pred)
        path = plot_confusion_matrix(cm, str(tmp_path))
        assert os.path.exists(path)

    def test_roc_curve_png_created(self, tmp_path):
        from ml_engine.evaluation.visualizer import plot_roc_curve
        y_true, _, y_prob = _binary_arrays(40)
        path = plot_roc_curve(y_true, y_prob, 0.75, str(tmp_path))
        assert os.path.exists(path)

    def test_pr_curve_png_created(self, tmp_path):
        from ml_engine.evaluation.visualizer import plot_pr_curve
        y_true, _, y_prob = _binary_arrays(40)
        path = plot_pr_curve(y_true, y_prob, 0.65, str(tmp_path))
        assert os.path.exists(path)

    def test_calibration_png_created(self, tmp_path):
        from ml_engine.evaluation.calibration import compute_calibration
        from ml_engine.evaluation.visualizer import plot_calibration
        y_true, _, y_prob = _binary_arrays(40)
        cal = compute_calibration(y_true, y_prob)
        if cal.prob_true:
            path = plot_calibration(cal, str(tmp_path))
            assert os.path.exists(path)

    def test_metric_summary_png_created(self, tmp_path):
        from ml_engine.evaluation.results import ClassificationMetrics
        from ml_engine.evaluation.visualizer import plot_metric_summary
        m = ClassificationMetrics(accuracy=0.8, f1=0.79, roc_auc=0.82, pr_auc=0.75)
        path = plot_metric_summary(m, str(tmp_path))
        assert path and os.path.exists(path)


# ── ReportBuilder ─────────────────────────────────────────────────────────

class TestReportBuilder:
    def _result(self):
        from ml_engine.evaluation.results import (
            ClassificationMetrics, ConfusionMatrixResult,
            CalibrationResult, ProductionDecision, EvaluationResult,
        )
        return EvaluationResult(
            model_name="GRU",
            model_version="v1.0.0",
            evaluation_timestamp="2026-07-15T00:00:00+00:00",
            execution_time_seconds=3.14,
            n_test_samples=100,
            decision_threshold=0.5,
            metrics=ClassificationMetrics(accuracy=0.8, roc_auc=0.82, f1=0.79, pr_auc=0.75, log_loss=0.45, brier_score=0.18),
            confusion_matrix=ConfusionMatrixResult(raw=[[40,10],[8,42]], normalized=[[0.8,0.2],[0.16,0.84]], tn=40, fp=10, fn=8, tp=42, total_samples=100),
            calibration=CalibrationResult(ece=0.05, mce=0.08),
            decision=ProductionDecision(verdict="PASS", passed_checks=["ROC-AUC","F1"]),
        )

    def test_json_written(self, tmp_path):
        from ml_engine.evaluation.report_builder import EvaluationReportBuilder
        paths = EvaluationReportBuilder(str(tmp_path)).build(self._result())
        assert os.path.exists(paths["json"])
        with open(paths["json"]) as f:
            data = json.load(f)
        assert data["model_name"] == "GRU"
        assert "metrics" in data
        assert "environment" in data

    def test_markdown_written(self, tmp_path):
        from ml_engine.evaluation.report_builder import EvaluationReportBuilder
        paths = EvaluationReportBuilder(str(tmp_path)).build(self._result())
        assert os.path.exists(paths["markdown"])
        with open(paths["markdown"], encoding="utf-8") as f:
            md = f.read()
        assert "PASS" in md
        assert "Metrics" in md

    def test_csv_written(self, tmp_path):
        from ml_engine.evaluation.report_builder import EvaluationReportBuilder
        paths = EvaluationReportBuilder(str(tmp_path)).build(self._result())
        assert os.path.exists(paths["csv"])
        with open(paths["csv"]) as f:
            content = f.read()
        assert "model_name" in content
        assert "GRU" in content

    def test_all_three_formats_produced(self, tmp_path):
        from ml_engine.evaluation.report_builder import EvaluationReportBuilder
        paths = EvaluationReportBuilder(str(tmp_path)).build(self._result())
        assert set(paths.keys()) >= {"json", "markdown", "csv"}


# ── ModelComparator ───────────────────────────────────────────────────────

class TestModelComparator:
    def _make_result(self, name: str, roc_auc: float, verdict: str):
        from ml_engine.evaluation.results import (
            ClassificationMetrics, ConfusionMatrixResult,
            CalibrationResult, ProductionDecision, EvaluationResult,
        )
        return EvaluationResult(
            model_name=name,
            model_version="v1",
            metrics=ClassificationMetrics(roc_auc=roc_auc, f1=0.7, accuracy=0.72, pr_auc=0.65, log_loss=0.5, brier_score=0.2, mcc=0.4),
            decision=ProductionDecision(verdict=verdict),
            confusion_matrix=ConfusionMatrixResult(),
            calibration=CalibrationResult(),
        )

    def test_rank_orders_by_primary_metric(self):
        from ml_engine.evaluation.comparator import ModelComparator
        comp = ModelComparator(primary_metric="roc_auc")
        comp.add(self._make_result("LSTM", 0.70, "PASS"))
        comp.add(self._make_result("GRU",  0.82, "PASS"))
        comp.add(self._make_result("BiGRU",0.75, "PASS"))
        ranked = comp.rank()
        assert ranked[0].model_name == "GRU"
        assert ranked[-1].model_name == "LSTM"

    def test_markdown_table_contains_all_models(self):
        from ml_engine.evaluation.comparator import ModelComparator
        comp = ModelComparator()
        comp.add(self._make_result("GRU", 0.80, "PASS"))
        comp.add(self._make_result("Transformer", 0.85, "PASS"))
        md = comp.to_markdown()
        assert "GRU" in md
        assert "Transformer" in md

    def test_save_produces_three_files(self, tmp_path):
        from ml_engine.evaluation.comparator import ModelComparator
        comp = ModelComparator()
        comp.add(self._make_result("GRU", 0.80, "PASS"))
        comp.add(self._make_result("LSTM", 0.72, "FAIL"))
        paths = comp.save(str(tmp_path))
        for key in ["json", "markdown", "csv"]:
            assert os.path.exists(paths[key]), f"Missing {key}"

    def test_empty_comparator_markdown(self):
        from ml_engine.evaluation.comparator import ModelComparator
        comp = ModelComparator()
        md = comp.to_markdown()
        assert "No models" in md


# ── ProductionEvaluatorV2 end-to-end ──────────────────────────────────────

@skip_torch
class TestProductionEvaluatorV2:
    def _make_model(self):
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        return GRUClassifier(input_size=FEAT, hidden_size=16, num_layers=1, output_classes=CLASSES)

    def _make_data(self, n: int = N):
        rng = np.random.default_rng(42)
        X = rng.random((n, SEQ, FEAT)).astype(np.float32)
        y = np.tile([0, 1], n // 2)[:n]
        return X, y

    def test_evaluate_returns_result(self, tmp_path):
        from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2
        model = self._make_model()
        X, y = self._make_data()
        evaluator = ProductionEvaluatorV2(str(tmp_path), run_walk_forward=False)
        result = evaluator.evaluate(model, X, y, "GRU", "v1")
        assert result.n_test_samples == N
        assert result.model_name == "GRU"

    def test_evaluate_creates_reports(self, tmp_path):
        from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2
        model = self._make_model()
        X, y = self._make_data()
        evaluator = ProductionEvaluatorV2(str(tmp_path), run_walk_forward=False)
        result = evaluator.evaluate(model, X, y, "GRU", "v1")
        assert "json" in result.artifact_paths
        assert os.path.exists(result.artifact_paths["json"])

    def test_evaluate_creates_plots(self, tmp_path):
        from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2
        model = self._make_model()
        X, y = self._make_data()
        evaluator = ProductionEvaluatorV2(str(tmp_path), run_walk_forward=False)
        result = evaluator.evaluate(model, X, y)
        plots_dir = os.path.join(str(tmp_path), "plots")
        assert os.path.isdir(plots_dir)
        assert len(os.listdir(plots_dir)) > 0

    def test_decision_verdict_is_pass_or_fail(self, tmp_path):
        from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2
        model = self._make_model()
        X, y = self._make_data()
        evaluator = ProductionEvaluatorV2(str(tmp_path), run_walk_forward=False)
        result = evaluator.evaluate(model, X, y)
        assert result.decision.verdict in {"PASS", "FAIL"}

    def test_empty_x_raises(self, tmp_path):
        from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2
        model = self._make_model()
        evaluator = ProductionEvaluatorV2(str(tmp_path))
        with pytest.raises(ValueError, match="empty"):
            evaluator.evaluate(model, np.empty((0, SEQ, FEAT), dtype=np.float32), np.array([]))

    def test_walk_forward_runs_when_enough_data(self, tmp_path):
        from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2
        model = self._make_model()
        X, y = self._make_data(200)
        evaluator = ProductionEvaluatorV2(str(tmp_path), run_walk_forward=True)
        result = evaluator.evaluate(model, X, y)
        assert result.walk_forward is not None
        assert result.walk_forward.n_folds > 0

    def test_sector_evaluation(self, tmp_path):
        from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2
        model = self._make_model()
        X, y = self._make_data(80)
        sectors = np.array(["IT"] * 40 + ["FMCG"] * 40)
        evaluator = ProductionEvaluatorV2(str(tmp_path), run_walk_forward=False)
        results = evaluator.evaluate_by_sector(model, X, y, sectors)
        assert "IT" in results
        assert "FMCG" in results
