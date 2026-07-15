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
from typing import List

from ml_engine.data.tensors.utils import add_target_column
from ml_engine.data.tensors.window_generator import WindowGenerator
from ml_engine.data.tensors.splitter import ChronologicalSplitter
from ml_engine.data.tensors.validator import TensorValidator
from ml_engine.data.tensors.metadata import MetadataGenerator
from ml_engine.data.tensors.serializer import TensorSerializer
from ml_engine.config.training_config import training_config

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
        
        input_base = os.path.join("ml_engine/data/storage/production", dataset_version)
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
        
        for p_file in parquet_files:
            ticker = os.path.basename(os.path.dirname(p_file)).replace("ticker=", "")
            logger.info(f"[TensorBuilder] Processing ticker: {ticker}")
            
            df = pd.read_parquet(p_file)
            
            # 1. Add Target
            df = add_target_column(df)
            
            if feature_cols is None:
                # Use all columns except ticker and target (and index which is usually Date)
                exclude = {"ticker", "target"}
                feature_cols = [c for c in df.columns if c not in exclude]
                
            # 2. Split (Must split before windowing to prevent data leakage!)
            # Wait, if we split before windowing, we lose sequence_length-1 days at the start of val and test.
            # Production robust way: split AFTER windowing OR window train, val, test independently.
            # To avoid data leakage across the exact split boundary, it's safer to window the whole df, 
            # then split chronologically on the window target dates.
            
            # Since the window generator assigns the target of the LAST element of the window,
            # we can window the whole df, and preserve dates to split accurately.
            
            # We'll adapt: WindowGenerator generates arrays. We need to split arrays chronologically.
            # A simple trick: split the DataFrame first, but include `seq_len - 1` historical rows 
            # for val and test from the preceding set. 
            
            train_df, val_df, test_df = ChronologicalSplitter.split_by_date(df)
            
            # Prepend history to val and test for windowing
            seq_len = training_config.SEQUENCE_LENGTH
            if len(train_df) >= seq_len - 1 and len(val_df) > 0:
                history = train_df.iloc[-(seq_len - 1):]
                val_df = pd.concat([history, val_df])
                
            if len(df.loc[:training_config.VAL_END_DATE]) >= seq_len - 1 and len(test_df) > 0:
                history = df.loc[:training_config.VAL_END_DATE].iloc[-(seq_len - 1):]
                test_df = pd.concat([history, test_df])
            
            # 3. Window
            Xt, yt = WindowGenerator.generate(train_df, feature_cols)
            Xv, yv = WindowGenerator.generate(val_df, feature_cols)
            Xts, yts = WindowGenerator.generate(test_df, feature_cols)
            
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
        valid = TensorValidator.validate(X_train, y_train, len(feature_cols), training_config.SEQUENCE_LENGTH)
        valid = valid and (len(X_val) == 0 or TensorValidator.validate(X_val, y_val, len(feature_cols), training_config.SEQUENCE_LENGTH))
        valid = valid and (len(X_test) == 0 or TensorValidator.validate(X_test, y_test, len(feature_cols), training_config.SEQUENCE_LENGTH))
        
        if not valid:
            logger.error("[TensorBuilder] Tensor validation failed. Aborting serialization.")
            raise ValueError("Tensor validation failed.")
            
        # 5. Metadata
        target_dist = {
            "0": int(np.sum(y_train == 0)),
            "1": int(np.sum(y_train == 1))
        } if len(y_train) > 0 else {}
        
        meta = MetadataGenerator.generate(
            dataset_version,
            feature_cols,
            X_train.shape,
            X_val.shape,
            X_test.shape,
            target_dist
        )
        
        # 6. Serialize
        if resume and os.path.exists(os.path.join(output_dir, "metadata.json")) and not force:
            logger.info("[TensorBuilder] Found existing metadata and --resume is set. Skipping save.")
            return
            
        TensorSerializer.save(output_dir, X_train, y_train, X_val, y_val, X_test, y_test, meta)
        logger.info(f"=== Tensor Builder Complete: {dataset_version} ===")
