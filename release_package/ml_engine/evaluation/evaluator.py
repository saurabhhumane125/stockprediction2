import os
import json
import logging
import time
import hashlib
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, matthews_corrcoef,
    brier_score_loss, confusion_matrix, roc_curve, precision_recall_curve
)
from sklearn.calibration import calibration_curve

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

from ml_engine.config.evaluation_config import evaluation_config
from ml_engine.config.training_config import training_config
from ml_engine.data.storage.numpy_storage import NumpyStorage

logger = logging.getLogger(__name__)


class ProductionEvaluator:
    """
    Production Evaluation Engine.
    Consumes test tensors and best trained model, calculates rigorous metrics,
    and generates visual artifacts.
    """

    def __init__(self, tensor_storage: NumpyStorage, artifact_dir: str):
        self.tensor_storage = tensor_storage
        self.artifact_dir = artifact_dir
        self.plots_dir = os.path.join(self.artifact_dir, "plots")
        os.makedirs(self.plots_dir, exist_ok=True)
        
        # Set Plot Styles
        plt.style.use(evaluation_config.PLOT_STYLE)

    def evaluate(self, model_path: str, data_path: str) -> Dict[str, Any]:
        """
        Executes the evaluation loop for the given test data split.
        """
        logger.info(f"Starting Production Evaluation Engine.")
        start_time = time.time()
        
        # 1. Load Data & Model
        test_arrays = self.tensor_storage.load_arrays(f"{data_path}/test.npz")
        X_test, y_true = test_arrays["X"], test_arrays["y"]
        
        if len(X_test) == 0:
            raise ValueError("Insufficient test data for evaluation.")
            
        logger.info(f"Loading model from {model_path}")
        model = tf.keras.models.load_model(model_path)
        
        # 2. Predict Probabilities
        y_prob = model.predict(X_test, batch_size=training_config.BATCH_SIZE, verbose=0).flatten()
        y_pred = (y_prob >= evaluation_config.DECISION_THRESHOLD).astype(int)
        
        # 3. Compute Metrics
        metrics = self._calculate_metrics(y_true, y_prob, y_pred)
        
        # 4. Generate Plots
        self._generate_plots(y_true, y_prob, y_pred)
        
        # 5. Metadata and Reports
        duration = time.time() - start_time
        report_data = self._generate_reports(metrics, y_true, y_prob, y_pred, duration)
        
        logger.info(f"Evaluation completed in {duration:.2f}s. Artifacts saved to {self.artifact_dir}")
        return report_data
        
    def _calculate_metrics(self, y_true: np.ndarray, y_prob: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1_score": f1_score(y_true, y_pred, zero_division=0),
            "mcc": matthews_corrcoef(y_true, y_pred),
            "brier_score": brier_score_loss(y_true, y_prob)
        }
        
        # Handle cases with only one class present
        if len(np.unique(y_true)) > 1:
            metrics["roc_auc"] = roc_auc_score(y_true, y_prob)
            metrics["pr_auc"] = average_precision_score(y_true, y_prob)
        else:
            metrics["roc_auc"] = float("nan")
            metrics["pr_auc"] = float("nan")
            
        # Conversion to native floats
        return {k: float(v) for k, v in metrics.items()}
        
    def _generate_plots(self, y_true: np.ndarray, y_prob: np.ndarray, y_pred: np.ndarray):
        self._plot_confusion_matrix(y_true, y_pred)
        self._plot_prediction_distribution(y_prob, y_true)
        
        if len(np.unique(y_true)) > 1:
            self._plot_roc_curve(y_true, y_prob)
            self._plot_pr_curve(y_true, y_prob)
            self._plot_calibration_curve(y_true, y_prob)

    def _plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray):
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "confusion_matrix.png"), dpi=evaluation_config.PLOT_DPI)
        plt.close()

    def _plot_roc_curve(self, y_true: np.ndarray, y_prob: np.ndarray):
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, color='blue', lw=2, label='ROC Curve')
        plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
        plt.title('Receiver Operating Characteristic (ROC)')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend(loc='lower right')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "roc_curve.png"), dpi=evaluation_config.PLOT_DPI)
        plt.close()

    def _plot_pr_curve(self, y_true: np.ndarray, y_prob: np.ndarray):
        precision, recall, _ = precision_recall_curve(y_true, y_prob)
        plt.figure(figsize=(6, 5))
        plt.plot(recall, precision, color='purple', lw=2)
        plt.title('Precision-Recall Curve')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "pr_curve.png"), dpi=evaluation_config.PLOT_DPI)
        plt.close()

    def _plot_calibration_curve(self, y_true: np.ndarray, y_prob: np.ndarray):
        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=evaluation_config.NUM_CALIBRATION_BINS)
        plt.figure(figsize=(6, 5))
        plt.plot(prob_pred, prob_true, marker='o', linewidth=1, label='Model')
        plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfectly Calibrated')
        plt.title('Calibration Curve (Reliability Diagram)')
        plt.xlabel('Mean Predicted Probability')
        plt.ylabel('Fraction of Positives')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "calibration_curve.png"), dpi=evaluation_config.PLOT_DPI)
        plt.close()

    def _plot_prediction_distribution(self, y_prob: np.ndarray, y_true: np.ndarray):
        plt.figure(figsize=(8, 5))
        sns.histplot(x=y_prob, hue=y_true, bins=30, kde=True, palette='viridis', alpha=0.6)
        plt.title('Prediction Probability Distribution by Class')
        plt.xlabel('Predicted Probability')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "prediction_distribution.png"), dpi=evaluation_config.PLOT_DPI)
        plt.close()

    def _generate_reports(self, metrics: Dict[str, float], y_true: np.ndarray, y_prob: np.ndarray, y_pred: np.ndarray, duration: float) -> Dict[str, Any]:
        
        # Calculate Distribution
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0,0,0,0)
        
        distribution = {
            "Total Samples": int(len(y_true)),
            "True Positives (TP)": int(tp),
            "True Negatives (TN)": int(tn),
            "False Positives (FP)": int(fp),
            "False Negatives (FN)": int(fn)
        }
        
        config_hash = hashlib.md5(str(evaluation_config.to_dict()).encode()).hexdigest()
        training_hash = hashlib.md5(str(training_config.to_dict()).encode()).hexdigest()
        
        report_data = {
            "Model Version": "latest",
            "Evaluation Timestamp": pd.Timestamp.utcnow().isoformat(),
            "Evaluation Duration": duration,
            "Decision Threshold": evaluation_config.DECISION_THRESHOLD,
            "Configuration Hash": config_hash,
            "Training Hash": training_hash,
            "Metrics": metrics,
            "Prediction Distribution": distribution
        }
        
        # Save JSONs
        with open(os.path.join(self.artifact_dir, "evaluation.json"), "w") as f:
            json.dump(report_data, f, indent=4)
            
        with open(os.path.join(self.artifact_dir, "metrics.json"), "w") as f:
            json.dump(metrics, f, indent=4)
            
        # Write Markdown Report
        md_content = f"""# Production Evaluation Report

**Evaluation Timestamp:** {report_data["Evaluation Timestamp"]}  
**Model Version:** {report_data["Model Version"]}  
**Evaluation Duration:** {duration:.2f}s  
**Decision Threshold:** {evaluation_config.DECISION_THRESHOLD}  

## Hashes
- **Configuration Hash:** `{config_hash}`
- **Training Hash:** `{training_hash}`

## Metrics
"""
        for k, v in metrics.items():
            md_content += f"- **{k.replace('_', ' ').title()}:** {v:.4f}\n"

        md_content += f"\n## Prediction Distribution\n"
        for k, v in distribution.items():
            md_content += f"- **{k}:** {v}\n"
            
        md_content += "\n## Visual Artifacts\n"
        md_content += "![Confusion Matrix](./plots/confusion_matrix.png)\n"
        md_content += "![ROC Curve](./plots/roc_curve.png)\n"
        md_content += "![PR Curve](./plots/pr_curve.png)\n"
        md_content += "![Calibration Curve](./plots/calibration_curve.png)\n"
        md_content += "![Prediction Distribution](./plots/prediction_distribution.png)\n"
        
        with open(os.path.join(self.artifact_dir, "evaluation.md"), "w") as f:
            f.write(md_content)
            
        return report_data
