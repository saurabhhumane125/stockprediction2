"""
ml_engine/models/weight_init.py
─────────────────────────────────────────────────────────────────────────────
Production weight-initialisation utilities for PyTorch modules.

Supported strategies (configuration-driven via ``ModelConfig.WEIGHT_INIT``):
  • ``xavier_uniform``   – Glorot uniform (default, good for tanh / sigmoid)
  • ``xavier_normal``    – Glorot normal
  • ``kaiming_uniform``  – He uniform (recommended for ReLU activations)
  • ``kaiming_normal``   – He normal
  • ``orthogonal``       – Orthogonal (often best for recurrent weights)
  • ``default``          – Leave PyTorch defaults untouched
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Callable

import torch.nn as nn

logger = logging.getLogger(__name__)

# Registry mapping config strings → init functions
_INIT_REGISTRY: dict[str, Callable[[nn.Module], None]] = {}


def _register(name: str) -> Callable:
    """Decorator that registers an init function under a config-string key."""
    def decorator(fn: Callable) -> Callable:
        _INIT_REGISTRY[name] = fn
        return fn
    return decorator


# ── Concrete strategies ────────────────────────────────────────────────────

@_register("xavier_uniform")
def _xavier_uniform(module: nn.Module) -> None:
    if isinstance(module, (nn.Linear, nn.GRU, nn.LSTM)):
        for name, param in module.named_parameters():
            if "weight" in name and param.dim() >= 2:
                nn.init.xavier_uniform_(param)
            elif "bias" in name:
                nn.init.zeros_(param)


@_register("xavier_normal")
def _xavier_normal(module: nn.Module) -> None:
    if isinstance(module, (nn.Linear, nn.GRU, nn.LSTM)):
        for name, param in module.named_parameters():
            if "weight" in name and param.dim() >= 2:
                nn.init.xavier_normal_(param)
            elif "bias" in name:
                nn.init.zeros_(param)


@_register("kaiming_uniform")
def _kaiming_uniform(module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.kaiming_uniform_(module.weight, nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, (nn.GRU, nn.LSTM)):
        for name, param in module.named_parameters():
            if "weight" in name and param.dim() >= 2:
                nn.init.kaiming_uniform_(param, nonlinearity="relu")
            elif "bias" in name:
                nn.init.zeros_(param)


@_register("kaiming_normal")
def _kaiming_normal(module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.kaiming_normal_(module.weight, nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, (nn.GRU, nn.LSTM)):
        for name, param in module.named_parameters():
            if "weight" in name and param.dim() >= 2:
                nn.init.kaiming_normal_(param, nonlinearity="relu")
            elif "bias" in name:
                nn.init.zeros_(param)


@_register("orthogonal")
def _orthogonal(module: nn.Module) -> None:
    if isinstance(module, (nn.GRU, nn.LSTM)):
        for name, param in module.named_parameters():
            if "weight_hh" in name and param.dim() >= 2:
                nn.init.orthogonal_(param)
            elif "weight_ih" in name and param.dim() >= 2:
                nn.init.xavier_uniform_(param)
            elif "bias" in name:
                nn.init.zeros_(param)
    elif isinstance(module, nn.Linear):
        if module.weight.dim() >= 2:
            nn.init.orthogonal_(module.weight)
        if module.bias is not None:
            nn.init.zeros_(module.bias)


@_register("default")
def _default(_module: nn.Module) -> None:
    """Leave PyTorch default initialisation unchanged."""


# ── Public API ────────────────────────────────────────────────────────────

def apply_weight_init(model: nn.Module, strategy: str) -> None:
    """
    Apply a named weight-initialisation strategy to every sub-module of *model*.

    Args:
        model:    Root ``torch.nn.Module``.
        strategy: One of the supported strategy names
                  (``"xavier_uniform"``, ``"kaiming_normal"``, etc.).

    Raises:
        ValueError: If *strategy* is not in the registered registry.
    """
    strategy = strategy.lower().replace(" ", "_")
    if strategy not in _INIT_REGISTRY:
        raise ValueError(
            f"Unknown weight init strategy '{strategy}'. "
            f"Supported: {sorted(_INIT_REGISTRY.keys())}"
        )
    init_fn = _INIT_REGISTRY[strategy]
    model.apply(init_fn)
    logger.debug(f"[WeightInit] Applied '{strategy}' to {type(model).__name__}.")
