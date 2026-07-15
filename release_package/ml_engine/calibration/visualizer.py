"""
ml_engine/calibration/visualizer.py
─────────────────────────────────────────────────────────────────────────────
Generates Reliability Diagrams and Histograms (Before vs. After calibration).
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
from typing import Dict
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve

from ml_engine.config.evaluation_config import evaluation_config

logger = logging.getLogger(__name__)

_DPI = evaluation_config.PLOT_DPI
_BINS = evaluation_config.NUM_CALIBRATION_BINS


def _save(path: str) -> str:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    plt.savefig(path, dpi=_DPI, bbox_inches="tight")
    plt.close()
    logger.debug(f"[CalibrationVisualizer] Saved → {path}")
    return path


class CalibrationVisualizer:
    """
    Generates static PNG plots for probability calibration.
    """
    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_plots(self, y_true: np.ndarray, y_prob_before: np.ndarray, y_prob_after: np.ndarray) -> Dict[str, str]:
        """
        Generates comparison plots.
        """
        paths = {}
        
        try:
            paths["reliability_diagram"] = self._plot_reliability(y_true, y_prob_before, y_prob_after)
        except Exception as e:
            logger.warning(f"[CalibrationVisualizer] Failed to plot reliability diagram: {e}")

        try:
            paths["histogram"] = self._plot_histogram(y_prob_before, y_prob_after)
        except Exception as e:
            logger.warning(f"[CalibrationVisualizer] Failed to plot histogram: {e}")

        return paths

    def _plot_reliability(self, y_true: np.ndarray, y_prob_before: np.ndarray, y_prob_after: np.ndarray) -> str:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Perfectly calibrated line
        ax.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
        
        # Before
        prob_true_b, prob_pred_b = calibration_curve(y_true, y_prob_before, n_bins=_BINS)
        ax.plot(prob_pred_b, prob_true_b, "s-", label="Before Calibration", alpha=0.7)
        
        # After
        prob_true_a, prob_pred_a = calibration_curve(y_true, y_prob_after, n_bins=_BINS)
        ax.plot(prob_pred_a, prob_true_a, "o-", label="After Calibration", alpha=0.9)
        
        ax.set_ylabel("Fraction of positives")
        ax.set_xlabel("Mean predicted probability")
        ax.set_ylim([-0.05, 1.05])
        ax.legend(loc="lower right")
        ax.set_title("Reliability Diagram (Calibration Curve)")
        
        return _save(os.path.join(self.output_dir, "reliability_diagram.png"))

    def _plot_histogram(self, y_prob_before: np.ndarray, y_prob_after: np.ndarray) -> str:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.hist(y_prob_before, range=(0, 1), bins=_BINS, histtype="step", lw=2, label="Before", density=True, alpha=0.7)
        ax.hist(y_prob_after, range=(0, 1), bins=_BINS, histtype="step", lw=2, label="After", density=True, alpha=0.9)
        
        ax.set_xlabel("Mean predicted probability")
        ax.set_ylabel("Density")
        ax.legend(loc="upper center", ncol=2)
        ax.set_title("Probability Distribution")
        
        return _save(os.path.join(self.output_dir, "probability_histogram.png"))
