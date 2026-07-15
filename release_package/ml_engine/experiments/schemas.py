"""
ml_engine/experiments/schemas.py
─────────────────────────────────────────────────────────────────────────────
Data schemas and TypedDicts for the Experiment Tracking System.
─────────────────────────────────────────────────────────────────────────────
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid


@dataclass
class ExperimentRecord:
    experiment_id: str
    name: str
    description: str
    created_at: str


@dataclass
class RunRecord:
    run_id: str
    experiment_id: str
    run_name: str
    status: str  # "RUNNING", "COMPLETED", "FAILED"
    created_at: str
    end_time: Optional[str] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(cls, experiment_id: str, run_name: str) -> "RunRecord":
        return cls(
            run_id=str(uuid.uuid4()),
            experiment_id=experiment_id,
            run_name=run_name,
            status="RUNNING",
            created_at=datetime.now(timezone.utc).isoformat()
        )
