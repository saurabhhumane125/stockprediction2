import os
import json
import time
import logging
from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd
import joblib

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

from ml_engine.config.inference_config import inference_config
from ml_engine.config.training_config import training_config
from ml_engine.registry.manager import RegistryManager
from ml_engine.data.datasets.sequence_builder import SequenceBuilder
from ml_engine.inference.exceptions import (
    InferenceInputError,
    RegistryResolutionError,
    CalibrationError
)

logger = logging.getLogger(__name__)


class ProductionInferenceEngine:
    """
    Production Inference Engine.
    Exclusively resolves the active model from the registry, applies sequence building,
    executes predictions, and enforces mathematical probability calibration.
    """

    def __init__(self, registry_manager: RegistryManager):
        self.registry = registry_manager
        
        # Instantiate existing SequenceBuilder with dummy storages as it's only used for _create_windows
        class DummyStorage: pass
        self.sequence_builder = SequenceBuilder(
            tabular_storage=DummyStorage(),
            tensor_storage=DummyStorage()
        )
        
        self.model = None
        self.scaler = None
        self.calibrator = None
        self.active_version = None
        self.manifest = None
        
        # Preload dependencies
        self._bootstrap_inference()

    def _bootstrap_inference(self):
        """Resolves active models via Registry and preloads weights into memory."""
        try:
            active_info = self.registry.get_active_model()
            self.active_version = active_info["version"]
            
            logger.info(f"Bootstrapping Inference Engine with Model Version: {self.active_version}")
            
            # Load Model
            self.model = tf.keras.models.load_model(active_info["model_path"])
            
            # Load Scaler
            self.scaler = joblib.load(active_info["scaler_path"])
            
            # Load Calibrator
            self.calibrator = joblib.load(active_info["calibrator_path"])
            
            # Load Manifest metadata for reporting
            manifest_path = os.path.join(
                self.registry.base_path, 
                "production", 
                self.active_version, 
                "manifest.json"
            )
            with open(manifest_path, "r") as f:
                self.manifest = json.load(f)
                
        except Exception as e:
            raise RegistryResolutionError(f"Failed to bootstrap active production model. Details: {e}")

    def _validate_input(self, features: np.ndarray):
        """Validates incoming feature sets strictly against training expectations."""
        if not isinstance(features, np.ndarray):
            raise InferenceInputError("Input features must be a numpy array.")
            
        if len(features.shape) != 2:
            raise InferenceInputError(f"Expected 2D array (samples, features). Received shape: {features.shape}")
        expected_features = getattr(self.scaler, 'n_features_in_', None)
        if expected_features and features.shape[1] != expected_features:
            raise InferenceInputError(f"Expected {expected_features} features. Received: {features.shape[1]}")
            
        if len(features) > inference_config.MAX_BATCH_SIZE:
            raise InferenceInputError(f"Batch size {len(features)} exceeds maximum {inference_config.MAX_BATCH_SIZE}")

    def predict(self, features: Union[np.ndarray, pd.DataFrame]) -> List[Dict[str, Any]]:
        """
        Main Prediction Pipeline.
        Ingests features, builds temporal sequences, and yields calibrated probabilities.
        """
        start_time = time.time()
        
        # Convert DataFrames to Numpy securely
        if isinstance(features, pd.DataFrame):
            features = features.to_numpy()
            
        # 1. Validation
        self._validate_input(features)
        
        # Apply Scaling natively
        try:
            features = self.scaler.transform(features)
        except Exception as e:
            raise InferenceInputError(f"Feature scaling failed. Details: {e}")
        
        # 2. Sequence Generation (Must have at least enough data to build one sequence)
        if len(features) < training_config.SEQUENCE_LENGTH:
            raise InferenceInputError(
                f"Insufficient data to build a sequence. "
                f"Need {training_config.SEQUENCE_LENGTH}, got {len(features)}"
            )
            
        # Use SequenceBuilder._create_windows securely
        feature_cols = [f"f{i}" for i in range(features.shape[1])]
        df = pd.DataFrame(features, columns=feature_cols)
        df["target"] = 0  # Dummy target to satisfy builder requirements
        
        sequences, _ = self.sequence_builder._create_windows(df, feature_cols)
        
        if len(sequences) == 0:
            raise InferenceInputError("Failed to generate sequences from input data.")
            
        # 3. Model Prediction
        try:
            raw_logits = self.model.predict(sequences, verbose=0).flatten()
        except Exception as e:
            raise InferenceInputError(f"Neural Network prediction failed. Details: {e}")
            
        # 4. Calibration
        try:
            # Handle Sklearn single-feature reshape requirement natively
            if hasattr(self.calibrator, "predict_proba"):
                calibrated_probs = self.calibrator.predict_proba(raw_logits.reshape(-1, 1))[:, 1]
            else:
                calibrated_probs = self.calibrator.predict(raw_logits)
        except Exception as e:
            raise CalibrationError(f"Probability Calibration failed. Details: {e}")
            
        duration = time.time() - start_time
        
        # 5. Build Reports
        results = []
        for raw, calibrated in zip(raw_logits, calibrated_probs):
            # Ensure native float mapping
            raw = float(raw)
            calibrated = float(calibrated)
            
            # Predict Class
            pred_class = 1 if calibrated >= inference_config.DECISION_THRESHOLD else 0
            
            report = {
                "Predicted Class": pred_class,
                "Raw Probability": raw,
                "Calibrated Probability": calibrated,
                "Confidence": calibrated if pred_class == 1 else (1.0 - calibrated),
                "Model Version": self.active_version,
                "Inference Timestamp": pd.Timestamp.utcnow().isoformat(),
                "Execution Duration": duration,
                "Manifest Hash": self.manifest.get("artifacts", {}).get("best_model.keras", "unknown")
            }
            results.append(report)
            
        return results
