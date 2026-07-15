"""
ml_engine/optimization/study_manager.py
─────────────────────────────────────────────────────────────────────────────
Manages Optuna study creation and resumption with SQLite storage.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
from typing import Optional
import optuna

from ml_engine.optimization.callbacks import build_pruner

logger = logging.getLogger(__name__)


class StudyManager:
    """
    Encapsulates Optuna study operations (SQLite storage, pruning strategy, study creation).
    """

    def __init__(self, study_name: str, storage_path: str, pruner_type: str = "median") -> None:
        """
        Args:
            study_name: Unique identifier for the optimization study.
            storage_path: Path to the SQLite DB file (e.g. 'ml_engine/artifacts/optimization.db')
            pruner_type: Pruning strategy.
        """
        self.study_name = study_name
        self.storage_path = storage_path
        self.pruner_type = pruner_type
        
        # Ensure directory exists for sqlite file
        os.makedirs(os.path.dirname(self.storage_path) if os.path.dirname(self.storage_path) else ".", exist_ok=True)
        self.storage_url = f"sqlite:///{self.storage_path}"
        
    def get_study(self, direction: str = "maximize") -> optuna.Study:
        """
        Load or create the study.

        Args:
            direction: Optimization direction ("maximize" or "minimize").
            
        Returns:
            An active Optuna Study instance.
        """
        pruner = build_pruner(self.pruner_type)
        
        study = optuna.create_study(
            study_name=self.study_name,
            storage=self.storage_url,
            load_if_exists=True,
            direction=direction,
            pruner=pruner
        )
        
        logger.info(f"[Optimization] Loaded study '{self.study_name}' from {self.storage_url}")
        logger.info(f"[Optimization] Study currently has {len(study.trials)} trials.")
        
        return study
