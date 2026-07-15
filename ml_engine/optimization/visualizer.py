"""
ml_engine/optimization/visualizer.py
─────────────────────────────────────────────────────────────────────────────
Generates Optuna visualization plots using matplotlib backend headlessly.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
from typing import Dict
import optuna
from optuna.visualization.matplotlib import (
    plot_contour,
    plot_optimization_history,
    plot_param_importances,
    plot_parallel_coordinate,
    plot_slice
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ml_engine.config.evaluation_config import evaluation_config

logger = logging.getLogger(__name__)

_DPI = evaluation_config.PLOT_DPI


def _save(path: str) -> str:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    plt.savefig(path, dpi=_DPI, bbox_inches="tight")
    plt.close()
    logger.debug(f"[OptimizationVisualizer] Saved → {path}")
    return path


class OptimizationVisualizer:
    """
    Generates static PNG plots for an Optuna study.
    """
    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_plots(self, study: optuna.Study) -> Dict[str, str]:
        """
        Generate all supported Optuna visualizations and save as PNG.

        Args:
            study: Completed Optuna study.
            
        Returns:
            Dict mapping plot name to absolute file path.
        """
        paths = {}
        completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
        
        if not completed:
            logger.warning("[OptimizationVisualizer] No completed trials found. Skipping plots.")
            return paths

        try:
            plot_optimization_history(study)
            paths["optimization_history"] = _save(os.path.join(self.output_dir, "optimization_history.png"))
        except Exception as e:
            logger.warning(f"[OptimizationVisualizer] Failed to plot history: {e}")

        try:
            plot_parallel_coordinate(study)
            paths["parallel_coordinates"] = _save(os.path.join(self.output_dir, "parallel_coordinates.png"))
        except Exception as e:
            logger.warning(f"[OptimizationVisualizer] Failed to plot parallel coordinates: {e}")

        if len(completed) > 1:
            try:
                plot_param_importances(study)
                paths["parameter_importance"] = _save(os.path.join(self.output_dir, "parameter_importance.png"))
            except Exception as e:
                logger.warning(f"[OptimizationVisualizer] Failed to plot importances: {e}")

            try:
                plot_slice(study)
                paths["slice_plot"] = _save(os.path.join(self.output_dir, "slice_plot.png"))
            except Exception as e:
                logger.warning(f"[OptimizationVisualizer] Failed to plot slices: {e}")

            try:
                plot_contour(study)
                paths["contour_plot"] = _save(os.path.join(self.output_dir, "contour_plot.png"))
            except Exception as e:
                logger.warning(f"[OptimizationVisualizer] Failed to plot contour: {e}")
                
        return paths
