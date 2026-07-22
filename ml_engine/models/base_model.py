"""
ml_engine/models/base_model.py
─────────────────────────────────────────────────────────────────────────────
Abstract base class for all production PyTorch classification models.

Every concrete architecture (GRU, BiGRU, LSTM, Transformer) must inherit
from ``BaseTimeSeriesClassifier`` and implement ``forward()``.

Provides:
  • ``save(path)``         – persist state-dict to disk
  • ``load(path, device)`` – restore state-dict from disk
  • ``predict(X)``         – batched inference returning class labels + probs
  • ``parameter_count()``  – trainable / non-trainable parameter counts
  • ``summary()``          – human-readable model summary dict
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class BaseTimeSeriesClassifier(ABC, nn.Module):
    """
    Abstract base class for all production time-series classification models.

    Subclasses must implement ``forward(x: Tensor) -> Tensor`` which receives
    an input of shape ``(batch, sequence_length, n_features)`` and returns
    logits of shape ``(batch, output_classes)``.

    Args:
        input_size:     Number of input features per time step.
        output_classes: Number of output logit dimensions (default 2).
    """

    def __init__(self, input_size: int, output_classes: int) -> None:
        super().__init__()
        self.input_size = input_size
        self.output_classes = output_classes

    # ── Abstract ──────────────────────────────────────────────────────────────

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor of shape ``(batch, sequence_length, input_size)``.

        Returns:
            Logits tensor of shape ``(batch, output_classes)``.
        """
        ...

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """
        Persist the model state-dict to *path*.

        Args:
            path: Absolute file path (e.g. ``"artifacts/model.pt"``).
        """
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        torch.save(self.state_dict(), path)
        logger.info(f"[{self.__class__.__name__}] State-dict saved → {path}")

    def load(self, path: str, device: str = "cpu") -> "BaseTimeSeriesClassifier":
        """
        Load state-dict from *path* into this model in-place.

        Args:
            path:   Path to a ``.pt`` state-dict file.
            device: Target device string (``"cpu"``, ``"cuda"``).

        Returns:
            ``self`` for chaining.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at '{path}'.")
        state = torch.load(path, map_location=device)
        self.load_state_dict(state)
        self.to(device)
        logger.info(f"[{self.__class__.__name__}] State-dict loaded ← {path} (device={device})")
        return self

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict(
        self,
        X: torch.Tensor,
        device: str = "cpu",
        batch_size: int = 256,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Run batched inference on *X*.

        Args:
            X:          Input tensor of shape ``(N, sequence_length, input_size)``.
            device:     Device to run inference on.
            batch_size: Number of samples per mini-batch.

        Returns:
            Tuple of:
              - ``labels``  – predicted class indices, shape ``(N,)``
              - ``probs``   – class probabilities, shape ``(N, output_classes)``
        """
        self.eval()
        self.to(device)
        all_labels, all_probs = [], []

        with torch.no_grad():
            for start in range(0, len(X), batch_size):
                batch = X[start : start + batch_size].to(device)
                logits = self(batch)
                probs = F.softmax(logits, dim=1)
                labels = probs.argmax(dim=1)
                all_labels.append(labels.cpu())
                all_probs.append(probs.cpu())

        return torch.cat(all_labels), torch.cat(all_probs)

    # ── Introspection ─────────────────────────────────────────────────────────

    def parameter_count(self) -> Dict[str, int]:
        """
        Return a dict with trainable and non-trainable parameter counts.

        Returns:
            ``{"trainable": int, "non_trainable": int, "total": int}``
        """
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        non_trainable = sum(p.numel() for p in self.parameters() if not p.requires_grad)
        return {
            "trainable": trainable,
            "non_trainable": non_trainable,
            "total": trainable + non_trainable,
        }

    def summary(self) -> Dict:
        """
        Return a human-readable summary dict suitable for logging or JSON export.

        Returns:
            Dict containing architecture name, input/output dims,
            parameter counts, and estimated memory footprint in MB.
        """
        counts = self.parameter_count()
        # Each float32 parameter ≈ 4 bytes
        mem_mb = round(counts["total"] * 4 / (1024 ** 2), 4)
        return {
            "architecture": self.__class__.__name__,
            "input_size": self.input_size,
            "output_classes": self.output_classes,
            "trainable_params": counts["trainable"],
            "non_trainable_params": counts["non_trainable"],
            "total_params": counts["total"],
            "estimated_memory_mb": mem_mb,
        }
