import os
import json
import logging
import hashlib
import time
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

from ml_engine.config.calibration_config import calibration_config
from ml_engine.config.training_config import training_config
from ml_engine.data.storage.numpy_storage import NumpyStorage

logger = logging.getLogger(__name__)


def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Calculates the Expected Calibration Error (ECE)"""
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)
    
    ece = 0.0
    bins = np.linspace(0., 1. + 1e-8, n_bins + 1)
    binned = np.digitize(y_prob, bins) - 1
    
    for b in range(n_bins):
        bin_idx = binned == b
        if np.any(bin_idx):
            bin_size = np.sum(bin_idx)
            bin_acc = np.mean(y_true[bin_idx])
            bin_conf = np.mean(y_prob[bin_idx])
            ece += (bin_size / len(y_prob)) * np.abs(bin_acc - bin_conf)
            
    return float(ece)


def maximum_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Calculates the Maximum Calibration Error (MCE)"""
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)
    if len(prob_true) == 0:
        return 0.0
    return float(np.max(np.abs(prob_true - prob_pred)))


class ProductionCalibrator:
    """
    Production Calibration Engine.
    Fits Platt Scaling and Isotonic Regression, selects optimal calibrator,
    and generates reliability artifacts.
    """

    def __init__(self, tensor_storage: NumpyStorage, artifact_dir: str):
        self.tensor_storage = tensor_storage
        self.artifact_dir = artifact_dir
        self.plots_dir = os.path.join(self.artifact_dir, "plots")
        os.makedirs(self.plots_dir, exist_ok=True)
        plt.style.use(calibration_config.PLOT_STYLE)

    def calibrate(self, model_path: str, data_path: str) -> Dict[str, Any]:
        """
        Executes calibration pipeline.
        """
        logger.info(f"Starting Production Calibration Engine.")
        start_time = time.time()
        
        # 1. Load Data & Base Model
        val_arrays = self.tensor_storage.load_arrays(f"{data_path}/val.npz")
        test_arrays = self.tensor_storage.load_arrays(f"{data_path}/test.npz")
        
        X_val, y_val = val_arrays["X"], val_arrays["y"]
        X_test, y_test = test_arrays["X"], test_arrays["y"]
        
        if len(X_val) == 0 or len(X_test) == 0:
            raise ValueError("Insufficient validation or testing data for calibration.")
            
        model = tf.keras.models.load_model(model_path)
        
        # 2. Extract Raw Logits / Probabilities
        raw_val_prob = model.predict(X_val, batch_size=training_config.BATCH_SIZE, verbose=0).flatten()
        raw_test_prob = model.predict(X_test, batch_size=training_config.BATCH_SIZE, verbose=0).flatten()
        
        # 3. Fit Calibrators
        platt = LogisticRegression()
        # reshape for sklearn
        platt.fit(raw_val_prob.reshape(-1, 1), y_val)
        
        isotonic = IsotonicRegression(out_of_bounds=calibration_config.ISOTONIC_OUT_OF_BOUNDS)
        isotonic.fit(raw_val_prob, y_val)
        
        # 4. Predict on Test Set
        prob_dict = {
            "Raw": raw_test_prob,
            "Platt Scaling": platt.predict_proba(raw_test_prob.reshape(-1, 1))[:, 1],
            "Isotonic Regression": isotonic.predict(raw_test_prob)
        }
        
        # 5. Calculate Metrics
        metrics = {}
        for name, probs in prob_dict.items():
            metrics[name] = {
                "brier_score": brier_score_loss(y_test, probs),
                "ece": expected_calibration_error(y_test, probs, n_bins=calibration_config.NUM_BINS),
                "mce": maximum_calibration_error(y_test, probs, n_bins=calibration_config.NUM_BINS)
            }
            
        # 6. Automatic Selection (Minimize Brier + ECE)
        # Using a simple heuristic: standard scaler sum or rank. Here we just pick min brier.
        best_method = min(metrics.keys(), key=lambda k: metrics[k]["brier_score"])
        best_calibrator = None
        if best_method == "Platt Scaling":
            best_calibrator = platt
        elif best_method == "Isotonic Regression":
            best_calibrator = isotonic
            
        # 7. Artifact Generation
        if best_calibrator is not None:
            joblib.dump(best_calibrator, os.path.join(self.artifact_dir, "calibrator.pkl"))
            
        self._generate_plots(y_test, prob_dict, best_method)
        
        duration = time.time() - start_time
        report = self._generate_reports(metrics, best_method, prob_dict[best_method], duration)
        
        logger.info(f"Calibration completed in {duration:.2f}s. Winning method: {best_method}")
        return report

    def _generate_plots(self, y_true: np.ndarray, prob_dict: Dict[str, np.ndarray], best_method: str):
        
        # Reliability Before
        prob_true_raw, prob_pred_raw = calibration_curve(y_true, prob_dict["Raw"], n_bins=calibration_config.NUM_BINS)
        
        plt.figure(figsize=(6, 5))
        plt.plot(prob_pred_raw, prob_true_raw, marker='o', linewidth=1, label='Raw Model')
        plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfect Calibration')
        plt.title('Reliability Diagram (Before Calibration)')
        plt.xlabel('Mean Predicted Probability')
        plt.ylabel('Fraction of Positives')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "reliability_before.png"), dpi=calibration_config.PLOT_DPI)
        plt.close()
        
        # Reliability After
        prob_true_best, prob_pred_best = calibration_curve(y_true, prob_dict[best_method], n_bins=calibration_config.NUM_BINS)
        
        plt.figure(figsize=(6, 5))
        plt.plot(prob_pred_best, prob_true_best, marker='s', linewidth=1, label=best_method, color='green')
        plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfect Calibration')
        plt.title('Reliability Diagram (After Calibration)')
        plt.xlabel('Mean Predicted Probability')
        plt.ylabel('Fraction of Positives')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "reliability_after.png"), dpi=calibration_config.PLOT_DPI)
        plt.close()
        
        # Confidence Distribution
        plt.figure(figsize=(8, 5))
        sns.histplot(x=prob_dict[best_method], hue=y_true, bins=30, kde=True, palette='viridis', alpha=0.6)
        plt.title(f'Confidence Distribution ({best_method})')
        plt.xlabel('Calibrated Probability')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "confidence_distribution.png"), dpi=calibration_config.PLOT_DPI)
        plt.close()

    def _generate_reports(self, metrics: Dict[str, Any], best_method: str, best_probs: np.ndarray, duration: float) -> Dict[str, Any]:
        
        config_hash = hashlib.md5(str(calibration_config.to_dict()).encode()).hexdigest()
        
        report_data = {
            "Calibration Timestamp": pd.Timestamp.utcnow().isoformat(),
            "Calibration Duration": duration,
            "Best Method": best_method,
            "Selection Justification": f"{best_method} achieved the lowest Brier Score.",
            "Configuration Hash": config_hash,
            "Metrics": metrics
        }
        
        with open(os.path.join(self.artifact_dir, "calibration_report.json"), "w") as f:
            json.dump(report_data, f, indent=4)
            
        with open(os.path.join(self.artifact_dir, "calibration_metrics.json"), "w") as f:
            json.dump(metrics, f, indent=4)
            
        md_content = f"""# Production Calibration Report

**Calibration Timestamp:** {report_data["Calibration Timestamp"]}  
**Calibration Duration:** {duration:.2f}s  
**Winning Method:** {best_method}  
**Selection Justification:** {report_data["Selection Justification"]}  
**Configuration Hash:** `{config_hash}`  

## Metrics Comparison
"""
        for method, m_dict in metrics.items():
            md_content += f"\n### {method}\n"
            for k, v in m_dict.items():
                md_content += f"- **{k.upper()}:** {v:.4f}\n"

        md_content += "\n## Visual Artifacts\n"
        md_content += "![Reliability Before](./plots/reliability_before.png)\n"
        md_content += "![Reliability After](./plots/reliability_after.png)\n"
        md_content += "![Confidence Distribution](./plots/confidence_distribution.png)\n"
        
        with open(os.path.join(self.artifact_dir, "calibration_report.md"), "w") as f:
            f.write(md_content)
            
        return report_data
