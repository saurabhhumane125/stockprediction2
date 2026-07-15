import os
import json
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NumpyStorage:
    """
    Storage layer for multi-dimensional numpy arrays (Tensors).
    Uses compressed .npz format with atomic writes.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def exists(self, path: str) -> bool:
        return os.path.exists(os.path.join(self.base_path, path))

    def save_arrays(self, path: str, **arrays: np.ndarray) -> None:
        """
        Save multiple numpy arrays into a single compressed .npz file.
        e.g., save_arrays("train.npz", X=X_train, y=y_train)
        """
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        temp_path = f"{full_path}.tmp"
        try:
            with open(temp_path, "wb") as f:
                np.savez_compressed(f, **arrays)
            if os.path.exists(full_path):
                os.replace(temp_path, full_path)
            else:
                os.rename(temp_path, full_path)
            logger.info(f"Saved arrays to {full_path}")
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Failed to save arrays to {full_path}: {e}")
            raise

    def load_arrays(self, path: str) -> Dict[str, np.ndarray]:
        """
        Load arrays from an .npz file.
        """
        full_path = os.path.join(self.base_path, path)
        if not self.exists(path):
            raise FileNotFoundError(f"Array file not found at {full_path}")
            
        data = np.load(full_path)
        logger.info(f"Loaded arrays from {full_path}")
        # Convert NpzFile to dict so it doesn't keep the file open
        return {k: data[k] for k in data.files}

    def save_metadata(self, metadata: Dict[str, Any], path: str) -> None:
        """
        Save JSON metadata sidecar.
        """
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        temp_path = f"{full_path}.tmp"
        try:
            with open(temp_path, "w") as f:
                json.dump(metadata, f, indent=4)
            if os.path.exists(full_path):
                os.replace(temp_path, full_path)
            else:
                os.rename(temp_path, full_path)
            logger.info(f"Saved metadata to {full_path}")
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Failed to save metadata to {full_path}: {e}")
            raise
