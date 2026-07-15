"""
ml_engine/evaluation/evaluator_v2.py
─────────────────────────────────────────────────────────────────────────────
Production Evaluation Engine (PyTorch-native, Milestone 18).

This evaluator is **architecture-agnostic**: it accepts any
``BaseTimeSeriesClassifier`` (GRU / BiGRU / LSTM / Transformer) and raw
numpy arrays, then orchestrates the full evaluation pipeline:

  1. Model inference → y_prob, y_pred
  2. Classification metrics  (metrics.py)
  3. Confusion matrix         (confusion.py)
  4. Calibration analysis     (calibration.py)
  5. Walk-forward validation  (walk_forward.py)
  6. Production decision gate (decision_gate.py)
  7. Visualisation            (visualizer.py)
  8. Report generation        (report_builder.py)

The **legacy Keras evaluator** (``evaluator.py``) is intentionally
preserved — it is used by the existing test suite and the registry
pipeline that loads ``.keras`` models.  This file lives alongside it.

Sector-grouped evaluation is supported via ``evaluate_by_sector()``.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import math
import os
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import torch

from ml_engine.config.evaluation_config import evaluation_config
from ml_engine.evaluation.calibration import compute_calibration
from ml_engine.evaluation.confusion import compute_confusion_matrix, save_confusion_matrix_json
from ml_engine.evaluation.decision_gate import evaluate_production_readiness
from ml_engine.evaluation.metrics import (
    compute_classification_metrics,
    compute_pr_data,
    compute_roc_data,
)
from ml_engine.evaluation.report_builder import EvaluationReportBuilder
from ml_engine.evaluation.results import EvaluationResult
from ml_engine.evaluation.visualizer import (
    plot_calibration,
    plot_calibration_histogram,
    plot_confusion_matrix,
    plot_metric_summary,
    plot_pr_curve,
    plot_roc_curve,
)
from ml_engine.evaluation.walk_forward import run_walk_forward
from ml_engine.models.base_model import BaseTimeSeriesClassifier

logger = logging.getLogger(__name__)


class ProductionEvaluatorV2:
    """
    Architecture-agnostic production evaluation engine for PyTorch models.

    Args:
        artifact_dir:  Root directory where all artefacts (plots, reports,
                       JSON files) will be written.
        device:        PyTorch device string (``"cpu"`` / ``"cuda"``).
        run_walk_forward: Whether to execute walk-forward validation.
                          Can be disabled for speed in CI.
    """

    def __init__(
        self,
        artifact_dir: str,
        device: str = "cpu",
        run_walk_forward: bool = True,
    ) -> None:
        self.artifact_dir = artifact_dir
        self.plots_dir = os.path.join(artifact_dir, "plots")
        self.device = device
        self._run_walk_forward = run_walk_forward

        os.makedirs(self.plots_dir, exist_ok=True)
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            plt.style.use(evaluation_config.PLOT_STYLE)
        except Exception:
            pass   # graceful degradation if matplotlib unavailable

    # ── Public API ────────────────────────────────────────────────────────

    def evaluate(
        self,
        model: BaseTimeSeriesClassifier,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_name: str = "model",
        model_version: str = "unknown",
        threshold: Optional[float] = None,
    ) -> EvaluationResult:
        """
        Run the full evaluation pipeline on the provided test arrays.

        Args:
            model:         Trained ``BaseTimeSeriesClassifier`` instance.
            X_test:        Test features, shape ``(N, seq_len, n_features)``.
            y_test:        Test labels,   shape ``(N,)``.
            model_name:    Human-readable model name (used in reports).
            model_version: Model version string (used in reports).
            threshold:     Decision threshold (defaults to config value).

        Returns:
            Populated ``EvaluationResult``.

        Raises:
            ValueError: If test data is empty or has fewer than 2 classes.
        """
        threshold = threshold or evaluation_config.DECISION_THRESHOLD

        if len(X_test) == 0:
            raise ValueError("X_test is empty — cannot evaluate.")

        logger.info(
            f"[EvaluatorV2] Starting evaluation of '{model_name}' v{model_version} "
            f"on {len(X_test)} samples."
        )
        start = time.time()

        # ── 1. Inference ──────────────────────────────────────────────────
        y_prob_2d, y_pred, y_prob_pos = self._infer(model, X_test, threshold)

        # ── 2. Metrics ────────────────────────────────────────────────────
        multi_class = len(np.unique(y_test)) > 1
        metrics = compute_classification_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_prob=y_prob_2d if not multi_class else y_prob_2d,
            threshold=threshold,
        )

        # ── 3. Confusion Matrix ───────────────────────────────────────────
        cm_result = compute_confusion_matrix(y_test, y_pred)

        # ── 4. Calibration ────────────────────────────────────────────────
        calibration = self._safe_calibration(y_test, y_prob_pos)

        # ── 5. Walk-forward ───────────────────────────────────────────────
        wf_result = None
        if self._run_walk_forward and len(X_test) >= evaluation_config.WALK_FORWARD_WINDOW:
            wf_result = self._walk_forward(y_test, y_pred, y_prob_pos)

        # ── 6. Production Decision ────────────────────────────────────────
        decision = evaluate_production_readiness(metrics, calibration)

        # ── 7. Visualisations ─────────────────────────────────────────────
        artifact_paths = self._generate_plots(
            y_test, y_pred, y_prob_pos, metrics, cm_result, calibration, multi_class
        )

        # ── 8. Confusion Matrix JSON ──────────────────────────────────────
        cm_json_path = os.path.join(self.artifact_dir, "confusion_matrix.json")
        save_confusion_matrix_json(cm_result, cm_json_path)
        artifact_paths["confusion_matrix_json"] = cm_json_path

        # ── 9. Build Result ───────────────────────────────────────────────
        duration = time.time() - start
        result = EvaluationResult(
            model_name=model_name,
            model_version=model_version,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
            execution_time_seconds=round(duration, 3),
            n_test_samples=int(len(y_test)),
            decision_threshold=threshold,
            metrics=metrics,
            confusion_matrix=cm_result,
            calibration=calibration,
            walk_forward=wf_result,
            decision=decision,
            artifact_paths=artifact_paths,
        )

        # ── 10. Reports ───────────────────────────────────────────────────
        report_paths = EvaluationReportBuilder(self.artifact_dir).build(result)
        result.artifact_paths.update(report_paths)

        logger.info(
            f"[EvaluatorV2] Evaluation complete in {duration:.2f}s | "
            f"Verdict={decision.verdict} | ROC-AUC={metrics.roc_auc:.4f}"
        )
        return result

    def evaluate_by_sector(
        self,
        model: BaseTimeSeriesClassifier,
        X_test: np.ndarray,
        y_test: np.ndarray,
        sector_labels: np.ndarray,
        model_name: str = "model",
        model_version: str = "unknown",
    ) -> Dict[str, EvaluationResult]:
        """
        Evaluate model performance grouped by sector.

        Args:
            model:          Trained model.
            X_test:         Test features ``(N, seq, feats)``.
            y_test:         Test labels ``(N,)``.
            sector_labels:  String/int array ``(N,)`` identifying sector per sample.
            model_name:     Model identifier.
            model_version:  Model version.

        Returns:
            Dict mapping sector name → ``EvaluationResult``.
        """
        sectors = np.unique(sector_labels)
        results: Dict[str, EvaluationResult] = {}

        for sector in sectors:
            mask = sector_labels == sector
            logger.info(f"[EvaluatorV2] Sector '{sector}' — {mask.sum()} samples.")
            sector_dir = os.path.join(self.artifact_dir, f"sector_{sector}")
            evaluator = ProductionEvaluatorV2(
                artifact_dir=sector_dir,
                device=self.device,
                run_walk_forward=False,   # skip WF for sub-groups
            )
            results[str(sector)] = evaluator.evaluate(
                model=model,
                X_test=X_test[mask],
                y_test=y_test[mask],
                model_name=f"{model_name}@{sector}",
                model_version=model_version,
            )

        return results

    # ── Internal ──────────────────────────────────────────────────────────

    def _infer(
        self,
        model: BaseTimeSeriesClassifier,
        X: np.ndarray,
        threshold: float,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Run batched inference and return ``(y_prob_2d, y_pred, y_prob_pos)``."""
        X_tensor = torch.tensor(X, dtype=torch.float32)
        _, probs = model.predict(X_tensor, device=self.device)
        y_prob_2d = probs.numpy()
        y_prob_pos = y_prob_2d[:, 1] if y_prob_2d.ndim > 1 else y_prob_2d.flatten()
        y_pred = (y_prob_pos >= threshold).astype(int)
        return y_prob_2d, y_pred, y_prob_pos

    def _walk_forward(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
    ):
        def metric_fn(yt, yp, yprob):
            from ml_engine.evaluation.metrics import compute_classification_metrics
            m = compute_classification_metrics(yt, yp, yprob)
            return {k: v for k, v in m.to_dict().items() if not (isinstance(v, float) and math.isnan(v))}

        return run_walk_forward(y_true, y_pred, y_prob, metric_fn)

    def _safe_calibration(self, y_true: np.ndarray, y_prob: np.ndarray):
        from ml_engine.evaluation.calibration import compute_calibration
        return compute_calibration(y_true, y_prob)

    def _generate_plots(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        metrics,
        cm_result,
        calibration,
        multi_class: bool,
    ) -> Dict[str, str]:
        paths: Dict[str, str] = {}

        try:
            paths["confusion_matrix"] = plot_confusion_matrix(cm_result, self.plots_dir)
        except Exception as exc:
            logger.warning(f"[EvaluatorV2] confusion_matrix plot failed: {exc}")

        if multi_class:
            try:
                paths["roc_curve"] = plot_roc_curve(y_true, y_prob, metrics.roc_auc, self.plots_dir)
            except Exception as exc:
                logger.warning(f"[EvaluatorV2] roc_curve plot failed: {exc}")

            try:
                paths["pr_curve"] = plot_pr_curve(y_true, y_prob, metrics.pr_auc, self.plots_dir)
            except Exception as exc:
                logger.warning(f"[EvaluatorV2] pr_curve plot failed: {exc}")

            if calibration.prob_true:
                try:
                    paths["calibration"] = plot_calibration(calibration, self.plots_dir)
                except Exception as exc:
                    logger.warning(f"[EvaluatorV2] calibration plot failed: {exc}")

        try:
            paths["calibration_histogram"] = plot_calibration_histogram(y_prob, y_true, self.plots_dir)
        except Exception as exc:
            logger.warning(f"[EvaluatorV2] histogram plot failed: {exc}")

        try:
            paths["metric_summary"] = plot_metric_summary(metrics, self.plots_dir)
        except Exception as exc:
            logger.warning(f"[EvaluatorV2] metric_summary plot failed: {exc}")

        return paths
