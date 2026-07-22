"""
ml_engine/models/bigru/bigru_classifier.py
─────────────────────────────────────────────────────────────────────────────
Production PyTorch Bidirectional GRU classifier for time-series classification.

Architecture
  Input  (batch, seq, features)
    └─ nn.GRU (bidirectional=True)  → (batch, seq, 2*hidden_size)
        └─ Concatenated last forward + last backward hidden states
            └─ LayerNorm / BatchNorm (configurable)
                └─ Dropout
                    └─ Linear(2*hidden_size → output_classes)
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Optional

import torch
import torch.nn as nn

from ml_engine.models.base_model import BaseTimeSeriesClassifier
from ml_engine.models.weight_init import apply_weight_init

logger = logging.getLogger(__name__)


class BiGRUClassifier(BaseTimeSeriesClassifier):
    """
    Multi-layer Bidirectional GRU classifier for financial time-series.

    The representation is formed by concatenating the final forward and
    backward hidden states of the top GRU layer, giving a vector of
    size ``2 * hidden_size`` before the classification head.

    Args:
        input_size:     Number of features per time step.
        hidden_size:    Number of GRU hidden units *per direction*.
        num_layers:     Number of stacked bidirectional GRU layers.
        output_classes: Number of output logit classes.
        dropout:        Dropout probability.
        normalization:  ``"layer"`` | ``"batch"`` | ``"none"``.
        weight_init:    Weight initialisation strategy name.
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        output_classes: int = 2,
        dropout: float = 0.3,
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
            bidirectional=True,
            dropout=gru_dropout,
        )

        # After concatenation the size doubles
        combined_size = hidden_size * 2
        self.norm = _build_norm(normalization, combined_size)
        self.dropout = nn.Dropout(p=dropout)
        self.classifier = nn.Linear(combined_size, output_classes)

        apply_weight_init(self, weight_init)
        logger.debug(
            f"[BiGRUClassifier] input={input_size} hidden={hidden_size} "
            f"layers={num_layers} classes={output_classes}"
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: ``(batch, seq_len, input_size)``
        Returns:
            Logits ``(batch, output_classes)``
        """
        # h_n shape: (num_layers * 2, batch, hidden_size)
        _, h_n = self.gru(x)

        # Extract top-layer forward and backward hidden states
        # Forward: h_n[-2], Backward: h_n[-1]
        forward_h = h_n[-2]     # (batch, hidden_size)
        backward_h = h_n[-1]    # (batch, hidden_size)
        combined = torch.cat([forward_h, backward_h], dim=1)  # (batch, 2*hidden)

        if self.norm is not None:
            combined = self.norm(combined)
        combined = self.dropout(combined)
        return self.classifier(combined)


def _build_norm(normalization: str, size: int):
    key = normalization.lower()
    if key == "layer":
        return nn.LayerNorm(size)
    elif key == "batch":
        return nn.BatchNorm1d(size)
    return None
