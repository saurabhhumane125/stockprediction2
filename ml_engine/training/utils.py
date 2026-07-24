"""
ml_engine/training/utils.py
─────────────────────────────────────────────────────────────────────────────
Shared training utilities:
  • seed_everything  – deterministic seeding across python / numpy / torch / cuda
  • TimeSeriesDataset – thin torch Dataset wrapping .npz tensor files
─────────────────────────────────────────────────────────────────────────────
"""
import os
import random
import logging
from typing import Tuple

import numpy as np

logger = logging.getLogger(__name__)


def seed_everything(seed: int = 42) -> None:
    """
    Guarantee reproducible training across all random-number generators.

    Covers:
        - Python's built-in ``random`` module
        - ``os.environ['PYTHONHASHSEED']``
        - ``numpy.random``
        - ``torch`` (CPU and CUDA, if available)

    Args:
        seed: Integer seed value. Defaults to 42.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            # Enforce deterministic CUDA kernels where possible
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        logger.debug(f"[seed_everything] All RNGs seeded with seed={seed} (torch included).")
    except ImportError:
        logger.debug(f"[seed_everything] torch not available – only numpy/python RNGs seeded.")


# ─── PyTorch Dataset ────────────────────────────────────────────────────────

try:
    import torch
    from torch.utils.data import Dataset

    class TimeSeriesDataset(Dataset):
        """
        Thin ``torch.utils.data.Dataset`` wrapper around pre-built .npz tensors.

        Expected .npz layout::

            X: shape (N, sequence_length, n_features)   float32
            y: shape (N,)                                int64 / float32

        Args:
            X: Feature array of shape (N, T, F).
            y: Target array of shape (N,).
        """

        def __init__(self, X: np.ndarray, y: np.ndarray, y_dtype=None) -> None:
            if len(X) != len(y):
                raise ValueError(
                    f"X and y must have the same number of samples, "
                    f"got X={len(X)} y={len(y)}."
                )
            self.X = torch.tensor(X, dtype=torch.float32)
            
            # Default to torch.long for backward compatibility with legacy classification models.
            # TrainingOrchestrator explicitly overrides this for regression tasks.
            if y_dtype is None:
                y_dtype = torch.long
                
            self.y = torch.tensor(y, dtype=y_dtype)

        def __len__(self) -> int:
            return len(self.X)

        def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
            return self.X[idx], self.y[idx]

        @property
        def input_shape(self) -> Tuple[int, int]:
            """Returns (sequence_length, n_features)."""
            return (self.X.shape[1], self.X.shape[2])

except ImportError:
    # If torch is not installed, provide a graceful placeholder
    # so that config / reporting modules that import this file still work.
    class TimeSeriesDataset:  # type: ignore[no-redef]
        """Placeholder – install PyTorch to use this class."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "PyTorch is required to use TimeSeriesDataset. "
                "Install it with: pip install torch"
            )
