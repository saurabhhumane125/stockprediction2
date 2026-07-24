import os
import time
import json
import logging
from typing import Dict, Any, List, Union

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from ml_engine.config.training_config import training_config
from ml_engine.core.types import TaskType
from ml_engine.data.tensors.targets.manager import TargetManager
from ml_engine.config.inference_config import inference_config
from ml_engine.registry.manager import RegistryManager
from ml_engine.inference.exceptions import (
    InferenceInputError,
    RegistryResolutionError,
    CalibrationError
)

logger = logging.getLogger(__name__)


class ProductionInferenceEngine:
    """
    Production Inference Engine.
    Exclusively resolves the active model from the registry, applies sequence building natively,
    executes predictions using Framework Dispatch, and enforces mathematical probability calibration.
    """

    def __init__(self, registry_manager: RegistryManager):
        self.registry = registry_manager
        
        self.model = None
        self.scaler = None
        self.calibrator = None
        self.active_version = None
        self.manifest = None
        self.framework = None
        
        # Preload dependencies
        self._bootstrap_inference()

    def _bootstrap_inference(self):
        """Resolves active models via Registry and preloads weights into memory."""
        try:
            active_info = self.registry.get_active_model()
            self.active_version = active_info["version"]
            self.manifest = active_info.get("manifest_data", {})
            
            logger.info(f"Bootstrapping Inference Engine with Model Version: {self.active_version}")
            
            self.framework = self.manifest.get("framework", "tensorflow")
            
            # Framework Dispatch
            if self.framework == "pytorch":
                import torch
                from ml_engine.models.model_factory import ModelFactory
                
                model_type = self.manifest.get("model_type", "GRU")
                input_size = self.manifest.get("input_size")
                if not input_size:
                    input_size = len(self.manifest.get("feature_names", []))
                    
                if not input_size:
                    raise ValueError("Cannot determine input_size for PyTorch model from manifest.")
                    
                self.model = ModelFactory.create(input_size=input_size, model_type=model_type)
                self.model.load_state_dict(torch.load(active_info["model_path"], map_location=torch.device('cpu')))
                self.model.eval()
            else:
                self.model = tf.keras.models.load_model(active_info["model_path"])
            
            # Load Scaler
            self.scaler = joblib.load(active_info["scaler_path"])
            
            # Load Calibrator
            if os.path.exists(active_info["calibrator_path"]):
                try:
                    self.calibrator = joblib.load(active_info["calibrator_path"])
                except Exception:
                    self.calibrator = None
            else:
                self.calibrator = None
                
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

    def _create_windows(self, features: np.ndarray) -> np.ndarray:
        """
        Applies a sliding window over the scaled features natively.
        Does not require a dummy target column.
        """
        seq_len = training_config.SEQUENCE_LENGTH
        if len(features) <= seq_len:
            return np.array([])
            
        X = []
        for i in range(len(features) - seq_len + 1):
            window = features[i:i + seq_len]
            if np.isnan(window).any():
                continue
            X.append(window)
            
        return np.array(X) if X else np.array([])

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
            scaled_features = self.scaler.transform(features)
        except Exception as e:
            raise InferenceInputError(f"Feature scaling failed. Details: {e}")
        
        # 2. Sequence Generation (Must have at least enough data to build one sequence)
        if len(features) < training_config.SEQUENCE_LENGTH:
            raise InferenceInputError(
                f"Insufficient data to build a sequence. "
                f"Need {training_config.SEQUENCE_LENGTH}, got {len(features)}"
            )
            
        # Generate Windows Natively
        sequences = self._create_windows(scaled_features)
        raw_sequences = self._create_windows(features)
        
        if len(sequences) == 0:
            raise InferenceInputError("Failed to generate sequences from input data.")
            
        # 3. Model Prediction
        try:
            if self.framework == "pytorch":
                import torch
                with torch.no_grad():
                    X_tensor = torch.tensor(sequences, dtype=torch.float32)
                    logits = self.model(X_tensor).cpu().numpy().flatten()
                raw_logits = logits
            else:
                raw_logits = self.model.predict(sequences, verbose=0).flatten()
        except Exception as e:
            raise InferenceInputError(f"Neural Network prediction failed. Details: {e}")
            
        # Task Type Resolution
        task_type_str = self.manifest.get("task_type", "BINARY_CLASSIFICATION")
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            task_type = TaskType.BINARY_CLASSIFICATION

        # 4. Calibration (TaskType-Aware)
        try:
            if self.calibrator and task_type == TaskType.BINARY_CLASSIFICATION:
                if isinstance(self.calibrator, CalibrationManager):
                    calibrated_probs = self.calibrator.transform(raw_logits)
                elif hasattr(self.calibrator, "predict_proba"):
                    calibrated_probs = self.calibrator.predict_proba(raw_logits.reshape(-1, 1))[:, 1]
                else:
                    calibrated_probs = self.calibrator.predict(raw_logits)
            else:
                calibrated_probs = raw_logits
        except Exception as e:
            logger.warning(f"Calibration failed: {e}. Falling back to raw logits.")
            calibrated_probs = raw_logits
            
        duration = time.time() - start_time
        
        # 5. Build Reports
        results = []

        for i, raw in enumerate(raw_logits):
            decoder = TargetManager.get_decoder(self.manifest)
            current_raw_features = raw_sequences[i]
            decoded = decoder.decode(raw, current_raw_features, self.manifest, calibrator=self.calibrator)
            
            report = {
                "Model Version": self.active_version,
                "Inference Timestamp": pd.Timestamp.utcnow().isoformat(),
                "Execution Duration": duration,
                "Manifest Hash": self.manifest.get("artifacts", {}).get("model.pt", self.manifest.get("artifacts", {}).get("best_model.keras", "unknown"))
            }
            report.update(decoded)
            results.append(report)
            
        return results
