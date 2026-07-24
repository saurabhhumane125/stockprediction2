import os
import sys
import pandas as pd
import numpy as np
import glob

# Ensure the root path is in sys.path
sys.path.append(os.path.abspath('.'))

from ml_engine.data.tensors.target_factory import TargetFactory
from ml_engine.config.training_config import TrainingConfig
from ml_engine.config.settings import DATASET_STORAGE_ROOT
from ml_engine.config.training_config import training_config

# 1. Get first parquet file
p_file = glob.glob(os.path.join(DATASET_STORAGE_ROOT, "NIFTY50/v3.0", "ticker=*", "data.parquet"))[0]

# Load only 100 rows
df = pd.read_parquet(p_file).head(100)

# 2. Add Target explicitly from TargetFactory
df, target_cols = TargetFactory.generate(df, TrainingConfig.target)

exclude = {"ticker"}.union(set(target_cols))
feature_cols = [c for c in df.columns if c not in exclude]

# 3. Apply the exact builder.py logic for Y shaping
def build_windows(data_df: pd.DataFrame) -> tuple:
    if len(data_df) == 0:
        return np.array([]), np.array([])
        
    X_list, y_list = [], []
    seq_len = training_config.SEQUENCE_LENGTH
    
    # Convert to numpy for speed
    X_mat = data_df[feature_cols].values
    y_mat = data_df[target_cols].values
    
    start_idx = 0
    for i in range(start_idx, len(data_df) - seq_len + 1):
        X_list.append(X_mat[i : i + seq_len])
        # Ensure y is always 1D per sample if single target, or 1D array if multi-target
        y_val = y_mat[i + seq_len - 1]
        if len(target_cols) == 1:
            y_val = y_val[0]
        y_list.append(y_val)
        
    return np.array(X_list), np.array(y_list)

Xt, yt = build_windows(df)

print(f"Generated X shape: {Xt.shape}")
print(f"Generated Y shape: {yt.shape}")
print(f"Target column names: {target_cols}")
print(f"Feature column names: {feature_cols}")
