"""
ml_engine/optimization/optimizer.py
─────────────────────────────────────────────────────────────────────────────
Core Hyperparameter Optimization Engine for TradePredict.
Integrates with ModelFactory, TrainingOrchestrator, and ProductionEvaluatorV2.
─────────────────────────────────────────────────────────────────────────────
"""
import copy
import logging
import os
import time
from typing import Optional, Dict, Any, List
from unittest.mock import patch

import optuna

from ml_engine.config.training_config import training_config, TrainingConfig
from ml_engine.config.model_config import model_config, ModelConfig
from ml_engine.config.evaluation_config import evaluation_config
from ml_engine.data.storage.numpy_storage import NumpyStorage
from ml_engine.registry.manager import RegistryManager
from ml_engine.models.factory import ModelFactory
from ml_engine.training.training_pipeline import TrainingOrchestrator
from ml_engine.evaluation.evaluator_v2 import ProductionEvaluatorV2

from ml_engine.optimization.search_space import default_search_space, suggest_hyperparameters
from ml_engine.optimization.study_manager import StudyManager
from ml_engine.optimization.callbacks import LoggingCallback
from ml_engine.optimization.report_builder import OptimizationReportBuilder
from ml_engine.optimization.results import (
    OptimizationResult, TrialRecord, ParameterImportance
)
from ml_engine.optimization.visualizer import OptimizationVisualizer

logger = logging.getLogger(__name__)


