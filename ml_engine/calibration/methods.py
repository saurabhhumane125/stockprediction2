"""
ml_engine/calibration/methods.py
─────────────────────────────────────────────────────────────────────────────
Implementations of various calibration methods.
─────────────────────────────────────────────────────────────────────────────
"""
from typing import Protocol, Any
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression


class BaseCalibrator(Protocol):
    """Protocol defining the required interface for a calibrator."""
    def fit(self, y_prob: np.ndarray, y_true: np.ndarray) -> None:
        ...
        
    def transform(self, y_prob: np.ndarray) -> np.ndarray:
        ...


class PlattScaler:
    """
    Calibrates probabilities using Logistic Regression (Platt Scaling).
    Expects 1D probability arrays for the positive class.
    """
    def __init__(self) -> None:
        # C=1e10 to effectively disable regularization for raw scaling
        self.model = LogisticRegression(C=1e10, solver='lbfgs')
        self._fitted = False

    def fit(self, y_prob: np.ndarray, y_true: np.ndarray) -> None:
        """Fit the Logistic Regression model."""
        # Log-odds transformation to map probabilities back to logits for Platt scaling
        # Avoid exactly 0 or 1 to prevent log(0)
        eps = 1e-15
        y_prob = np.clip(y_prob, eps, 1 - eps)
        logits = np.log(y_prob / (1 - y_prob)).reshape(-1, 1)
        
        self.model.fit(logits, y_true)
        self._fitted = True

    def transform(self, y_prob: np.ndarray) -> np.ndarray:
        """Apply the fitted scaling."""
        if not self._fitted:
            raise RuntimeError("PlattScaler is not fitted yet.")
        eps = 1e-15
        y_prob = np.clip(y_prob, eps, 1 - eps)
        logits = np.log(y_prob / (1 - y_prob)).reshape(-1, 1)
        return self.model.predict_proba(logits)[:, 1]


class IsotonicCalibrator:
    """
    Calibrates probabilities using Isotonic Regression.
    """
    def __init__(self) -> None:
        self.model = IsotonicRegression(out_of_bounds='clip', y_min=0.0, y_max=1.0)
        self._fitted = False

    def fit(self, y_prob: np.ndarray, y_true: np.ndarray) -> None:
        """Fit the Isotonic Regression model."""
        self.model.fit(y_prob, y_true)
        self._fitted = True

    def transform(self, y_prob: np.ndarray) -> np.ndarray:
        """Apply the fitted calibration."""
        if not self._fitted:
            raise RuntimeError("IsotonicCalibrator is not fitted yet.")
        return self.model.predict(y_prob)


class DummyCalibrator:
    """
    Pass-through calibrator when calibration is disabled or 'none'.
    """
    def fit(self, y_prob: np.ndarray, y_true: np.ndarray) -> None:
        pass

    def transform(self, y_prob: np.ndarray) -> np.ndarray:
        return y_prob


def get_calibrator(method: str) -> BaseCalibrator:
    """Factory to get the requested calibrator method."""
    method = method.lower().strip()
    if method == "isotonic":
        return IsotonicCalibrator()
    elif method == "platt":
        return PlattScaler()
    elif method == "none":
        return DummyCalibrator()
    else:
        raise ValueError(f"Unknown calibration method: {method}")
