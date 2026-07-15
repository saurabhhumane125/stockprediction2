"""
ml_engine/evaluation/confusion.py
─────────────────────────────────────────────────────────────────────────────
Confusion-matrix computation and export.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import logging
import os
from typing import List, Optional

import numpy as np
from sklearn.metrics import confusion_matrix

from ml_engine.evaluation.results import ConfusionMatrixResult

logger = logging.getLogger(__name__)


def compute_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[int]] = None,
) -> ConfusionMatrixResult:
    """
    Compute raw and row-normalised confusion matrix.

    Args:
        y_true:  Ground-truth labels.
        y_pred:  Predicted labels.
        labels:  Explicit label ordering (defaults to sorted unique values).

    Returns:
        Populated ``ConfusionMatrixResult``.
    """
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    raw = cm.tolist()

    with np.errstate(divide="ignore", invalid="ignore"):
        norm = np.where(cm.sum(axis=1, keepdims=True) == 0, 0, cm / cm.sum(axis=1, keepdims=True))
    normalized = np.round(norm, 4).tolist()

    # Unpack binary-specific TN/FP/FN/TP
    tn = fp = fn = tp = 0
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel().tolist()

    return ConfusionMatrixResult(
        raw=raw,
        normalized=normalized,
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
        total_samples=int(len(y_true)),
    )


def save_confusion_matrix_json(result: ConfusionMatrixResult, path: str) -> None:
    """
    Persist the confusion matrix result as JSON.

    Args:
        result: ``ConfusionMatrixResult`` to serialise.
        path:   Target file path (e.g. ``artifacts/confusion_matrix.json``).
    """
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(result.to_dict(), f, indent=4)
    logger.debug(f"[ConfusionMatrix] Saved JSON → {path}")
