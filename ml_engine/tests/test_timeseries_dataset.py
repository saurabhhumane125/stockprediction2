import numpy as np
import pytest
import torch
from ml_engine.training.utils import TimeSeriesDataset

def test_timeseries_dataset_default_dtype():
    # By default, for backward compatibility, it should cast to torch.long
    X = np.random.randn(10, 5, 3).astype(np.float32)
    y = np.array([0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8, 0.9, -1.0])
    
    dataset = TimeSeriesDataset(X, y)
    assert dataset.y.dtype == torch.long
    # values will be truncated to 0, or -1 (int casting)
    assert (dataset.y == 0).sum() + (dataset.y == -1).sum() == len(y)

def test_timeseries_dataset_regression_dtype():
    # Explicitly passing torch.float32 should preserve fractions
    X = np.random.randn(10, 5, 3).astype(np.float32)
    y = np.array([0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8, 0.9, -1.0], dtype=np.float32)
    
    dataset = TimeSeriesDataset(X, y, y_dtype=torch.float32)
    assert dataset.y.dtype == torch.float32
    assert torch.allclose(dataset.y, torch.tensor(y))
