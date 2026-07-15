"""
ml_engine/data/tensors/window_generator.py
─────────────────────────────────────────────────────────────────────────────
Generates overlapping sequences from time series data.
─────────────────────────────────────────────────────────────────────────────
"""
import numpy as np
import pandas as pd
from typing import Tuple
from ml_engine.config.training_config import training_config


class WindowGenerator:
    """Slices a feature dataframe into sequential windows and corresponding targets."""

    @staticmethod
    def generate(df: pd.DataFrame, feature_cols: list) -> Tuple[np.ndarray, np.ndarray]:
        """
        Creates sequences of length `training_config.SEQUENCE_LENGTH`.
        
        Args:
            df: DataFrame containing features and a 'target' column.
            feature_cols: List of column names to use as features.
            
        Returns:
            X: Array of shape (N, seq_len, num_features)
            y: Array of shape (N,)
        """
        seq_len = training_config.SEQUENCE_LENGTH
        
        if len(df) < seq_len:
            return np.array([]), np.array([])
            
        # Extract raw arrays
        features_array = df[feature_cols].values
        target_array = df["target"].values
        
        X, y = [], []
        # Stride of 1 for overlapping windows
        for i in range(len(df) - seq_len + 1):
            window = features_array[i : i + seq_len]
            # Target is aligned with the END of the window
            target = target_array[i + seq_len - 1]
            
            X.append(window)
            y.append(target)
            
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
