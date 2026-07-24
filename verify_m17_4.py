import os
import torch
import numpy as np
from torch.utils.data import DataLoader

def investigate():
    print("--- STARTING M17.4 RUNTIME DTYPE INVESTIGATION ---")
    
    # STAGE 1: Immediately after loading train.pt
    train_path = "ml_engine/data/tensors/NIFTY50/v3.0/train.pt"
    train_X_tensor, train_y_tensor = torch.load(train_path)
    
    print("\nSTAGE 1")
    print(f"dtype: {train_y_tensor.dtype}")
    print(f"shape: {train_y_tensor.shape}")
    print(f"first 10 values: {train_y_tensor[:10].tolist()}")
    
    # Simulate training_pipeline.py _load() returning numpy arrays
    train_y_np = train_y_tensor.numpy()
    
    # STAGE 2: Immediately before TimeSeriesDataset stores y
    print("\nSTAGE 2")
    print(f"dtype: {train_y_np.dtype}")
    print(f"shape: {train_y_np.shape}")
    print(f"first 10 values: {train_y_np[:10].tolist()}")
    
    # STAGE 3: Immediately after self.y = torch.tensor(y, dtype=torch.long)
    # Simulate TimeSeriesDataset
    class MockTimeSeriesDataset:
        def __init__(self, X, y):
            self.X = torch.tensor(X, dtype=torch.float32)
            self.y = torch.tensor(y, dtype=torch.long)
            
        def __len__(self):
            return len(self.X)
            
        def __getitem__(self, idx):
            return self.X[idx], self.y[idx]
            
    train_ds = MockTimeSeriesDataset(train_X_tensor.numpy(), train_y_np)
    
    print("\nSTAGE 3")
    print(f"dtype: {train_ds.y.dtype}")
    print(f"shape: {train_ds.y.shape}")
    print(f"first 10 values: {train_ds.y[:10].tolist()}")
    
    # STAGE 4: First batch returned by DataLoader
    loader = DataLoader(train_ds, batch_size=48, shuffle=False)
    X_batch, y_batch = next(iter(loader))
    
    print("\nSTAGE 4")
    print(f"dtype: {y_batch.dtype}")
    print(f"shape: {y_batch.shape}")
    print(f"first 10 values: {y_batch[:10].tolist()}")
    
    # STAGE 5: Beginning of _train_epoch() Before any casting
    # (Matches Stage 4 essentially, but let's log it explicitly)
    y_batch_st5 = y_batch.clone()
    print("\nSTAGE 5")
    print(f"dtype: {y_batch_st5.dtype}")
    print(f"shape: {y_batch_st5.shape}")
    print(f"first 10 values: {y_batch_st5[:10].tolist()}")
    
    # STAGE 6: Immediately before loss computation
    # In training_pipeline.py: y_batch = y_batch.float().to(device)
    y_batch_st6 = y_batch_st5.float()
    print("\nSTAGE 6")
    print(f"dtype: {y_batch_st6.dtype}")
    print(f"shape: {y_batch_st6.shape}")
    print(f"first 10 values: {y_batch_st6[:10].tolist()}")

if __name__ == "__main__":
    investigate()
