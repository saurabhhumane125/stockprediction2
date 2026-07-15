"""
ml_engine/training/callbacks.py
─────────────────────────────────────────────────────────────────────────────
Framework-independent callback interfaces for the training pipeline.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import time
from typing import Dict, Any, Optional

from ml_engine.experiments.tracker import ExperimentTracker

logger = logging.getLogger(__name__)


class TrainingCallback:
    """Base interface for all training callbacks."""
    
    def on_train_begin(self, config: Dict[str, Any]):
        pass

    def on_epoch_begin(self, epoch: int):
        pass

    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        pass

    def on_train_end(self, metrics: Dict[str, float], model_path: Optional[str] = None):
        pass

    def on_early_stopping(self, epoch: int, best_epoch: int, best_metric: float):
        pass


class ExperimentTrackingCallback(TrainingCallback):
    """
    Connects the training loop to the SQLite Experiment Tracking system.
    """
    def __init__(self, tracker: ExperimentTracker):
        self.tracker = tracker
        self.epoch_start_time = 0.0

    def on_train_begin(self, config: Dict[str, Any]):
        logger.info(f"[ExperimentTrackingCallback] Starting run {self.tracker.run.run_id}")
        self.tracker.log_parameters(config)

    def on_epoch_begin(self, epoch: int):
        self.epoch_start_time = time.time()

    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        duration = time.time() - self.epoch_start_time
        # In a real deep tracking system we might log metrics per epoch.
        # For our tracker, we'll log the latest metrics. 
        # Overwrites previous epoch metrics.
        metrics_with_duration = {**metrics, "epoch_duration_s": duration}
        self.tracker.log_metrics(metrics_with_duration)

    def on_train_end(self, metrics: Dict[str, float], model_path: Optional[str] = None):
        logger.info("[ExperimentTrackingCallback] Training ended. Logging final metrics and artifacts.")
        self.tracker.log_metrics(metrics)
        if model_path:
            self.tracker.log_artifacts({"best_model": model_path})
        self.tracker.end_run("COMPLETED")

    def on_early_stopping(self, epoch: int, best_epoch: int, best_metric: float):
        logger.info(f"[ExperimentTrackingCallback] Early stopping at epoch {epoch}")
        self.tracker.log_metadata({
            "early_stopping": True,
            "stopped_epoch": epoch,
            "best_epoch": best_epoch,
            "best_metric": best_metric
        })
