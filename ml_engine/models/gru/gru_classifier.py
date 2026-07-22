"""
ml_engine/models/gru/gru_classifier.py
─────────────────────────────────────────────────────────────────────────────
Production PyTorch GRU classifier for time-series classification.

Architecture
  Input  (batch, seq, features)
    └─ nn.GRU  [num_layers, hidden_size, dropout]
        └─ Last hidden state (batch, hidden_size)
            └─ LayerNorm / BatchNorm (configurable)
                └─ Dropout
                    └─ Linear → logits  (batch, output_classes)

NOTE: The existing ``ml_engine/models/gru/builder.py`` (Keras) is intentionally
preserved — the legacy inference engine loads it. This file sits alongside it
and is used exclusively by the new PyTorch TrainingOrchestrator.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple

import torch
import torch.nn as nn

from ml_engine.models.base_model import BaseTimeSeriesClassifier
from ml_engine.models.weight_init import apply_weight_init

logger = logging.getLogger(__name__)


class GRUClassifier(BaseTimeSeriesClassifier):
    """
    Multi-layer GRU classifier for financial time-series.

    Args:
        input_size:     Number of features per time step.
        hidden_size:    Number of GRU hidden units.
        num_layers:     Number of stacked GRU layers.
        output_classes: Number of output logit classes.
        dropout:        Dropout probability (applied between GRU layers and
                        before the classification head).
        normalization:  ``"layer"`` | ``"batch"`` | ``"none"``.
        weight_init:    Weight initialisation strategy name.
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_classes: int = 2,
        dropout: float = 0.2,
        normalization: str = "layer",
        weight_init: str = "xavier_uniform",
    ) -> None:
        super().__init__(input_size=input_size, output_classes=output_classes)

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        gru_dropout = dropout if num_layers > 1 else 0.0
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=gru_dropout,
        )

        self.norm = _build_norm(normalization, hidden_size)
        self.dropout = nn.Dropout(p=dropout)
        self.classifier = nn.Linear(hidden_size, output_classes)

        apply_weight_init(self, weight_init)
        logger.debug(
            f"[GRUClassifier] input={input_size} hidden={hidden_size} "
            f"layers={num_layers} classes={output_classes}"
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: ``(batch, seq_len, input_size)``
        Returns:
            Logits ``(batch, output_classes)``
        """
        _, h_n = self.gru(x)          # h_n: (num_layers, batch, hidden)
        last_hidden = h_n[-1]          # take top-layer hidden state
        if self.norm is not None:
            last_hidden = self.norm(last_hidden)
        last_hidden = self.dropout(last_hidden)
        return self.classifier(last_hidden)


# ── Shared helper ──────────────────────────────────────────────────────────

def _build_norm(normalization: str, size: int) -> Optional[nn.Module]:
    """Return the requested normalisation layer or None."""
    key = normalization.lower()
    if key == "layer":
        return nn.LayerNorm(size)
    elif key == "batch":
        return nn.BatchNorm1d(size)
    return None
