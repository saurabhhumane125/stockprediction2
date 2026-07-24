import os
import glob
import logging
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from ml_engine.config.settings import DATASET_STORAGE_ROOT
from ml_engine.data.tensors.targets.strategies.legacy import LegacyTargetStrategy
from ml_engine.data.tensors.targets.strategies.vol_adjusted import VolatilityAdjustedTargetStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DummyTargetConfig:
    pass

def validate_targets(dataset_version: str):
    input_base = os.path.join(DATASET_STORAGE_ROOT, dataset_version)
    parquet_files = glob.glob(os.path.join(input_base, "ticker=*", "data.parquet"))
    
    if not parquet_files:
        logger.error(f"No parquet files found for {dataset_version}")
        return
        
    logger.info(f"Validating across {len(parquet_files)} tickers...")
    
    raw_returns = []
    vol_targets = []
    
    vol_strat = VolatilityAdjustedTargetStrategy()
    config = DummyTargetConfig()
    
    for i, p_file in enumerate(parquet_files[:50]): # Sample 50 tickers
        df = pd.read_parquet(p_file)
        
        # Raw Return_5d
        df_raw = df.copy()
        df_raw["return_5d"] = (df_raw["close"].shift(-5) - df_raw["close"]) / df_raw["close"]
        
        # Vol-Adjusted Target
        df_vol, cols_vol = vol_strat.generate(df, config)
        
        # Align rows by dropping NaNs from raw where vol has NaNs
        df_aligned = pd.merge(df_raw[["return_5d"]], df_vol[[cols_vol[0]]], left_index=True, right_index=True, how="inner")
        df_aligned = df_aligned.dropna()
        
        raw_returns.extend(df_aligned["return_5d"].values)
        vol_targets.extend(df_aligned[cols_vol[0]].values)
        
    raw_returns = np.array(raw_returns)
    vol_targets = np.array(vol_targets)
    
    logger.info("=== TARGET VALIDATION REPORT ===")
    logger.info(f"Aligned Target Count: {len(raw_returns)}")
    
    # Statistical comparison
    def print_stats(name, data):
        logger.info(f"--- {name} ---")
        logger.info(f"Mean: {np.mean(data):.4f}")
        logger.info(f"Median: {np.median(data):.4f}")
        logger.info(f"StdDev: {np.std(data):.4f}")
        logger.info(f"Min: {np.min(data):.4f}")
        logger.info(f"Max: {np.max(data):.4f}")
        logger.info(f"Skewness: {stats.skew(data):.4f}")
        logger.info(f"Kurtosis: {stats.kurtosis(data):.4f}")
        outliers = np.sum(np.abs(data - np.mean(data)) > 3 * np.std(data))
        logger.info(f"Outliers (>3 std): {outliers} ({outliers/len(data)*100:.2f}%)")
        
    print_stats("Raw Return_5d Target", raw_returns)
    print_stats("Vol-Adjusted Target", vol_targets)
    
    logger.info("Validation complete.")

if __name__ == "__main__":
    validate_targets("NIFTY50/v2.0")
