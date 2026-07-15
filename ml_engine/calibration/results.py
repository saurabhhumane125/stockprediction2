"""
ml_engine/calibration/results.py
─────────────────────────────────────────────────────────────────────────────
Typed dataclasses for tracking calibration metrics and results.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass
class CalibrationMetrics:
    """Metrics tracking the quality of probability calibration."""
    ece: float           # Expected Calibration Error
    mce: float           # Maximum Calibration Error
    brier_score: float   # Brier Score
    log_loss: float      # Log Loss

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class CalibrationResult:
    """Aggregated results from a calibration process."""
    method: str
    before_metrics: CalibrationMetrics
    after_metrics: CalibrationMetrics
    execution_time_seconds: float
    artifact_paths: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["before_metrics"] = self.before_metrics.to_dict()
        d["after_metrics"] = self.after_metrics.to_dict()
        return d
