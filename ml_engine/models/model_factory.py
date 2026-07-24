"""
ml_engine/models/model_factory.py
─────────────────────────────────────────────────────────────────────────────
Production Model Factory — single source of truth for model instantiation.

Design
  • Self-registering pattern: each architecture class registers itself under
    a string key via ``@ModelFactory.register(...)``.
  • No if-else chains — new architectures are added purely by decoration.
  • Configuration-driven: all hyperparameters come from ``ModelConfig`` or
    an explicit override dict.
  • Returns a ``BaseTimeSeriesClassifier`` regardless of concrete type,
    making the ``TrainingOrchestrator`` fully architecture-agnostic.

Usage::

    # Using global config default
    model = ModelFactory.create(input_size=23)

    # Explicit architecture + overrides
    model = ModelFactory.create(
        input_size=23,
        model_type="Transformer",
        overrides={"num_heads": 8, "num_layers": 4},
    )

    # Factory callable for TrainingOrchestrator
    factory_fn = ModelFactory.make_builder(model_type="GRU")
    model = factory_fn(input_shape=(48, 23))
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Tuple, Type

from ml_engine.config.model_config import model_config
from ml_engine.config.training_config import TrainingConfig
from ml_engine.core.types import TaskType
from ml_engine.models.base_model import BaseTimeSeriesClassifier

logger = logging.getLogger(__name__)


class ModelFactory:
    """
    Registry-based factory for production time-series classification models.

    Architectures register themselves via the ``@ModelFactory.register`` class
    decorator so no factory source code needs to change when adding new models.
    """

    _registry: Dict[str, Type[BaseTimeSeriesClassifier]] = {}

    # ── Registry ──────────────────────────────────────────────────────────────

    @classmethod
    def register(cls, key: str) -> Callable:
        """
        Class decorator that registers a model class under *key*.

        Args:
            key: Case-insensitive string identifier
                 (e.g. ``"GRU"``, ``"Transformer"``).
        """
        def decorator(model_cls: Type[BaseTimeSeriesClassifier]) -> Type[BaseTimeSeriesClassifier]:
            normalized = key.lower()
            if normalized in cls._registry:
                logger.warning(
                    f"[ModelFactory] Overwriting registered model key '{key}'."
                )
            cls._registry[normalized] = model_cls
            logger.debug(f"[ModelFactory] Registered '{key}' → {model_cls.__name__}")
            return model_cls
        return decorator

    @classmethod
    def list_models(cls) -> list[str]:
        """Return sorted list of registered model keys."""
        return sorted(cls._registry.keys())

    # ── Creation ──────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        input_size: int,
        model_type: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> BaseTimeSeriesClassifier:
        """
        Instantiate and return a model.

        Args:
            input_size:  Number of features per time step  (sequence dim F).
            model_type:  Architecture key. Defaults to ``ModelConfig.MODEL_TYPE``.
            overrides:   Dict of constructor kwargs that override ``ModelConfig``
                         values (e.g. ``{"hidden_size": 128, "num_layers": 3}``).

        Returns:
            A fully initialised ``BaseTimeSeriesClassifier`` subclass instance.

        Raises:
            KeyError: If *model_type* is not registered.
        """
        overrides = overrides or {}
        key = (model_type or model_config.MODEL_TYPE).lower()

        if key not in cls._registry:
            raise KeyError(
                f"Model type '{model_type}' is not registered. "
                f"Available: {cls.list_models()}"
            )

        model_cls = cls._registry[key]
        kwargs = cls._build_kwargs(key, input_size, overrides)
        model = model_cls(**kwargs)

        logger.info(
            f"[ModelFactory] Created {model_cls.__name__} | "
            f"input={input_size} | params={model.parameter_count()['total']:,}"
        )
        return model

    @classmethod
    def make_builder(
        cls,
        model_type: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Callable[[Tuple[int, int]], BaseTimeSeriesClassifier]:
        """
        Return a builder callable compatible with ``TrainingOrchestrator``.

        The returned callable accepts ``input_shape: Tuple[seq_len, n_features]``
        and returns an initialised model — matching the orchestrator's contract::

            model_builder: Callable[[Tuple[int, int]], nn.Module]

        Args:
            model_type: Architecture key (defaults to ``ModelConfig.MODEL_TYPE``).
            overrides:  Hyperparameter overrides passed through to ``create()``.
        """
        def builder(input_shape: Tuple[int, int]) -> BaseTimeSeriesClassifier:
            _seq_len, n_features = input_shape
            return cls.create(
                input_size=n_features,
                model_type=model_type,
                overrides=overrides,
            )
        return builder

    # ── Internal ──────────────────────────────────────────────────────────────

    @classmethod
    def _build_kwargs(
        cls,
        key: str,
        input_size: int,
        overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Merge ModelConfig defaults with caller-supplied overrides.

        The mapping from config fields to constructor parameters is defined
        here once so that concrete model classes need no config knowledge.
        """
        cfg = model_config

        # Infer output dimension dynamically from TaskType
        target_cfg = TrainingConfig.target
        task_type = target_cfg.task_type
        
        if task_type == TaskType.BINARY_CLASSIFICATION:
            inferred_output_classes = 1
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
            # Assumes 3-class (BUY/HOLD/SELL) natively, but configurable
            inferred_output_classes = len(target_cfg.thresholds) + 1 if target_cfg.thresholds else 3
        elif task_type == TaskType.REGRESSION:
            inferred_output_classes = 1
        elif task_type == TaskType.MULTI_OUTPUT_REGRESSION:
            inferred_output_classes = len(target_cfg.horizons)
        else:
            inferred_output_classes = 1

        # Common kwargs shared by all recurrent models
        common = {
            "input_size": input_size,
            "hidden_size": cfg.HIDDEN_SIZE,
            "num_layers": cfg.NUM_LAYERS,
            "output_classes": inferred_output_classes,
            "dropout": cfg.DROPOUT,
            "normalization": cfg.NORMALIZATION,
            "weight_init": cfg.WEIGHT_INIT,
        }

        if key == "transformer":
            kwargs = {
                "input_size": input_size,
                "hidden_size": cfg.HIDDEN_SIZE,
                "num_heads": cfg.TRANSFORMER_HEADS,
                "ff_dim": cfg.TRANSFORMER_FF_DIM,
                "num_layers": cfg.TRANSFORMER_DEPTH,
                "output_classes": inferred_output_classes,
                "dropout": cfg.DROPOUT,
                "weight_init": cfg.WEIGHT_INIT,
            }
        else:
            kwargs = dict(common)

        # Apply caller overrides last — they always win
        kwargs.update(overrides)
        return kwargs


# ── Auto-register all built-in architectures ─────────────────────────────
# Imports here are intentionally deferred to the bottom of the file to avoid
# circular imports: each model file imports base_model but not model_factory.

def _register_builtin_models() -> None:
    from ml_engine.models.gru.gru_classifier import GRUClassifier
    from ml_engine.models.bigru.bigru_classifier import BiGRUClassifier
    from ml_engine.models.lstm.lstm_classifier import LSTMClassifier
    from ml_engine.models.transformer.transformer_classifier import TransformerClassifier

    ModelFactory._registry["gru"] = GRUClassifier
    ModelFactory._registry["bigru"] = BiGRUClassifier
    ModelFactory._registry["lstm"] = LSTMClassifier
    ModelFactory._registry["transformer"] = TransformerClassifier

    logger.debug(f"[ModelFactory] Built-in models registered: {ModelFactory.list_models()}")


_register_builtin_models()
