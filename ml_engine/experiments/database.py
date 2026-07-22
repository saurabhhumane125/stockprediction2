"""
ml_engine/experiments/database.py
─────────────────────────────────────────────────────────────────────────────
SQLite database wrapper for Experiment Tracking.
─────────────────────────────────────────────────────────────────────────────
"""
import json
import logging
import sqlite3
import os
from typing import List, Dict, Any, Optional

from ml_engine.experiments.schemas import ExperimentRecord, RunRecord

logger = logging.getLogger(__name__)


class ExperimentDatabase:
    """
    Handles SQLite connections and queries for experiment tracking.
    """
    def __init__(self, db_path: str = "ml_engine/experiments/tracking.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Experiments Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Runs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    run_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    end_time TEXT,
                    FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
                )
            """)
            
            # EAV Table for Metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS run_metadata (
                    run_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    PRIMARY KEY (run_id, key),
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            
            # EAV Table for Parameters
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS run_parameters (
                    run_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    PRIMARY KEY (run_id, key),
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            
            # EAV Table for Metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS run_metrics (
                    run_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value REAL,
                    PRIMARY KEY (run_id, key),
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            
            # EAV Table for Artifacts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS run_artifacts (
                    run_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    path TEXT NOT NULL,
                    PRIMARY KEY (run_id, key),
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            conn.commit()

    def create_experiment(self, experiment: ExperimentRecord):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO experiments (experiment_id, name, description, created_at) VALUES (?, ?, ?, ?)",
                (experiment.experiment_id, experiment.name, experiment.description, experiment.created_at)
            )
            conn.commit()

    def get_experiment_by_name(self, name: str) -> Optional[ExperimentRecord]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM experiments WHERE name = ?", (name,)).fetchone()
            if row:
                return ExperimentRecord(**dict(row))
            return None

    def create_run(self, run: RunRecord):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO runs (run_id, experiment_id, run_name, status, created_at, end_time) VALUES (?, ?, ?, ?, ?, ?)",
                (run.run_id, run.experiment_id, run.run_name, run.status, run.created_at, run.end_time)
            )
            conn.commit()

    def update_run_status(self, run_id: str, status: str, end_time: str):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE runs SET status = ?, end_time = ? WHERE run_id = ?",
                (status, end_time, run_id)
            )
            conn.commit()

    def _safe_serialize(self, v: Any) -> str:
        try:
            import numpy as np
            if isinstance(v, np.ndarray):
                return json.dumps(v.tolist())
        except ImportError:
            pass

        try:
            import torch
            if isinstance(v, torch.Tensor):
                if v.numel() == 1:
                    return str(v.item())
                return json.dumps(v.detach().cpu().numpy().tolist())
        except ImportError:
            pass

        if isinstance(v, (dict, list, tuple)):
            try:
                return json.dumps(v)
            except TypeError:
                pass

        return str(v)

    def log_metadata(self, run_id: str, metadata: Dict[str, Any]):
        with self._get_conn() as conn:
            for k, v in metadata.items():
                val_str = self._safe_serialize(v)
                conn.execute(
                    "INSERT OR REPLACE INTO run_metadata (run_id, key, value) VALUES (?, ?, ?)",
                    (run_id, k, val_str)
                )
            conn.commit()

    def log_parameters(self, run_id: str, parameters: Dict[str, Any]):
        with self._get_conn() as conn:
            for k, v in parameters.items():
                val_str = self._safe_serialize(v)
                conn.execute(
                    "INSERT OR REPLACE INTO run_parameters (run_id, key, value) VALUES (?, ?, ?)",
                    (run_id, k, val_str)
                )
            conn.commit()

    def log_metrics(self, run_id: str, metrics: Dict[str, Any]):
        scalar_types = (int, float, bool)
        try:
            import numpy as np
            scalar_types = scalar_types + (np.number, np.bool_)
        except ImportError:
            pass

        scalars = {}
        complex_metrics = {}

        for k, v in metrics.items():
            if isinstance(v, scalar_types):
                scalars[k] = v
            else:
                try:
                    import torch
                    if isinstance(v, torch.Tensor) and v.numel() == 1:
                        scalars[k] = v.item()
                        continue
                except ImportError:
                    pass
                complex_metrics[k] = v

        with self._get_conn() as conn:
            for k, v in scalars.items():
                conn.execute(
                    "INSERT OR REPLACE INTO run_metrics (run_id, key, value) VALUES (?, ?, ?)",
                    (run_id, k, float(v))
                )
            conn.commit()

        if complex_metrics:
            self.log_metadata(run_id, complex_metrics)
            conn.commit()

    def log_artifacts(self, run_id: str, artifacts: Dict[str, str]):
        with self._get_conn() as conn:
            for k, path in artifacts.items():
                conn.execute(
                    "INSERT OR REPLACE INTO run_artifacts (run_id, key, path) VALUES (?, ?, ?)",
                    (run_id, k, path)
                )
            conn.commit()

    def get_run(self, run_id: str) -> Optional[RunRecord]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
            if not row:
                return None
                
            run_dict = dict(row)
            
            # Fetch EAV tables
            meta_rows = conn.execute("SELECT key, value FROM run_metadata WHERE run_id = ?", (run_id,)).fetchall()
            param_rows = conn.execute("SELECT key, value FROM run_parameters WHERE run_id = ?", (run_id,)).fetchall()
            metric_rows = conn.execute("SELECT key, value FROM run_metrics WHERE run_id = ?", (run_id,)).fetchall()
            artifact_rows = conn.execute("SELECT key, path FROM run_artifacts WHERE run_id = ?", (run_id,)).fetchall()
            
            run = RunRecord(**run_dict)
            
            def _safe_deserialize(val: str) -> Any:
                try:
                    return json.loads(val)
                except (ValueError, TypeError):
                    return val

            run.metadata = {r["key"]: _safe_deserialize(r["value"]) for r in meta_rows}
            run.parameters = {r["key"]: _safe_deserialize(r["value"]) for r in param_rows}
            run.metrics = {r["key"]: float(r["value"]) if r["value"] is not None else 0.0 for r in metric_rows}
            run.artifacts = {r["key"]: r["path"] for r in artifact_rows}
            
            return run

    def get_runs_by_experiment(self, experiment_id: str) -> List[RunRecord]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT run_id FROM runs WHERE experiment_id = ?", (experiment_id,)).fetchall()
            return [self.get_run(r["run_id"]) for r in rows]
            
    def get_all_experiments(self) -> List[ExperimentRecord]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM experiments ORDER BY created_at DESC").fetchall()
            return [ExperimentRecord(**dict(r)) for r in rows]
