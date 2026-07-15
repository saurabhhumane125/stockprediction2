"""
ml_engine/experiments/manager.py
─────────────────────────────────────────────────────────────────────────────
Manages queries, leaderboards, and comparisons for the Experiment System.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
from typing import List, Optional

from ml_engine.experiments.database import ExperimentDatabase
from ml_engine.experiments.schemas import RunRecord, ExperimentRecord

logger = logging.getLogger(__name__)


class ExperimentManager:
    """
    High-level API for querying runs, generating leaderboards, and comparisons.
    """
    def __init__(self, db_path: str = "ml_engine/experiments/tracking.db"):
        self.db = ExperimentDatabase(db_path)

    def list_experiments(self) -> List[ExperimentRecord]:
        return self.db.get_all_experiments()

    def get_experiment(self, name: str) -> Optional[ExperimentRecord]:
        return self.db.get_experiment_by_name(name)

    def list_runs(self, experiment_name: str) -> List[RunRecord]:
        exp = self.get_experiment(experiment_name)
        if not exp:
            return []
        return self.db.get_runs_by_experiment(exp.experiment_id)

    def get_run(self, run_id: str) -> Optional[RunRecord]:
        return self.db.get_run(run_id)

    def get_leaderboard(self, experiment_name: str, sort_metric: str = "f1_score", descending: bool = True) -> List[RunRecord]:
        """
        Rank runs within an experiment based on a specific metric.
        """
        runs = self.list_runs(experiment_name)
        # Filter out runs that don't have the metric
        runs_with_metric = [r for r in runs if sort_metric in r.metrics]
        
        runs_with_metric.sort(
            key=lambda x: x.metrics[sort_metric],
            reverse=descending
        )
        return runs_with_metric

    def compare_runs(self, run_ids: List[str]) -> List[RunRecord]:
        """
        Fetch multiple runs for side-by-side comparison.
        """
        runs = []
        for rid in run_ids:
            run = self.get_run(rid)
            if run:
                runs.append(run)
            else:
                logger.warning(f"Run {rid} not found for comparison.")
        return runs
