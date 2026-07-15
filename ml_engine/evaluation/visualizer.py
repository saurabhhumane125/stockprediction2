"""
ml_engine/evaluation/visualizer.py
─────────────────────────────────────────────────────────────────────────────
Evaluation visualisation layer.

Generates production-quality charts:
  • Confusion matrix (raw + normalised heat-maps)
  • ROC curve
  • Precision-Recall curve
  • Calibration / reliability diagram
  • Calibration histogram (prediction confidence distribution)
  • Metric summary bar chart

All functions write PNG files to a configurable ``plots_dir`` and return
the saved path so callers can populate ``EvaluationResult.artifact_paths``.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import os
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")   # headless backend — no display required
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import seaborn as sns
from sklearn.metrics import roc_curve, precision_recall_curve

from ml_engine.config.evaluation_config import evaluation_config
from ml_engine.evaluation.results import CalibrationResult, ClassificationMetrics, ConfusionMatrixResult

logger = logging.getLogger(__name__)

_DPI = evaluation_config.PLOT_DPI


def _save(fig: plt.Figure, path: str) -> str:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    fig.savefig(path, dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.debug(f"[Visualizer] Saved → {path}")
    return path


# ── Confusion Matrix ──────────────────────────────────────────────────────

def plot_confusion_matrix(
    cm_result: ConfusionMatrixResult,
    plots_dir: str,
    class_names: Optional[List[str]] = None,
) -> str:
    """
    Plot raw and row-normalised confusion matrices side-by-side.

    Returns:
        Absolute path to the saved PNG.
    """
    raw = np.array(cm_result.raw)
    norm = np.array(cm_result.normalized)
    labels = class_names or [str(i) for i in range(raw.shape[0])]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, data, fmt, title in zip(
        axes,
        [raw, norm],
        ["d", ".2f"],
        ["Confusion Matrix (raw)", "Confusion Matrix (normalised)"],
    ):
        sns.heatmap(
            data, annot=True, fmt=fmt, cmap="Blues",
            xticklabels=labels, yticklabels=labels,
            ax=ax, cbar=False,
        )
        ax.set_title(title)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
    fig.tight_layout()
    return _save(fig, os.path.join(plots_dir, "confusion_matrix.png"))


# ── ROC Curve ─────────────────────────────────────────────────────────────

def plot_roc_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    roc_auc: float,
    plots_dir: str,
) -> str:
    """
    Plot the ROC curve with AUC annotation.

    Returns:
        Absolute path to the saved PNG.
    """
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="#2563EB", lw=2, label=f"ROC (AUC = {roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1)
    ax.fill_between(fpr, tpr, alpha=0.08, color="#2563EB")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    return _save(fig, os.path.join(plots_dir, "roc_curve.png"))


# ── PR Curve ──────────────────────────────────────────────────────────────

def plot_pr_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    pr_auc: float,
    plots_dir: str,
) -> str:
    """
    Plot the Precision-Recall curve with AUC annotation.

    Returns:
        Absolute path to the saved PNG.
    """
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(recall, precision, color="#7C3AED", lw=2, label=f"PR (AUC = {pr_auc:.4f})")
    baseline = y_true.mean()
    ax.axhline(baseline, color="gray", linestyle="--", lw=1, label=f"Baseline ({baseline:.2f})")
    ax.fill_between(recall, precision, alpha=0.08, color="#7C3AED")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curve")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    return _save(fig, os.path.join(plots_dir, "pr_curve.png"))


# ── Calibration ───────────────────────────────────────────────────────────

def plot_calibration(
    calibration: CalibrationResult,
    plots_dir: str,
) -> str:
    """
    Plot reliability diagram (calibration curve).

    Returns:
        Absolute path to the saved PNG.
    """
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(
        calibration.prob_pred, calibration.prob_true,
        marker="o", lw=2, color="#059669",
        label=f"Model (ECE={calibration.ece:.4f}, MCE={calibration.mce:.4f})",
    )
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", lw=1, label="Perfect calibration")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.set_title("Calibration Curve (Reliability Diagram)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    return _save(fig, os.path.join(plots_dir, "calibration_curve.png"))


def plot_calibration_histogram(
    y_prob: np.ndarray,
    y_true: np.ndarray,
    plots_dir: str,
) -> str:
    """
    Plot prediction probability distribution by class.

    Returns:
        Absolute path to the saved PNG.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    for cls, color, label in [(0, "#DC2626", "Class 0 (HOLD/SELL)"), (1, "#16A34A", "Class 1 (BUY)")]:
        mask = y_true == cls
        if mask.any():
            ax.hist(y_prob[mask], bins=30, alpha=0.6, color=color, label=label, density=True)
    ax.set_xlabel("Predicted Probability (positive class)")
    ax.set_ylabel("Density")
    ax.set_title("Prediction Probability Distribution by Class")
    ax.legend()
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    return _save(fig, os.path.join(plots_dir, "calibration_histogram.png"))


# ── Metric Summary ────────────────────────────────────────────────────────

def plot_metric_summary(
    metrics: ClassificationMetrics,
    plots_dir: str,
) -> str:
    """
    Plot a horizontal bar chart of the key scalar metrics.

    Returns:
        Absolute path to the saved PNG.
    """
    names = ["Accuracy", "Balanced Acc.", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC", "MCC"]
    values = [
        metrics.accuracy, metrics.balanced_accuracy,
        metrics.precision, metrics.recall,
        metrics.f1, metrics.roc_auc,
        metrics.pr_auc, metrics.mcc,
    ]

    # Filter NaN entries
    pairs = [(n, v) for n, v in zip(names, values) if not (isinstance(v, float) and np.isnan(v))]
    if not pairs:
        logger.warning("[Visualizer] No valid metrics for summary chart.")
        return ""
    names, values = zip(*pairs)

    colors = ["#22C55E" if v >= 0.6 else "#F97316" if v >= 0.5 else "#EF4444" for v in values]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(names, values, color=colors, edgecolor="white", height=0.6)
    ax.set_xlim(0, 1)
    ax.axvline(0.5, color="gray", linestyle="--", lw=1)
    ax.set_xlabel("Score")
    ax.set_title("Evaluation Metric Summary")
    for bar, v in zip(bars, values):
        ax.text(
            min(v + 0.01, 0.95), bar.get_y() + bar.get_height() / 2,
            f"{v:.4f}", va="center", fontsize=9,
        )
    fig.tight_layout()
    return _save(fig, os.path.join(plots_dir, "metric_summary.png"))
