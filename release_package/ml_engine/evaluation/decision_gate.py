"""
ml_engine/evaluation/decision_gate.py
─────────────────────────────────────────────────────────────────────────────
Production Decision Gate.

Evaluates a ``ClassificationMetrics`` + ``CalibrationResult`` against
configurable acceptance thresholds from ``EvaluationConfig`` and returns a
typed ``ProductionDecision``.

All thresholds are configuration-driven — nothing is hard-coded.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import math
from typing import List, Tuple

from ml_engine.config.evaluation_config import evaluation_config
from ml_engine.evaluation.results import CalibrationResult, ClassificationMetrics, ProductionDecision

logger = logging.getLogger(__name__)

# Each check: (description, actual_value, threshold, mode)
# mode "min" → actual must be >= threshold
# mode "max" → actual must be <= threshold
_CheckSpec = Tuple[str, float, float, str]


def evaluate_production_readiness(
    metrics: ClassificationMetrics,
    calibration: CalibrationResult,
) -> ProductionDecision:
    """
    Decide whether a trained model meets production acceptance criteria.

    A model receives verdict ``"PASS"`` only when **every** enabled threshold
    is satisfied. If any threshold fails the verdict is ``"FAIL"``.

    Args:
        metrics:     Computed classification metrics for the test set.
        calibration: Calibration analysis result.

    Returns:
        ``ProductionDecision`` with verdict, per-check breakdown, and reasons.
    """
    cfg = evaluation_config

    checks: List[_CheckSpec] = [
        ("ROC-AUC",          metrics.roc_auc,          cfg.MIN_ROC_AUC,      "min"),
        ("F1",               metrics.f1,               cfg.MIN_F1,           "min"),
        ("Accuracy",         metrics.accuracy,         cfg.MIN_ACCURACY,     "min"),
        ("PR-AUC",           metrics.pr_auc,           cfg.MIN_PR_AUC,       "min"),
        ("Log-Loss",         metrics.log_loss,         cfg.MAX_LOG_LOSS,     "max"),
        ("Brier Score",      metrics.brier_score,      cfg.MAX_BRIER_SCORE,  "max"),
        ("ECE",              calibration.ece,          cfg.MAX_ECE,          "max"),
    ]

    passed: List[str] = []
    failed: List[str] = []
    reasons: List[str] = []

    for name, value, threshold, mode in checks:
        if math.isnan(value):
            # NaN metrics (e.g. single-class set) are treated as failures
            failed.append(name)
            reasons.append(f"{name} = NaN (could not be computed — likely single-class labels).")
            continue

        if mode == "min":
            ok = value >= threshold
            direction = f">= {threshold:.4f}"
        else:
            ok = value <= threshold
            direction = f"<= {threshold:.4f}"

        if ok:
            passed.append(name)
        else:
            failed.append(name)
            reasons.append(
                f"{name} = {value:.4f} does not satisfy threshold {direction}."
            )

    verdict = "PASS" if len(failed) == 0 else "FAIL"
    logger.info(
        f"[DecisionGate] Verdict={verdict} | "
        f"passed={len(passed)} failed={len(failed)}"
    )
    return ProductionDecision(
        verdict=verdict,
        passed_checks=passed,
        failed_checks=failed,
        reasons=reasons,
    )
