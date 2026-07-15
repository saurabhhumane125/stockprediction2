"""
ml_engine/data/tensors/dataset.py
─────────────────────────────────────────────────────────────────────────────
PyTorch Dataset definition for consumption by TrainingRunner.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import torch
from torch.utils.data import Dataset
import logging

logger = logging.getLogger(__name__)


class TimeSeriesDataset(Dataset):
    """
    Standard PyTorch Dataset for pre-sliced time series data.
    """
    def __init__(self, tensor_dir: str, split: str = "train"):
        """
        Loads the pre-saved PyTorch tensors.
        """
        super().__init__()
        
        path = os.path.join(tensor_dir, f"{split}.pt")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing dataset partition: {path}")
            
        logger.info(f"[TimeSeriesDataset] Loading {split} partition from {path}")
        self.X, self.y = torch.load(path, weights_only=True)
        
    def __len__(self):
        return len(self.X)
        
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
