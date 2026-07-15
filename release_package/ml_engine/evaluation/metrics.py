"""
ml_engine/evaluation/metrics.py
─────────────────────────────────────────────────────────────────────────────
Pure-function metric computation layer.

All functions accept numpy arrays only — no framework coupling.
Every metric is guarded against single-class label edge cases.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    cohen_kappa_score,
    f1_score,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
)

from ml_engine.evaluation.results import ClassificationMetrics

logger = logging.getLogger(__name__)

_MULTI_CLASS_GUARD = "Only one class present in y_true — metric set to NaN."


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
    average: str = "binary",
) -> ClassificationMetrics:
    """
    Compute the full production classification metric suite.

    Args:
        y_true:    Ground-truth integer labels  ``(N,)``.
        y_pred:    Predicted class labels       ``(N,)``.
        y_prob:    Positive-class probabilities ``(N,)``
                   (binary) or ``(N, C)`` (multiclass).
        threshold: Decision threshold (used only if caller passes binary probs).
        average:   Sklearn averaging strategy for precision/recall/F1.

    Returns:
        Populated ``ClassificationMetrics`` dataclass.
    """
    multi_class_safe = len(np.unique(y_true)) > 1

    acc = float(accuracy_score(y_true, y_pred))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, average=average, zero_division=0))
    rec = float(recall_score(y_true, y_pred, average=average, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, average=average, zero_division=0))
    mcc = float(matthews_corrcoef(y_true, y_pred))
    kappa = float(cohen_kappa_score(y_true, y_pred))
    brier = float(brier_score_loss(y_true, y_prob if y_prob.ndim == 1 else y_prob[:, 1]))

    if multi_class_safe:
        try:
            roc_auc = float(
                roc_auc_score(
                    y_true,
                    y_prob,
                    multi_class="ovr" if y_prob.ndim > 1 else "raise",
                )
            )
        except Exception:
            roc_auc = float("nan")

        try:
            pr_auc = float(
                average_precision_score(
                    y_true,
                    y_prob if y_prob.ndim == 1 else y_prob[:, 1],
                )
            )
        except Exception:
            pr_auc = float("nan")

        try:
            ll = float(
                log_loss(
                    y_true,
                    y_prob if y_prob.ndim > 1 else np.column_stack([1 - y_prob, y_prob]),
                )
            )
        except Exception:
            ll = float("nan")
    else:
        logger.warning(_MULTI_CLASS_GUARD)
        roc_auc = pr_auc = ll = float("nan")

    return ClassificationMetrics(
        accuracy=acc,
        balanced_accuracy=bal_acc,
        precision=prec,
        recall=rec,
        f1=f1,
        roc_auc=roc_auc,
        pr_auc=pr_auc,
        mcc=mcc,
        cohen_kappa=kappa,
        log_loss=ll,
        brier_score=brier,
    )


def compute_roc_data(
    y_true: np.ndarray, y_prob: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute ROC curve arrays.

    Returns:
        ``(fpr, tpr, thresholds)``
    """
    return roc_curve(y_true, y_prob)


def compute_pr_data(
    y_true: np.ndarray, y_prob: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute Precision-Recall curve arrays.

    Returns:
        ``(precision, recall, thresholds)``
    """
    return precision_recall_curve(y_true, y_prob)
