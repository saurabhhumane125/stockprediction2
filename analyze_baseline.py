import numpy as np
import os
import scipy.stats as stats
import json

base_path = 'artifacts/candidates/NIFTY50/v3.0_run_ba67f51d'

# 1. Load predictions
try:
    test_preds = np.load(os.path.join(base_path, 'test_preds.npy'))
except Exception as e:
    print(f"Failed to load predictions: {e}")
    test_preds = None

# 2. Load targets from the test tensor
import torch
try:
    tensor_path = 'ml_engine/data/tensors/NIFTY50/v3.0/test.pt'
    X, y = torch.load(tensor_path)
    test_y = y.numpy()
except Exception as e:
    print(f"Failed to load targets: {e}")
    test_y = None

if test_preds is not None and test_y is not None:
    print("--- PREDICTION DISTRIBUTION ---")
    print(f"Min: {np.min(test_preds)}")
    print(f"Max: {np.max(test_preds)}")
    print(f"Mean: {np.mean(test_preds)}")
    print(f"Median: {np.median(test_preds)}")
    print(f"Std: {np.std(test_preds)}")
    print(f"Var: {np.var(test_preds)}")
    print(f"Percentiles: [10%: {np.percentile(test_preds, 10)}, 90%: {np.percentile(test_preds, 90)}]")

    print("\n--- TARGET DISTRIBUTION ---")
    print(f"Min: {np.min(test_y)}")
    print(f"Max: {np.max(test_y)}")
    print(f"Mean: {np.mean(test_y)}")
    print(f"Median: {np.median(test_y)}")
    print(f"Std: {np.std(test_y)}")
    print(f"Var: {np.var(test_y)}")
    print(f"Percentiles: [10%: {np.percentile(test_y, 10)}, 90%: {np.percentile(test_y, 90)}]")
    print(f"Skewness: {stats.skew(test_y)}")
    print(f"Kurtosis: {stats.kurtosis(test_y)}")
    
    print("\n--- RESIDUALS ---")
    residuals = test_y - test_preds.flatten()
    print(f"Mean: {np.mean(residuals)}")
    print(f"Median: {np.median(residuals)}")
    print(f"Std: {np.std(residuals)}")
    print(f"Max Error: {np.max(residuals)}")
    print(f"Min Error: {np.min(residuals)}")
