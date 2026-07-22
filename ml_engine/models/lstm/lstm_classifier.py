"""
ml_engine/models/lstm/lstm_classifier.py
─────────────────────────────────────────────────────────────────────────────
Production PyTorch LSTM classifier for time-series classification.

Architecture
  Input  (batch, seq, features)
    └─ nn.LSTM  [num_layers, hidden_size, dropout]
        └─ Last hidden state h_n[-1]  (batch, hidden_size)
            └─ LayerNorm / BatchNorm
                └─ Dropout
                    └─ Linear → logits  (batch, output_classes)
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


class LSTMClassifier(BaseTimeSeriesClassifier):
    """
    Multi-layer LSTM classifier for financial time-series.

    Args:
        input_size:     Number of features per time step.
        hidden_size:    Number of LSTM hidden units.
        num_layers:     Number of stacked LSTM layers.
        output_classes: Number of output logit classes.
        dropout:        Dropout probability.
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

        lstm_dropout = dropout if num_layers > 1 else 0.0
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=lstm_dropout,
        )

        self.norm = _build_norm(normalization, hidden_size)
        self.dropout = nn.Dropout(p=dropout)
        self.classifier = nn.Linear(hidden_size, output_classes)

        apply_weight_init(self, weight_init)
        logger.debug(
            f"[LSTMClassifier] input={input_size} hidden={hidden_size} "
            f"layers={num_layers} classes={output_classes}"
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: ``(batch, seq_len, input_size)``
        Returns:
            Logits ``(batch, output_classes)``
        """
        # h_n: (num_layers, batch, hidden_size)
        _, (h_n, _) = self.lstm(x)
        last_hidden = h_n[-1]  # top-layer hidden state

        if self.norm is not None:
            last_hidden = self.norm(last_hidden)
        last_hidden = self.dropout(last_hidden)
        return self.classifier(last_hidden)


def _build_norm(normalization: str, size: int) -> Optional[nn.Module]:
    key = normalization.lower()
    if key == "layer":
        return nn.LayerNorm(size)
    elif key == "batch":
        return nn.BatchNorm1d(size)
    return None
