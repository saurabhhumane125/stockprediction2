"""
ml_engine/evaluation/calibration.py
─────────────────────────────────────────────────────────────────────────────
Calibration analysis — analysis only, no calibration correction applied.

Computes:
  • Expected Calibration Error (ECE)
  • Maximum Calibration Error (MCE)
  • Reliability diagram data (prob_true vs prob_pred per bin)
  • Bin sample counts
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging

import numpy as np
from sklearn.calibration import calibration_curve

from ml_engine.config.evaluation_config import evaluation_config
from ml_engine.evaluation.results import CalibrationResult

logger = logging.getLogger(__name__)


def compute_calibration(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int | None = None,
) -> CalibrationResult:
    """
    Compute calibration metrics from predicted probabilities.

    Args:
        y_true:  Ground-truth binary labels  ``(N,)``.
        y_prob:  Positive-class probabilities ``(N,)``.
        n_bins:  Number of calibration bins.
                 Defaults to ``EvaluationConfig.NUM_CALIBRATION_BINS``.

    Returns:
        Populated ``CalibrationResult``.
    """
    if len(np.unique(y_true)) < 2:
        logger.warning("[Calibration] Only one class in y_true — calibration metrics set to NaN.")
        return CalibrationResult()

    n_bins = n_bins or evaluation_config.NUM_CALIBRATION_BINS

    prob_true, prob_pred = calibration_curve(
        y_true, y_prob, n_bins=n_bins, strategy="uniform"
    )

    # ECE: weighted average |predicted_prob - fraction_positive| per bin
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_counts: list[int] = []
    abs_errors: list[float] = []

    for i in range(len(prob_pred)):
        low = bin_edges[i]
        high = bin_edges[i + 1]
        mask = (y_prob >= low) & (y_prob < high)
        n = int(mask.sum())
        bin_counts.append(n)
        if n > 0:
            abs_errors.append(abs(prob_true[i] - prob_pred[i]) * n)

    total = sum(bin_counts)
    ece = float(sum(abs_errors) / total) if total > 0 else float("nan")

    # MCE: maximum per-bin |error|
    mce = float(np.max(np.abs(prob_true - prob_pred))) if len(prob_true) > 0 else float("nan")

    return CalibrationResult(
        ece=round(ece, 6),
        mce=round(mce, 6),
        prob_true=prob_true.tolist(),
        prob_pred=prob_pred.tolist(),
        bin_counts=bin_counts,
    )
