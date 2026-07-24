"""
ml_engine/data/tensors/builder.py
─────────────────────────────────────────────────────────────────────────────
Orchestrates the tensor creation workflow.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import glob
import logging
import pandas as pd
import numpy as np
from typing import List, Tuple
import joblib
import hashlib
from sklearn.preprocessing import StandardScaler

from ml_engine.data.tensors.targets.manager import TargetManager
from ml_engine.core.types import TaskType
from ml_engine.config.training_config import TrainingConfig
from ml_engine.data.tensors.window_generator import WindowGenerator
from ml_engine.data.tensors.splitter import ChronologicalSplitter
from ml_engine.data.tensors.validator import TensorValidator
from ml_engine.data.tensors.metadata import MetadataGenerator
from ml_engine.data.tensors.serializer import TensorSerializer
from ml_engine.config.training_config import training_config
from ml_engine.config.settings import DATASET_STORAGE_ROOT

logger = logging.getLogger(__name__)


class TensorBuilder:
    """End-to-end orchestrator for Tensor Dataset Generation."""

    @staticmethod
    def build_all(dataset_version: str, output_base: str = "ml_engine/data/tensors", force: bool = False, resume: bool = False):
        """
        Builds tensors for all tickers found in the given dataset version.
        
        Args:
            dataset_version: e.g. "CORE/v1.0"
            output_base: Root for outputs
            force: Overwrite existing
            resume: Skip existing
        """
        logger.info(f"=== Tensor Builder Started for {dataset_version} ===")
        
        input_base = os.path.join(DATASET_STORAGE_ROOT, dataset_version)
        output_dir = os.path.join(output_base, dataset_version)
        
        if not os.path.exists(input_base):
            logger.error(f"[TensorBuilder] Input path not found: {input_base}")
            raise FileNotFoundError(f"Missing input dataset: {input_base}")
            
        # Find all data.parquet files
        parquet_files = glob.glob(os.path.join(input_base, "ticker=*", "data.parquet"))
        if not parquet_files:
            logger.error(f"[TensorBuilder] No data.parquet files found in {input_base}")
            raise FileNotFoundError(f"No parquet files in {input_base}")
            
        logger.info(f"[TensorBuilder] Found {len(parquet_files)} tickers.")
        
        # We will concatenate all dataframes together chronologically, 
        # or build windows per ticker and then concat, which is safer for time boundaries.
        
        X_train_list, y_train_list = [], []
        X_val_list, y_val_list = [], []
        X_test_list, y_test_list = [], []
        
        feature_cols = None
        processed_data = []
        
        # --- PASS 1: Split Chronologically and Collect Training Data for Scaler Fitting ---
        for p_file in parquet_files:
            ticker = os.path.basename(os.path.dirname(p_file)).replace("ticker=", "")
            logger.info(f"[TensorBuilder] Pass 1 (Scaler Fitting): {ticker}")
            
            df = pd.read_parquet(p_file)
            
            # 1. Add Target explicitly from TargetStrategy
            target_strategy = TargetManager.get_strategy(TrainingConfig)
            df, target_cols = target_strategy.generate(df, TrainingConfig.target)
            
            if feature_cols is None:
                # Use all columns except ticker and targets
                exclude = {"ticker"}.union(set(target_cols))
                feature_cols = [c for c in df.columns if c not in exclude]
                
            train_df, val_df, test_df = ChronologicalSplitter.split_by_date(df)
            processed_data.append((ticker, df, train_df, val_df, test_df, target_cols))
            
        # Fit Global StandardScaler on all train data
        logger.info("[TensorBuilder] Fitting Global StandardScaler on combined training data...")
        all_train_features = pd.concat([item[2][feature_cols] for item in processed_data])
        scaler = StandardScaler()
        scaler.fit(all_train_features)
        
        # Save Scaler
        os.makedirs(output_dir, exist_ok=True)
        scaler_path = os.path.join(output_dir, "scaler.pkl")
        joblib.dump(scaler, scaler_path)
        logger.info(f"[TensorBuilder] Scaler saved to {scaler_path}")
        
        # Calculate Scaler Checksum for Metadata
        with open(scaler_path, "rb") as f:
            scaler_checksum = hashlib.sha256(f.read()).hexdigest()
            
        scaler_info = {
            "scaler_type": "StandardScaler",
            "scaler_checksum": scaler_checksum
        }
        
        # --- PASS 2: Apply Scaler and Generate Sequences ---
        for ticker, df, train_df, val_df, test_df, target_cols in processed_data:
            logger.info(f"[TensorBuilder] Pass 2 (Sequence Generation): {ticker}")
            
            # Apply Scaling
            df_scaled = df.copy()
            df_scaled[feature_cols] = scaler.transform(df[feature_cols])
            
            def build_windows(data_df: pd.DataFrame, is_val_or_test=False) -> Tuple[np.ndarray, np.ndarray]:
                if len(data_df) == 0:
                    return np.array([]), np.array([])
                    
                X_list, y_list = [], []
                seq_len = training_config.SEQUENCE_LENGTH
                
                # Convert to numpy for speed
                X_mat = data_df[feature_cols].values
                y_mat = data_df[target_cols].values
                
                start_idx = seq_len if is_val_or_test else 0
                for i in range(start_idx, len(data_df) - seq_len + 1):
                    X_list.append(X_mat[i : i + seq_len])
                    # Ensure y is always 1D per sample if single target, or 1D array if multi-target
                    y_val = y_mat[i + seq_len - 1]
                    if len(target_cols) == 1:
                        y_val = y_val[0]
                    y_list.append(y_val)
                    
                return np.array(X_list), np.array(y_list)
            
            # Re-split chronologically from the scaled dataframe
            train_df, val_df, test_df = ChronologicalSplitter.split_by_date(df_scaled)
            
            # Prepend history to val and test for windowing
            seq_len = training_config.SEQUENCE_LENGTH
            if len(train_df) >= seq_len - 1 and len(val_df) > 0:
                history = train_df.iloc[-(seq_len - 1):]
                val_df = pd.concat([history, val_df])
                
            if len(df_scaled.loc[:training_config.VAL_END_DATE]) >= seq_len - 1 and len(test_df) > 0:
                history = df_scaled.loc[:training_config.VAL_END_DATE].iloc[-(seq_len - 1):]
                test_df = pd.concat([history, test_df])
            
            # 3. Window
            Xt, yt = build_windows(train_df, is_val_or_test=False)
            Xv, yv = build_windows(val_df, is_val_or_test=True)
            Xts, yts = build_windows(test_df, is_val_or_test=True)
            
            if len(Xt) > 0: X_train_list.append(Xt); y_train_list.append(yt)
            if len(Xv) > 0: X_val_list.append(Xv); y_val_list.append(yv)
            if len(Xts) > 0: X_test_list.append(Xts); y_test_list.append(yts)
            
        # Concat all tickers
        logger.info("[TensorBuilder] Concatenating tensors...")
        X_train = np.concatenate(X_train_list) if X_train_list else np.array([])
        y_train = np.concatenate(y_train_list) if y_train_list else np.array([])
        
        X_val = np.concatenate(X_val_list) if X_val_list else np.array([])
        y_val = np.concatenate(y_val_list) if y_val_list else np.array([])
        
        X_test = np.concatenate(X_test_list) if X_test_list else np.array([])
        y_test = np.concatenate(y_test_list) if y_test_list else np.array([])
        
        # 4. Validate
        logger.info("[TensorBuilder] Validating tensors...")
        task_type = getattr(training_config.target, "task_type", TaskType.BINARY_CLASSIFICATION)
        expected_targets = len(target_cols)
        valid = TensorValidator.validate(X_train, y_train, len(feature_cols), training_config.SEQUENCE_LENGTH, task_type, expected_targets)
        valid = valid and (len(X_val) == 0 or TensorValidator.validate(X_val, y_val, len(feature_cols), training_config.SEQUENCE_LENGTH, task_type, expected_targets))
        valid = valid and (len(X_test) == 0 or TensorValidator.validate(X_test, y_test, len(feature_cols), training_config.SEQUENCE_LENGTH, task_type, expected_targets))
        
        if not valid:
            logger.error("[TensorBuilder] Tensor validation failed. Aborting serialization.")
            raise ValueError("Tensor validation failed.")
            
        # 5. Metadata
        target_dist = {}
        if len(y_train) > 0 and len(y_train.shape) == 1 and y_train.dtype in (int, np.int32, np.int64):
            # Only calculate distribution for classification (1D integer targets)
            unique, counts = np.unique(y_train, return_counts=True)
            target_dist = {str(k): int(v) for k, v in zip(unique, counts)}
        
        meta = MetadataGenerator.generate(
            dataset_version,
            feature_cols,
            X_train.shape,
            X_val.shape,
            X_test.shape,
            target_dist,
            scaler_info,
            target_cols
        )
        
        # 6. Serialize
        if resume and os.path.exists(os.path.join(output_dir, "metadata.json")) and not force:
            logger.info("[TensorBuilder] Found existing metadata and --resume is set. Skipping save.")
            return
            
        TensorSerializer.save(output_dir, X_train, y_train, X_val, y_val, X_test, y_test, meta)
        logger.info(f"=== Tensor Builder Complete: {dataset_version} ===")
