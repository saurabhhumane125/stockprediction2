import os
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

from ml_engine.interfaces.base_trainer import BaseTrainer
from ml_engine.config.training_config import training_config
from ml_engine.data.storage.numpy_storage import NumpyStorage

logger = logging.getLogger(__name__)


class KerasTrainer(BaseTrainer):
    """
    Production Training Engine for TensorFlow/Keras models.
    Supports checkpoints, callbacks, deterministic execution, and artifact saving.
    """

    def __init__(self, tensor_storage: NumpyStorage, artifact_dir: str):
        self.tensor_storage = tensor_storage
        self.artifact_dir = artifact_dir
        os.makedirs(self.artifact_dir, exist_ok=True)
        
        # Enforce deterministic execution
        tf.keras.utils.set_random_seed(42)
        tf.config.experimental.enable_op_determinism()

    def train(self, model_builder: callable, data_path: str, resume: bool = False) -> tf.keras.Model:
        """
        Executes the training loop.
        
        Args:
            model_builder (callable): Function returning a compiled tf.keras.Model.
            data_path (str): Path relative to NumpyStorage for loading tensors (e.g. TICKER/v1).
            resume (bool): Whether to resume from the latest checkpoint if it exists.
        """
        start_time = time.time()
        logger.info(f"Starting Training Engine for data path: {data_path}")
        
        # 1. Load Data
        train_arrays = self.tensor_storage.load_arrays(f"{data_path}/train.npz")
        val_arrays = self.tensor_storage.load_arrays(f"{data_path}/val.npz")
        
        X_train, y_train = train_arrays["X"], train_arrays["y"]
        X_val, y_val = val_arrays["X"], val_arrays["y"]
        
        if len(X_train) == 0 or len(X_val) == 0:
            raise ValueError("Insufficient data for training or validation.")
            
        input_shape = (X_train.shape[1], X_train.shape[2])
        
        # 2. Build or Resume Model
        checkpoint_path = os.path.join(self.artifact_dir, "best_model.keras")
        if resume and os.path.exists(checkpoint_path):
            logger.info(f"Resuming training from checkpoint: {checkpoint_path}")
            model = tf.keras.models.load_model(checkpoint_path)
        else:
            tf.keras.backend.clear_session()
            model = model_builder(
                input_shape=input_shape,
                hidden_size=training_config.HIDDEN_SIZE,
                dropout=training_config.DROPOUT,
                learning_rate=training_config.LEARNING_RATE
            )
            
        # 3. tf.data.Dataset Pipeline
        train_ds = tf.data.Dataset.from_tensor_slices((X_train, y_train))
        train_ds = train_ds.shuffle(buffer_size=len(X_train), seed=42).batch(training_config.BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
        
        val_ds = tf.data.Dataset.from_tensor_slices((X_val, y_val)).batch(training_config.BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
        
        # 4. Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss', 
                patience=training_config.EARLY_STOPPING_PATIENCE, 
                restore_best_weights=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                filepath=checkpoint_path,
                monitor='val_loss',
                save_best_only=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            )
        ]
        
        # 5. Execute Training
        logger.info(f"Executing model.fit() for max {training_config.EPOCHS} epochs.")
        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=training_config.EPOCHS,
            callbacks=callbacks,
            verbose=1
        )
        
        duration = time.time() - start_time
        logger.info(f"Training completed in {duration:.2f}s")
        
        # 6. Artifact Generation
        self._save_artifacts(history.history, duration)
        
        return model

    def evaluate(self, model: tf.keras.Model, data_path: str) -> Dict[str, float]:
        """
        Evaluate the model on out-of-sample data.
        """
        test_arrays = self.tensor_storage.load_arrays(f"{data_path}/test.npz")
        X_test, y_test = test_arrays["X"], test_arrays["y"]
        
        if len(X_test) == 0:
            raise ValueError("Insufficient testing data.")
            
        test_ds = tf.data.Dataset.from_tensor_slices((X_test, y_test)).batch(training_config.BATCH_SIZE)
        
        results = model.evaluate(test_ds, verbose=0)
        # Assumes model was compiled with loss and accuracy
        metrics = {
            "loss": results[0],
            "accuracy": results[1]
        }
        
        logger.info(f"Evaluation Metrics: {metrics}")
        return metrics

    def _save_artifacts(self, history_dict: Dict[str, Any], duration: float):
        """
        Saves training history, hashes and metadata.
        """
        # Convert float32 objects from TF history to float for JSON serialization
        history_clean = {}
        for k, v_list in history_dict.items():
            history_clean[k] = [float(val) for val in v_list]
            
        best_val_loss = min(history_clean.get("val_loss", [float("inf")]))
            
        metadata = {
            "timestamp": pd.Timestamp.utcnow().isoformat(),
            "execution_time_seconds": duration,
            "best_val_loss": best_val_loss,
            "training_config_hash": hashlib.md5(str(training_config.to_dict()).encode()).hexdigest(),
            "config": training_config.to_dict(),
            "epochs_run": len(history_clean.get("loss", []))
        }
        
        with open(os.path.join(self.artifact_dir, "training_history.json"), "w") as f:
            json.dump(history_clean, f, indent=4)
            
        with open(os.path.join(self.artifact_dir, "training_summary.json"), "w") as f:
            json.dump(metadata, f, indent=4)
