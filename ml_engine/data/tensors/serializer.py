"""
ml_engine/data/tensors/serializer.py
─────────────────────────────────────────────────────────────────────────────
Serializes numpy arrays into PyTorch .pt formats and JSON metadata.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)


class TensorSerializer:
    """Persists ML-ready datasets."""

    @staticmethod
    def save(
        output_dir: str, 
        X_train: np.ndarray, y_train: np.ndarray,
        X_val: np.ndarray, y_val: np.ndarray,
        X_test: np.ndarray, y_test: np.ndarray,
        metadata: dict
    ):
        """Saves tensors and metadata to disk."""
        import torch
        
        logger.info(f"[Serializer] Saving tensors to {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save Tensors
        if X_train.shape[0] > 0:
            torch.save((torch.from_numpy(X_train), torch.from_numpy(y_train)), os.path.join(output_dir, "train.pt"))
        if X_val.shape[0] > 0:
            torch.save((torch.from_numpy(X_val), torch.from_numpy(y_val)), os.path.join(output_dir, "val.pt"))
        if X_test.shape[0] > 0:
            torch.save((torch.from_numpy(X_test), torch.from_numpy(y_test)), os.path.join(output_dir, "test.pt"))
            
        # Save Metadata
        with open(os.path.join(output_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)
            
        # Save feature mapping explicitly for easy downstream lookup
        with open(os.path.join(output_dir, "feature_mapping.json"), "w") as f:
            json.dump(metadata["features"], f, indent=4)
            
        logger.info("[Serializer] Serialization complete.")