class HyperparameterOptimizer:
    """
    Automates Hyperparameter Tuning using Optuna.
    Does not duplicate training logic. Uses unittest.mock to temporarily
    inject hyperparameters into the configuration singletons for each trial.
    """

    def __init__(
        self,
        study_name: str,
        tensor_storage: NumpyStorage,
        registry: RegistryManager,
        data_path: str,
        artifact_dir: str,
        n_trials: int = 50,
        pruner_type: str = "median",
        direction: str = "maximize",
    ) -> None:
        self.study_name = study_name
        self.tensor_storage = tensor_storage
        self.registry = registry
        self.data_path = data_path
        self.artifact_dir = artifact_dir
        self.n_trials = n_trials
        self.direction = direction

        self.storage_path = os.path.join(self.artifact_dir, f"{self.study_name}.db")
        self.study_manager = StudyManager(
            study_name=self.study_name,
            storage_path=self.storage_path,
            pruner_type=pruner_type
        )
        
        os.makedirs(self.artifact_dir, exist_ok=True)

    def run(self) -> OptimizationResult:
        """
        Execute the optimization study.
        """
        study = self.study_manager.get_study(direction=self.direction)
        
        start_time = time.time()
        
        study.optimize(
            self.objective,
            n_trials=self.n_trials,
            callbacks=[LoggingCallback()],
            catch=(Exception,)
        )
        
        total_time = time.time() - start_time
        logger.info(f"[Optimization] Study '{self.study_name}' complete in {total_time:.2f}s.")
        
        result = self._build_result(study, total_time)
        
        # Reports & Visualizations
        visualizer = OptimizationVisualizer(output_dir=os.path.join(self.artifact_dir, "plots"))
        plot_paths = visualizer.generate_plots(study)
        result.artifact_paths.update(plot_paths)
        
        report_builder = OptimizationReportBuilder(output_dir=self.artifact_dir)
        report_paths = report_builder.build(result)
        result.artifact_paths.update(report_paths)
        
        return result

    def objective(self, trial: optuna.Trial) -> float:
        """
        The objective function to minimize/maximize.
        """
        # 1. Sample Hyperparameters
        params = suggest_hyperparameters(trial, default_search_space)
        logger.debug(f"[Optimization] Trial {trial.number} starting with params: {params}")

        # Create localized config instances to avoid corrupting globals
        trial_train_cfg = TrainingConfig()
        trial_model_cfg = ModelConfig()

        # Apply mapped params
        for k, v in params.items():
            if hasattr(trial_train_cfg, k):
                setattr(trial_train_cfg, k, v)
            if hasattr(trial_model_cfg, k):
                setattr(trial_model_cfg, k, v)

        # 2. Inject configs via patch so TrainingOrchestrator and ModelFactory see them
        with patch("ml_engine.config.training_config.training_config", trial_train_cfg), \
             patch("ml_engine.config.model_config.model_config", trial_model_cfg):
                 
            # Note: We must also override the training config in the orchestrator directly if it has bound it already,
            # but since we inject before instantiation, it binds the patched version.

            # 3. Model Builder Proxy
            def model_builder(input_shape):
                # The factory relies on model_config.
                model = ModelFactory.create(input_shape=input_shape)
                return model

            trial_artifact_dir = os.path.join(self.artifact_dir, f"trial_{trial.number}")
            
            # 4. Orchestrate Training
            orchestrator = TrainingOrchestrator(
                model_builder=model_builder,
                tensor_storage=self.tensor_storage,
                registry=self.registry,
                data_path=self.data_path,
                artifact_dir=trial_artifact_dir,
                version=f"{self.study_name}_T{trial.number}",
            )
            # Make absolutely sure it uses our patched config
            orchestrator.cfg = trial_train_cfg
            
            try:
                # We do not resume inside the optimizer.
                train_result = orchestrator.run(resume=False)
            except Exception as e:
                logger.error(f"[Optimization] Trial {trial.number} failed during training: {e}", exc_info=True)
                raise optuna.TrialPruned() from e

            # 5. Evaluate using the new Evaluator
            try:
                # Load the saved best model weights
                import torch
                model = model_builder((trial_train_cfg.SEQUENCE_LENGTH, 10)) # shape dummy, factory handles it correctly? Factory ignores 10 if not input size but we need actual test shape
                
                # Fetch test sets via the storage to get correct shape
                arrays = self.tensor_storage.load_arrays(f"{self.data_path}/test.npz")
                X_test, y_test = arrays["X"], arrays["y"]
                
                model = model_builder((X_test.shape[1], X_test.shape[2]))
                model.load_state_dict(torch.load(os.path.join(trial_artifact_dir, "model.pt"), map_location="cpu"))
                
                evaluator = ProductionEvaluatorV2(
                    artifact_dir=os.path.join(trial_artifact_dir, "eval"),
                    run_walk_forward=False # Skip walk forward in HPO to save time
                )
                
                eval_result = evaluator.evaluate(
                    model=model,
                    X_test=X_test,
                    y_test=y_test,
                    model_name=trial_model_cfg.MODEL_TYPE,
                    model_version=f"trial_{trial.number}"
                )
                
                primary_metric_key = evaluation_config.COMPARATOR_PRIMARY_METRIC
                val = eval_result.metrics.to_dict().get(primary_metric_key)
                
                if val is None or (isinstance(val, float) and val != val):  # check for NaN
                    raise ValueError(f"Primary metric {primary_metric_key} was NaN.")
                    
                return float(val)

            except Exception as e:
                logger.error(f"[Optimization] Trial {trial.number} failed during evaluation: {e}", exc_info=True)
                raise optuna.TrialPruned() from e

    def _build_result(self, study: optuna.Study, duration: float) -> OptimizationResult:
        
        # Parameter Importances
        importances = []
        try:
            if len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]) > 1:
                imp = optuna.importance.get_param_importances(study)
                for k, v in imp.items():
                    importances.append(ParameterImportance(name=k, importance=v))
        except Exception as e:
            logger.warning(f"Could not compute importances: {e}")

        # Best Trial
        try:
            best_trial = study.best_trial
            best_value = best_trial.value
            best_params = best_trial.params
            best_number = best_trial.number
        except ValueError:
            best_value = None
            best_params = {}
            best_number = None

        # Build TrialRecords
        def _make_record(t: optuna.trial.FrozenTrial) -> TrialRecord:
            dt_start = t.datetime_start.isoformat() if t.datetime_start else ""
            dt_complete = t.datetime_complete.isoformat() if t.datetime_complete else None
            dur = (t.datetime_complete - t.datetime_start).total_seconds() if t.datetime_complete and t.datetime_start else 0.0
            return TrialRecord(
                number=t.number,
                state=t.state.name,
                value=t.value,
                datetime_start=dt_start,
                datetime_complete=dt_complete,
                params=t.params,
                duration_seconds=dur
            )

        top_trials = []
        completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
        completed.sort(key=lambda t: t.value if t.value is not None else float('-inf'), reverse=(self.direction=="maximize"))
        for t in completed[:10]:
            top_trials.append(_make_record(t))

        failed_trials = []
        for t in study.trials:
            if t.state in (optuna.trial.TrialState.FAIL, optuna.trial.TrialState.PRUNED):
                failed_trials.append(_make_record(t))

        return OptimizationResult(
            study_name=self.study_name,
            n_trials=len(study.trials),
            best_value=best_value,
            best_params=best_params,
            best_trial_number=best_number,
            optimization_time_seconds=duration,
            top_n_trials=top_trials,
            failed_trials=failed_trials,
            parameter_importance=importances
        )
