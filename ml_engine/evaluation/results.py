"""
ml_engine/evaluation/results.py
─────────────────────────────────────────────────────────────────────────────
Typed dataclasses for all evaluation outputs.

Using dataclasses (stdlib, no extra deps) with ``asdict()`` support so every
result can be trivially serialised to JSON / CSV.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# ── Metric containers ─────────────────────────────────────────────────────

@dataclass
class ClassificationMetrics:
    """All scalar classification metrics for a single evaluation run."""

    accuracy: float = 0.0
    balanced_accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    roc_auc: float = float("nan")
    pr_auc: float = float("nan")
    mcc: float = 0.0
    cohen_kappa: float = 0.0
    log_loss: float = float("nan")
    brier_score: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class ConfusionMatrixResult:
    """Raw and normalised confusion-matrix data."""

    raw: List[List[int]] = field(default_factory=list)       # [[TN, FP], [FN, TP]]
    normalized: List[List[float]] = field(default_factory=list)
    tn: int = 0
    fp: int = 0
    fn: int = 0
    tp: int = 0
    total_samples: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CalibrationResult:
    """Calibration analysis output."""

    ece: float = float("nan")    # Expected Calibration Error
    mce: float = float("nan")    # Maximum Calibration Error
    prob_true: List[float] = field(default_factory=list)   # reliability diagram y
    prob_pred: List[float] = field(default_factory=list)   # reliability diagram x
    bin_counts: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WalkForwardFold:
    """Metrics for a single rolling-window fold."""

    fold_index: int = 0
    start_index: int = 0
    end_index: int = 0
    n_samples: int = 0
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class WalkForwardResult:
    """Aggregated walk-forward validation output."""

    folds: List[WalkForwardFold] = field(default_factory=list)
    mean_metrics: Dict[str, float] = field(default_factory=dict)
    std_metrics: Dict[str, float] = field(default_factory=dict)
    n_folds: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_folds": self.n_folds,
            "mean_metrics": self.mean_metrics,
            "std_metrics": self.std_metrics,
            "folds": [
                {
                    "fold_index": f.fold_index,
                    "start_index": f.start_index,
                    "end_index": f.end_index,
                    "n_samples": f.n_samples,
                    "metrics": f.metrics,
                }
                for f in self.folds
            ],
        }


@dataclass
class ProductionDecision:
    """Result of the production acceptance gate."""

    verdict: str = "FAIL"           # "PASS" or "FAIL"
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationResult:
    """Top-level container aggregating all evaluation outputs for one model."""

    model_name: str = ""
    model_version: str = ""
    evaluation_timestamp: str = ""
    execution_time_seconds: float = 0.0
    n_test_samples: int = 0
    decision_threshold: float = 0.5

    metrics: ClassificationMetrics = field(default_factory=ClassificationMetrics)
    confusion_matrix: ConfusionMatrixResult = field(default_factory=ConfusionMatrixResult)
    calibration: CalibrationResult = field(default_factory=CalibrationResult)
    walk_forward: Optional[WalkForwardResult] = None
    decision: ProductionDecision = field(default_factory=ProductionDecision)

    # Paths to saved artefacts
    artifact_paths: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "evaluation_timestamp": self.evaluation_timestamp,
            "execution_time_seconds": self.execution_time_seconds,
            "n_test_samples": self.n_test_samples,
            "decision_threshold": self.decision_threshold,
            "metrics": self.metrics.to_dict(),
            "confusion_matrix": self.confusion_matrix.to_dict(),
            "calibration": self.calibration.to_dict(),
            "walk_forward": self.walk_forward.to_dict() if self.walk_forward else None,
            "decision": self.decision.to_dict(),
            "artifact_paths": self.artifact_paths,
        }
        return d
