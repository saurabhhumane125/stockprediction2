import os
import time
import json
import logging
import pandas as pd
from typing import List, Dict, Any, Optional

import numpy as np

from ml_engine.config.pipeline_config import pipeline_config
from ml_engine.config.inference_config import inference_config
from ml_engine.config.training_config import training_config
from ml_engine.pipeline.exceptions import PipelineExecutionError, StageDependencyError

# M1-12 Engine Imports
from ml_engine.data.download.yfinance_downloader import YFinanceDownloader
from ml_engine.data.storage.parquet_storage import ParquetStorage
from ml_engine.data.storage.numpy_storage import NumpyStorage
from ml_engine.data.validation.validators import ProductionDataValidator
from ml_engine.data.preprocess.cleaner import ProductionCleaner
from ml_engine.data.features.generator import FeatureGenerator
from ml_engine.data.datasets.builder import DatasetBuilder
from ml_engine.data.datasets.sequence_builder import SequenceBuilder
from ml_engine.training.keras_trainer import KerasTrainer
from ml_engine.evaluation.evaluator import ProductionEvaluator
from ml_engine.calibration.calibrator import ProductionCalibrator
from ml_engine.registry.manager import RegistryManager
from ml_engine.config.registry_config import registry_config
from ml_engine.inference.engine import ProductionInferenceEngine

logger = logging.getLogger(__name__)

