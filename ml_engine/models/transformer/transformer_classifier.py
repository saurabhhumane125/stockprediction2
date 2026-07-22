"""
ml_engine/models/transformer/transformer_classifier.py
─────────────────────────────────────────────────────────────────────────────
Production PyTorch Transformer Encoder classifier for time-series.

Architecture
  Input  (batch, seq, features)
    └─ Linear projection → (batch, seq, hidden_size)
        └─ + Sinusoidal Positional Encoding
            └─ N × TransformerEncoderLayer (MultiheadAttention + FF + LN)
                └─ Global Average Pool over sequence  (batch, hidden_size)
                    └─ Dropout
                        └─ Linear → logits  (batch, output_classes)

Design decisions:
  • Sinusoidal positional encoding (no learned embeddings) → length-agnostic
  • Global average pooling → richer signal than CLS-token for short sequences
  • ``batch_first=True`` throughout for consistency with other models
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import math
from typing import Optional

import torch
import torch.nn as nn

from ml_engine.models.base_model import BaseTimeSeriesClassifier
from ml_engine.models.weight_init import apply_weight_init

logger = logging.getLogger(__name__)


# ── Positional Encoding ───────────────────────────────────────────────────

class SinusoidalPositionalEncoding(nn.Module):
    """
    Adds fixed sinusoidal positional encodings to the token embeddings.

    The encoding is computed once and registered as a buffer so it is
    device-agnostic and not updated during training.

    Args:
        hidden_size: Dimensionality of the embeddings.
        max_len:     Maximum sequence length supported.
        dropout:     Dropout applied after adding the encodings.
    """

    def __init__(self, hidden_size: int, max_len: int = 512, dropout: float = 0.1) -> None:
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, hidden_size)          # (max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(
            torch.arange(0, hidden_size, 2).float() * (-math.log(10000.0) / hidden_size)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)                            # (1, max_len, d_model)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: ``(batch, seq_len, hidden_size)``
        Returns:
            ``(batch, seq_len, hidden_size)`` with positional info added.
        """
        x = x + self.pe[:, : x.size(1), :]
        return self.dropout(x)


# ── Transformer Encoder Classifier ───────────────────────────────────────

class TransformerClassifier(BaseTimeSeriesClassifier):
    """
    Transformer Encoder-based classifier for financial time-series.

    Args:
        input_size:     Number of input features per time step.
        hidden_size:    Projection dimension (``d_model``).
                        Must be divisible by *num_heads*.
        num_heads:      Number of multi-head attention heads.
        ff_dim:         Feed-forward inner dimension inside each encoder block.
        num_layers:     Number of ``TransformerEncoderLayer`` blocks.
        output_classes: Number of output logit classes.
        dropout:        Dropout probability used in attention, FF, and head.
        weight_init:    Weight initialisation strategy.
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_heads: int = 4,
        ff_dim: int = 256,
        num_layers: int = 2,
        output_classes: int = 2,
        dropout: float = 0.1,
        weight_init: str = "xavier_uniform",
    ) -> None:
        if hidden_size % num_heads != 0:
            raise ValueError(
                f"hidden_size ({hidden_size}) must be divisible by num_heads ({num_heads})."
            )
        super().__init__(input_size=input_size, output_classes=output_classes)

        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.num_layers = num_layers

        # Project raw features → model dimension
        self.input_projection = nn.Linear(input_size, hidden_size)

        self.positional_encoding = SinusoidalPositionalEncoding(
            hidden_size=hidden_size, dropout=dropout
        )

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=num_heads,
            dim_feedforward=ff_dim,
            dropout=dropout,
            activation="relu",
            batch_first=True,
            norm_first=True,   # Pre-LN (more stable training)
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.dropout = nn.Dropout(p=dropout)
        self.classifier = nn.Linear(hidden_size, output_classes)

        apply_weight_init(self, weight_init)
        logger.debug(
            f"[TransformerClassifier] input={input_size} hidden={hidden_size} "
            f"heads={num_heads} layers={num_layers} ff={ff_dim} classes={output_classes}"
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: ``(batch, seq_len, input_size)``
        Returns:
            Logits ``(batch, output_classes)``
        """
        # Project and add positional encodings
        x = self.input_projection(x)           # (batch, seq, hidden_size)
        x = self.positional_encoding(x)

        # Encode
        x = self.encoder(x)                    # (batch, seq, hidden_size)

        # Global average pooling over the sequence dimension
        x = x.mean(dim=1)                      # (batch, hidden_size)
        x = self.dropout(x)
        return self.classifier(x)
