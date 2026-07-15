"""
ml_engine/evaluation/walk_forward.py
─────────────────────────────────────────────────────────────────────────────
Rolling-window (walk-forward) evaluation.

Splits the test set into consecutive windows and computes metrics on each
fold independently, then aggregates mean ± std across all folds.

Configuration is read from ``EvaluationConfig``:
  • ``WALK_FORWARD_WINDOW``        – samples per fold
  • ``WALK_FORWARD_STEP``          – slide step between folds
  • ``WALK_FORWARD_MIN_SAMPLES``   – minimum fold size to include
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Callable

import numpy as np

from ml_engine.config.evaluation_config import evaluation_config
from ml_engine.evaluation.results import WalkForwardFold, WalkForwardResult

logger = logging.getLogger(__name__)


def run_walk_forward(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    metric_fn: Callable[[np.ndarray, np.ndarray, np.ndarray], dict],
    window: int | None = None,
    step: int | None = None,
    min_samples: int | None = None,
) -> WalkForwardResult:
    """
    Execute rolling-window validation over the provided arrays.

    Args:
        y_true:     Ground-truth labels ``(N,)``.
        y_pred:     Predicted labels    ``(N,)``.
        y_prob:     Probabilities       ``(N,)`` or ``(N, C)``.
        metric_fn:  Callable accepting ``(y_true, y_pred, y_prob)``
                    and returning a ``Dict[str, float]``.
        window:     Samples per fold (default ``EvaluationConfig.WALK_FORWARD_WINDOW``).
        step:       Slide step (default ``EvaluationConfig.WALK_FORWARD_STEP``).
        min_samples: Minimum fold size to include in results.

    Returns:
        ``WalkForwardResult`` with per-fold and aggregate metrics.
    """
    window = window or evaluation_config.WALK_FORWARD_WINDOW
    step = step or evaluation_config.WALK_FORWARD_STEP
    min_samples = min_samples or evaluation_config.WALK_FORWARD_MIN_SAMPLES

    n = len(y_true)
    folds: list[WalkForwardFold] = []
    fold_idx = 0

    start = 0
    while start < n:
        end = min(start + window, n)
        size = end - start

        if size < min_samples:
            break

        yt = y_true[start:end]
        yp = y_pred[start:end]
        yprob = y_prob[start:end]

        try:
            fold_metrics = metric_fn(yt, yp, yprob)
        except Exception as exc:
            logger.warning(f"[WalkForward] Fold {fold_idx} metric error: {exc}")
            fold_metrics = {}

        folds.append(
            WalkForwardFold(
                fold_index=fold_idx,
                start_index=int(start),
                end_index=int(end),
                n_samples=size,
                metrics=fold_metrics,
            )
        )
        fold_idx += 1
        start += step

    if not folds:
        logger.warning("[WalkForward] No folds generated — dataset may be too small.")
        return WalkForwardResult(n_folds=0)

    # Aggregate mean / std across folds
    all_keys = set(k for f in folds for k in f.metrics)
    mean_metrics: dict[str, float] = {}
    std_metrics: dict[str, float] = {}

    for key in sorted(all_keys):
        values = [f.metrics[key] for f in folds if key in f.metrics and not _is_nan(f.metrics[key])]
        if values:
            mean_metrics[key] = float(np.mean(values))
            std_metrics[key] = float(np.std(values))
        else:
            mean_metrics[key] = float("nan")
            std_metrics[key] = float("nan")

    logger.info(f"[WalkForward] Completed {len(folds)} folds (window={window}, step={step}).")
    return WalkForwardResult(
        folds=folds,
        mean_metrics=mean_metrics,
        std_metrics=std_metrics,
        n_folds=len(folds),
    )


def _is_nan(value) -> bool:
    try:
        return np.isnan(float(value))
    except (TypeError, ValueError):
        return False
