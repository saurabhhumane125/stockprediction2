import torch
import numpy as np
import json
import os
import pandas as pd

def inspect_tensors(dataset_dir):
    features = []
    
    # Load metadata for feature names
    with open(os.path.join(dataset_dir, "metadata.json"), "r") as f:
        meta = json.load(f)
        features = meta["features"]["order"]
        
    all_X = []
    
    for split in ["train.pt", "val.pt", "test.pt"]:
        path = os.path.join(dataset_dir, split)
        if os.path.exists(path):
            X, y = torch.load(path)
            all_X.append(X.numpy())
            
    if not all_X:
        print("No tensors found")
        return
        
    X_global = np.concatenate(all_X, axis=0)
    
    print(f"Global Shape: {X_global.shape}")
    print("=" * 60)
    print(f"{'Feature Name':<20} | {'Dtype':<10} | {'Min':<12} | {'Max':<12} | {'Mean':<12} | {'Std':<12} | {'NaN':<5} | {'Inf':<5}")
    print("-" * 60)
    
    stats_list = []
    
    for i, feature_name in enumerate(features):
        feature_data = X_global[:, :, i]
        
        f_min = float(np.nanmin(feature_data))
        f_max = float(np.nanmax(feature_data))
        f_mean = float(np.nanmean(feature_data))
        f_std = float(np.nanstd(feature_data))
        f_nan = int(np.isnan(feature_data).sum())
        f_inf = int(np.isinf(feature_data).sum())
        
        print(f"{feature_name:<20} | {str(feature_data.dtype):<10} | {f_min:<12.4f} | {f_max:<12.4f} | {f_mean:<12.4f} | {f_std:<12.4f} | {f_nan:<5} | {f_inf:<5}")
        
        stats_list.append({
            "name": feature_name,
            "max_abs": max(abs(f_min), abs(f_max))
        })
        
    print("=" * 60)
    g_min = float(np.nanmin(X_global))
    g_max = float(np.nanmax(X_global))
    g_mean = float(np.nanmean(X_global))
    g_std = float(np.nanstd(X_global))
    
    print("Global Tensor Statistics:")
    print(f"Overall min:  {g_min:.4f}")
    print(f"Overall max:  {g_max:.4f}")
    print(f"Overall mean: {g_mean:.4f}")
    print(f"Overall std:  {g_std:.4f}")
    
    print("=" * 60)
    print("Top 10 largest magnitude features:")
    stats_list.sort(key=lambda x: x["max_abs"], reverse=True)
    for i, s in enumerate(stats_list[:10]):
        print(f"{i+1}. {s['name']} (Max Abs: {s['max_abs']:.4f})")

if __name__ == "__main__":
    inspect_tensors(r"d:\STOCK-PREDICTION-UI\ml_engine\data\tensors\CORE\v1.0")