class PipelineRunner:
    """
    Production Pipeline Runner.
    Orchestrates the entire E2E machine learning lifecycle sequentially.
    """

    def __init__(self, base_dir: str = "ml_data", ticker: str = "RELIANCE.NS"):
        self.base_dir = base_dir
        self.ticker = ticker
        
        # State tracking
        self.context: Dict[str, Any] = {}
        self.summary: Dict[str, Any] = {
            "pipeline_start": pd.Timestamp.utcnow().isoformat(),
            "stages": [],
            "status": "initialized"
        }
        
        # Storage
        self.tabular_storage = ParquetStorage(base_path=os.path.join(base_dir, "tabular"))
        self.tensor_storage = NumpyStorage(base_path=os.path.join(base_dir, "tensors"))
        
        # Registry
        registry_path = os.path.join(base_dir, "registry")
        self.registry = RegistryManager(registry_base_path=registry_path)
        
    def _log_stage(self, stage_name: str, duration: float, status: str, error: Optional[str] = None):
        """Appends stage telemetry to pipeline summary."""
        self.summary["stages"].append({
            "stage": stage_name,
            "duration_seconds": duration,
            "status": status,
            "error": error
        })
        
    def _save_summary(self):
        """Persists the pipeline execution summary."""
        self.summary["pipeline_end"] = pd.Timestamp.utcnow().isoformat()
        os.makedirs(self.base_dir, exist_ok=True)
        path = os.path.join(self.base_dir, "pipeline_summary.json")
        with open(path, "w") as f:
            json.dump(self.summary, f, indent=4)

    def run(self, stages: Optional[List[str]] = None, resume_from: Optional[str] = None) -> bool:
        """
        Executes the pipeline stages chronologically.
        """
        run_stages = stages or pipeline_config.DEFAULT_STAGES
        
        if resume_from:
            if resume_from not in run_stages:
                raise PipelineExecutionError(f"Stage {resume_from} not in pipeline sequence.")
            start_idx = run_stages.index(resume_from)
            run_stages = run_stages[start_idx:]
            
        logger.info(f"Starting Pipeline Execution for stages: {run_stages}")
        self.summary["status"] = "running"
        
        try:
            for stage in run_stages:
                logger.info(f"--- Executing Stage: {stage} ---")
                start_time = time.time()
                
                try:
                    self._execute_stage(stage)
                    duration = time.time() - start_time
                    self._log_stage(stage, duration, "success")
                except Exception as e:
                    duration = time.time() - start_time
                    self._log_stage(stage, duration, "failed", str(e))
                    raise PipelineExecutionError(f"Stage '{stage}' failed: {e}")
                    
            self.summary["status"] = "completed"
            self._save_summary()
            return True
            
        except Exception as global_e:
            self.summary["status"] = "failed"
            self._save_summary()
            logger.error(f"Pipeline failed: {global_e}")
            raise
            
    def _execute_stage(self, stage: str):
        """Routes string stage names to physical implementations."""
        if stage == pipeline_config.STAGE_DOWNLOAD:
            downloader = YFinanceDownloader(storage=self.tabular_storage)
            # Fetch last 5 years for production
            downloader.download(self.ticker, period="5y")
            self.context["raw_data_path"] = f"{self.ticker}/raw.parquet"
            
        elif stage == pipeline_config.STAGE_VALIDATE:
            raw_path = self.context.get("raw_data_path", f"{self.ticker}/raw.parquet")
            df = self.tabular_storage.load_dataframe(raw_path)
            validator = ProductionDataValidator()
            validator.validate_raw_dataset(df)
            
        elif stage == pipeline_config.STAGE_CLEAN:
            raw_path = self.context.get("raw_data_path", f"{self.ticker}/raw.parquet")
            df = self.tabular_storage.load_dataframe(raw_path)
            cleaner = ProductionCleaner()
            clean_df = cleaner.clean(df)
            clean_path = f"{self.ticker}/clean.parquet"
            self.tabular_storage.save_dataframe(clean_df, clean_path)
            self.context["clean_data_path"] = clean_path
            
        elif stage == pipeline_config.STAGE_DATASET:
            # Assumes feature engineering sits inside builder or is separate.
            # E2E logic normally has feature engineering then split. Let's do generator then split.
            clean_path = self.context.get("clean_data_path", f"{self.ticker}/clean.parquet")
            df = self.tabular_storage.load_dataframe(clean_path)
            
            # Feature Eng
            generator = FeatureGenerator()
            featured_df = generator.generate_all_features(df)
            
            # Dataset Builder
            builder = DatasetBuilder(storage=self.tabular_storage)
            metadata = builder.build(featured_df, self.ticker)
            if not metadata:
                raise PipelineExecutionError("Dataset Builder failed to produce metadata.")
            self.context["dataset_version"] = metadata["dataset_version"]
            
        elif stage == pipeline_config.STAGE_SEQUENCE:
            version = self.context.get("dataset_version", "v1")
            seq_builder = SequenceBuilder(
                tabular_storage=self.tabular_storage,
                tensor_storage=self.tensor_storage,
                dataset_version=version
            )
            seq_meta = seq_builder.build_sequences(self.ticker)
            if not seq_meta:
                raise PipelineExecutionError("Sequence Builder failed.")
                
        elif stage == pipeline_config.STAGE_TRAIN:
            version = self.context.get("dataset_version", "v1")
            trainer = KerasTrainer(
                ticker=self.ticker,
                dataset_version=version,
                tensor_storage=self.tensor_storage,
                model_dir=os.path.join(self.base_dir, "models")
            )
            history = trainer.train()
            self.context["model_path"] = os.path.join(self.base_dir, "models", self.ticker, version, "best_model.keras")
            
        elif stage == pipeline_config.STAGE_EVALUATE:
            version = self.context.get("dataset_version", "v1")
            evaluator = ProductionEvaluator(
                ticker=self.ticker,
                dataset_version=version,
                model_dir=os.path.join(self.base_dir, "models"),
                tensor_storage=self.tensor_storage
            )
            report_path = evaluator.evaluate()
            self.context["evaluation_report"] = report_path
            
        elif stage == pipeline_config.STAGE_CALIBRATE:
            version = self.context.get("dataset_version", "v1")
            calibrator = ProductionCalibrator(
                ticker=self.ticker,
                dataset_version=version,
                model_dir=os.path.join(self.base_dir, "models"),
                tensor_storage=self.tensor_storage
            )
            report_path = calibrator.calibrate()
            self.context["calibration_report"] = report_path
            
        elif stage == pipeline_config.STAGE_REGISTER:
            version = self.context.get("dataset_version", "v1")
            model_dir = os.path.join(self.base_dir, "models", self.ticker, version)
            
            source_artifacts = {
                "best_model.keras": os.path.join(model_dir, "best_model.keras"),
                "calibrator.pkl": os.path.join(model_dir, "calibrator.pkl"),
                "evaluation_report.json": os.path.join(model_dir, "evaluation_report.json"),
                "calibration_report.json": os.path.join(model_dir, "calibration_report.json")
            }
            
            self.registry.register_candidate(version, source_artifacts)
            
            # Simple automatic promotion for E2E (in reality this might require manual approval)
            # We'll promote straight to production for the pipeline success case.
            self.registry.promote_model(version, registry_config.STATE_CANDIDATE, registry_config.STATE_PRODUCTION)
            
        elif stage == pipeline_config.STAGE_INFERENCE_TEST:
            engine = ProductionInferenceEngine(registry_manager=self.registry)
            
            # Create a mock array matching features
            dummy_features = np.random.rand(
                training_config.SEQUENCE_LENGTH + 2, 
                inference_config.EXPECTED_FEATURES
            ).astype(np.float32)
            
            res = engine.predict(dummy_features)
            if not res:
                raise PipelineExecutionError("Inference validation returned empty results.")
                
        else:
            raise PipelineExecutionError(f"Unknown stage: {stage}")
