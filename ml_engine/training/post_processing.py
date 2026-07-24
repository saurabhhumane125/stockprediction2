"""
ml_engine/training/post_processing.py
─────────────────────────────────────────────────────────────────────────────
TaskType-aware PostProcessingDispatcher for the post-training pipeline.
Dispatches evaluation, calibration, plot generation, and metric reporting 
strictly according to TaskType.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
from typing import Dict, Any, Optional

import numpy as np

from ml_engine.core.types import TaskType
from ml_engine.training.metrics_registry import MetricsRegistry
from ml_engine.calibration.calibrator import CalibrationManager
from ml_engine.training.evaluation_plots import (
    find_optimal_threshold,
    generate_evaluation_plots,
    generate_regression_evaluation_plots,
)

logger = logging.getLogger(__name__)


class PostProcessingDispatcher:
    """
    Production Dispatcher for TaskType-aware post-training actions.
    Decides which evaluation, calibration, plotting, and thresholding steps execute.
    """

    @staticmethod
    def dispatch(
        task_type: TaskType,
        val_true: np.ndarray,
        val_preds: np.ndarray,
        val_probs: np.ndarray,
        val_logits: np.ndarray,
        test_true: np.ndarray,
        test_preds: np.ndarray,
        test_probs: np.ndarray,
        test_logits: np.ndarray,
        artifact_dir: str,
    ) -> Dict[str, Any]:
        """
        Executes task-specific post-processing workflows.
        Returns a dictionary containing evaluation metrics, plot paths, and calibrator path.
        """
        logger.info(f"[PostProcessingDispatcher] Executing workflow for TaskType: {task_type.value}")

        if task_type == TaskType.BINARY_CLASSIFICATION:
            return PostProcessingDispatcher._process_binary(
                val_true, val_preds, val_probs, val_logits,
                test_true, test_preds, test_probs, test_logits,
                artifact_dir
            )
        elif task_type == TaskType.REGRESSION:
            return PostProcessingDispatcher._process_regression(
                val_true, val_preds, val_probs, val_logits,
                test_true, test_preds, test_probs, test_logits,
                artifact_dir
            )
        elif task_type == TaskType.MULTI_OUTPUT_REGRESSION:
            return PostProcessingDispatcher._process_multi_output_regression(
                val_true, val_preds, val_probs, val_logits,
                test_true, test_preds, test_probs, test_logits,
                artifact_dir
            )
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
            return PostProcessingDispatcher._process_multiclass(
                val_true, val_preds, val_probs, val_logits,
                test_true, test_preds, test_probs, test_logits,
                artifact_dir
            )
        else:
            raise ValueError(f"Unsupported TaskType for PostProcessingDispatcher: {task_type}")

    @staticmethod
    def _process_binary(
        val_true, val_preds, val_probs, val_logits,
        test_true, test_preds, test_probs, test_logits,
        artifact_dir
    ) -> Dict[str, Any]:
        metrics = {}
        
        # 1. Classification Metrics
        test_prob_auc = test_probs[:, 1] if (test_probs.ndim > 1 and test_probs.shape[1] == 2) else test_probs
        clf_metrics = MetricsRegistry.evaluate(TaskType.BINARY_CLASSIFICATION, test_true, test_preds, test_prob_auc)
        metrics.update(clf_metrics)

        # 2. Probability Calibration
        val_prob_calib = val_probs[:, 1] if (val_probs.ndim > 1 and val_probs.shape[1] == 2) else val_probs
        calibrator = CalibrationManager()
        calibrator.fit(val_prob_calib, val_true)
        calibrator_path = os.path.join(artifact_dir, "calibrator.pkl")
        calibrator.save(calibrator_path)

        # 3. Diagnostic Plots & Optimal Threshold
        plot_paths = {}
        try:
            np.save(os.path.join(artifact_dir, "val_logits.npy"), val_logits)
            np.save(os.path.join(artifact_dir, "val_probs.npy"), val_probs)
            np.save(os.path.join(artifact_dir, "test_logits.npy"), test_logits)
            np.save(os.path.join(artifact_dir, "test_probs.npy"), test_probs)

            val_prob_1d = val_probs[:, 1] if (val_probs.ndim > 1 and val_probs.shape[1] == 2) else val_probs
            test_prob_1d = test_probs[:, 1] if (test_probs.ndim > 1 and test_probs.shape[1] == 2) else test_probs

            optimal_thresh = find_optimal_threshold(val_true, val_prob_1d)
            metrics["optimal_val_f1_threshold"] = optimal_thresh

            val_plots = generate_evaluation_plots(val_true, val_prob_1d, val_logits, artifact_dir, prefix="val")
            test_plots = generate_evaluation_plots(test_true, test_prob_1d, test_logits, artifact_dir, prefix="test")
            plot_paths = {**val_plots, **test_plots}
        except Exception as e:
            logger.warning(f"[PostProcessingDispatcher] Binary plot generation failed: {e}")

        metrics["plot_paths"] = plot_paths
        return {
            "metrics": metrics,
            "calibrator_path": calibrator_path
        }

    @staticmethod
    def _process_regression(
        val_true, val_preds, val_probs, val_logits,
        test_true, test_preds, test_probs, test_logits,
        artifact_dir
    ) -> Dict[str, Any]:
        metrics = {}

        # 1. Regression Metrics (RMSE, MAE, R2, IC)
        reg_metrics = MetricsRegistry.evaluate(TaskType.REGRESSION, test_true, test_preds)
        metrics.update(reg_metrics)

        # 2. Residual Statistics on Validation Set
        residuals = val_true.squeeze() - val_preds.squeeze()
        metrics["mean_residual"] = float(np.mean(residuals))
        metrics["std_residual"] = float(np.std(residuals))
        metrics["max_error"] = float(np.max(np.abs(residuals)))

        # 3. Regression Diagnostic Plots (Pred vs Actual, Residual Histogram)
        plot_paths = {}
        try:
            np.save(os.path.join(artifact_dir, "val_preds.npy"), val_preds)
            np.save(os.path.join(artifact_dir, "test_preds.npy"), test_preds)

            val_plots = generate_regression_evaluation_plots(val_true, val_preds, artifact_dir, prefix="val")
            test_plots = generate_regression_evaluation_plots(test_true, test_preds, artifact_dir, prefix="test")
            plot_paths = {**val_plots, **test_plots}
        except Exception as e:
            logger.warning(f"[PostProcessingDispatcher] Regression plot generation failed: {e}")

        metrics["plot_paths"] = plot_paths

        # Save an uncalibrated identity calibrator sentinel for seamless registry artifact handling
        calibrator = CalibrationManager("none")
        calibrator.fit(val_preds, val_true)
        calibrator_path = os.path.join(artifact_dir, "calibrator.pkl")
        calibrator.save(calibrator_path)

        return {
            "metrics": metrics,
            "calibrator_path": calibrator_path
        }

    @staticmethod
    def _process_multi_output_regression(
        val_true, val_preds, val_probs, val_logits,
        test_true, test_preds, test_probs, test_logits,
        artifact_dir
    ) -> Dict[str, Any]:
        metrics = {}
        reg_metrics = MetricsRegistry.evaluate(TaskType.MULTI_OUTPUT_REGRESSION, test_true, test_preds)
        metrics.update(reg_metrics)

        residuals = val_true.squeeze() - val_preds.squeeze()
        metrics["mean_residual"] = float(np.mean(residuals))
        metrics["std_residual"] = float(np.std(residuals))

        calibrator = CalibrationManager("none")
        calibrator.fit(val_preds, val_true)
        calibrator_path = os.path.join(artifact_dir, "calibrator.pkl")
        calibrator.save(calibrator_path)

        return {
            "metrics": metrics,
            "calibrator_path": calibrator_path
        }

    @staticmethod
    def _process_multiclass(
        val_true, val_preds, val_probs, val_logits,
        test_true, test_preds, test_probs, test_logits,
        artifact_dir
    ) -> Dict[str, Any]:
        metrics = {}
        mc_metrics = MetricsRegistry.evaluate(TaskType.MULTICLASS_CLASSIFICATION, test_true, test_preds, test_probs)
        metrics.update(mc_metrics)

        calibrator = CalibrationManager("none")
        calibrator.fit(val_probs, val_true)
        calibrator_path = os.path.join(artifact_dir, "calibrator.pkl")
        calibrator.save(calibrator_path)

        return {
            "metrics": metrics,
            "calibrator_path": calibrator_path
        }
