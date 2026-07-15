"""
ml_engine/optimization/results.py
─────────────────────────────────────────────────────────────────────────────
Typed dataclasses for tracking optimization results.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class ParameterImportance:
    """Importance of a single hyperparameter."""
    name: str
    importance: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TrialRecord:
    """Record of a single optimization trial."""
    number: int
    state: str
    value: Optional[float]
    datetime_start: str
    datetime_complete: Optional[str]
    params: Dict[str, Any]
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationResult:
    """Aggregated results from an Optuna study."""
    study_name: str
    n_trials: int
    best_value: Optional[float]
    best_params: Dict[str, Any]
    best_trial_number: Optional[int]
    optimization_time_seconds: float = 0.0
    
    top_n_trials: List[TrialRecord] = field(default_factory=list)
    failed_trials: List[TrialRecord] = field(default_factory=list)
    parameter_importance: List[ParameterImportance] = field(default_factory=list)
    
    artifact_paths: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["top_n_trials"] = [t.to_dict() for t in self.top_n_trials]
        d["failed_trials"] = [t.to_dict() for t in self.failed_trials]
        d["parameter_importance"] = [p.to_dict() for p in self.parameter_importance]
        return d
