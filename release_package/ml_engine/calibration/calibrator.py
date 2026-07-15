"""
ml_engine/calibration/calibrator.py
─────────────────────────────────────────────────────────────────────────────
Calibration Manager for fitting and transforming probabilities, and 
CalibratedModelWrapper for seamless API integration.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
import pickle
from typing import Any, Tuple, Optional
import numpy as np
import torch

from ml_engine.calibration.methods import get_calibrator, BaseCalibrator
from ml_engine.config.evaluation_config import evaluation_config

logger = logging.getLogger(__name__)


class CalibrationManager:
    """
    Manages the fitting and application of a probability calibrator.
    """
    def __init__(self, method: Optional[str] = None) -> None:
        self.method_name = method or getattr(evaluation_config, "CALIBRATION_METHOD", "isotonic")
        self.calibrator: BaseCalibrator = get_calibrator(self.method_name)
        self._fitted = False

    def fit(self, y_prob: np.ndarray, y_true: np.ndarray) -> None:
        """
        Fits the calibrator using validation data.
        Expects 1D arrays for binary classification.
        """
        if self.method_name == "none":
            self._fitted = True
            return
            
        logger.info(f"[CalibrationManager] Fitting '{self.method_name}' calibrator on {len(y_prob)} samples.")
        
        # Ensure 1D
        if y_prob.ndim > 1:
            y_prob = y_prob[:, 1]
            
        self.calibrator.fit(y_prob, y_true)
        self._fitted = True

    def transform(self, y_prob: np.ndarray) -> np.ndarray:
        """
        Transforms raw probabilities into calibrated probabilities.
        """
        if not self._fitted:
            raise RuntimeError("CalibrationManager must be fitted before transform.")
            
        is_2d = y_prob.ndim > 1
        probs_1d = y_prob[:, 1] if is_2d else y_prob
        
        calibrated_1d = self.calibrator.transform(probs_1d)
        calibrated_1d = np.clip(calibrated_1d, 0.0, 1.0)
        
        if is_2d:
            # Reconstruct 2D array [P(y=0), P(y=1)]
            calibrated_2d = np.zeros_like(y_prob)
            calibrated_2d[:, 1] = calibrated_1d
            calibrated_2d[:, 0] = 1.0 - calibrated_1d
            return calibrated_2d
            
        return calibrated_1d

    def save(self, filepath: str) -> None:
        """Persist the fitted calibrator to disk."""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                "method": self.method_name,
                "calibrator": self.calibrator,
                "fitted": self._fitted
            }, f)
        logger.info(f"[CalibrationManager] Saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "CalibrationManager":
        """Load a fitted calibrator from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            
        manager = cls(method=data["method"])
        manager.calibrator = data["calibrator"]
        manager._fitted = data["fitted"]
        logger.info(f"[CalibrationManager] Loaded from {filepath}")
        return manager


class CalibratedModelWrapper:
    """
    Wraps a BaseTimeSeriesClassifier and a CalibrationManager.
    Intercepts `predict()` calls to apply calibration transparently.
    Maintains 100% backward compatibility with ProductionEvaluatorV2.
    """
    def __init__(self, model: Any, calibrator: CalibrationManager) -> None:
        self.model = model
        self.calibrator = calibrator

    def predict(self, X: torch.Tensor, device: str = "cpu") -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Overrides the predict method of the model.
        Returns (logits, calibrated_probs).
        """
        logits, raw_probs = self.model.predict(X, device=device)
        
        # Convert to numpy for calibration
        raw_probs_np = raw_probs.cpu().numpy()
        calibrated_probs_np = self.calibrator.transform(raw_probs_np)
        
        # Convert back to tensor
        calibrated_probs = torch.tensor(calibrated_probs_np, dtype=torch.float32)
        
        return logits, calibrated_probs
        
    def __getattr__(self, name: str) -> Any:
        """Delegate all other attributes/methods to the underlying model."""
        return getattr(self.model, name)
