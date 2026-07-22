"""
ml_engine/experiments/tracker.py
─────────────────────────────────────────────────────────────────────────────
High-level tracker API intended for injection into Training/Evaluation hooks.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import platform
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from ml_engine.experiments.database import ExperimentDatabase
from ml_engine.experiments.schemas import ExperimentRecord, RunRecord

logger = logging.getLogger(__name__)


class ExperimentTracker:
    """
    Active tracker for an ongoing ML run. 
    Maintains run state and delegates storage to ExperimentDatabase.
    """
    def __init__(self, experiment_name: str, run_name: str, db_path: str = "ml_engine/experiments/tracking.db"):
        self.db = ExperimentDatabase(db_path)
        
        # Ensure experiment exists
        exp = self.db.get_experiment_by_name(experiment_name)
        if not exp:
            exp = ExperimentRecord(
                experiment_id=str(uuid.uuid4()),
                name=experiment_name,
                description="",
                created_at=datetime.now(timezone.utc).isoformat()
            )
            self.db.create_experiment(exp)
            
        # Create Run
        self.run = RunRecord.create(exp.experiment_id, run_name)
        self.db.create_run(self.run)
        
        # Log System Metadata immediately
        self._log_system_metadata()
        logger.info(f"[ExperimentTracker] Started run {self.run.run_id} in experiment '{experiment_name}'")

    def _log_system_metadata(self):
        meta = {
            "os": platform.platform(),
            "python_version": sys.version.split()[0],
            "hostname": platform.node()
        }
        
        # Attempt to get PyTorch version if available
        try:
            import torch
            meta["torch_version"] = torch.__version__
            meta["cuda_available"] = str(torch.cuda.is_available())
        except ImportError:
            pass
            
        self.log_metadata(meta)

    def log_metadata(self, metadata: Dict[str, Any]):
        self.run.metadata.update(metadata)
        self.db.log_metadata(self.run.run_id, metadata)

    def log_parameters(self, params: Dict[str, Any]):
        self.run.parameters.update(params)
        self.db.log_parameters(self.run.run_id, params)

    def log_metrics(self, metrics: Dict[str, Any]):
        self.run.metrics.update(metrics)
        self.db.log_metrics(self.run.run_id, metrics)

    def log_artifacts(self, artifacts: Dict[str, str]):
        self.run.artifacts.update(artifacts)
        self.db.log_artifacts(self.run.run_id, artifacts)

    def end_run(self, status: str = "COMPLETED"):
        self.run.status = status
        self.run.end_time = datetime.now(timezone.utc).isoformat()
        self.db.update_run_status(self.run.run_id, self.run.status, self.run.end_time)
        logger.info(f"[ExperimentTracker] Ended run {self.run.run_id} with status {status}")
        
    def fail_run(self):
        self.end_run("FAILED")
