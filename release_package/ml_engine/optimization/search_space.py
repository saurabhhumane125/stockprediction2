"""
ml_engine/optimization/search_space.py
─────────────────────────────────────────────────────────────────────────────
Configuration-driven search space definition.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import optuna


@dataclass
class SearchSpaceConfig:
    """Configurable boundaries for hyperparameter tuning."""
    
    # Architecture
    model_types: List[str] = ("GRU", "BiGRU", "LSTM", "Transformer")
    hidden_size_range: Tuple[int, int] = (32, 256)
    hidden_size_step: int = 32
    num_layers_range: Tuple[int, int] = (1, 4)
    dropout_range: Tuple[float, float] = (0.0, 0.5)
    
    # Training Loop
    learning_rate_range: Tuple[float, float] = (1e-5, 1e-2)
    batch_size_choices: List[int] = (32, 64, 128)
    optimizer_choices: List[str] = ("adam", "adamw", "sgd")
    scheduler_choices: List[str] = ("ReduceLROnPlateau", "CosineAnnealing", "None")
    
    # Regularization
    weight_decay_range: Tuple[float, float] = (1e-6, 1e-2)
    gradient_clip_range: Tuple[float, float] = (0.1, 5.0)
    
    # Dataset
    sequence_length_choices: List[int] = (24, 48, 96)
    
    # Model Specific (e.g. classification head activation)
    activation_choices: List[str] = ("relu", "gelu")


# Default search space configuration
default_search_space = SearchSpaceConfig()


def suggest_hyperparameters(trial: optuna.Trial, config: SearchSpaceConfig = default_search_space) -> Dict[str, Any]:
    """
    Sample a complete set of hyperparameters for a trial.
    """
    params = {}
    
    # Architecture
    params["MODEL_TYPE"] = trial.suggest_categorical("MODEL_TYPE", list(config.model_types))
    params["HIDDEN_SIZE"] = trial.suggest_int(
        "HIDDEN_SIZE", 
        config.hidden_size_range[0], 
        config.hidden_size_range[1], 
        step=config.hidden_size_step
    )
    params["NUM_LAYERS"] = trial.suggest_int("NUM_LAYERS", config.num_layers_range[0], config.num_layers_range[1])
    params["DROPOUT"] = trial.suggest_float("DROPOUT", config.dropout_range[0], config.dropout_range[1])
    params["ACTIVATION"] = trial.suggest_categorical("ACTIVATION", list(config.activation_choices))
    
    # Training
    params["LEARNING_RATE"] = trial.suggest_float("LEARNING_RATE", config.learning_rate_range[0], config.learning_rate_range[1], log=True)
    params["BATCH_SIZE"] = trial.suggest_categorical("BATCH_SIZE", list(config.batch_size_choices))
    params["OPTIMIZER"] = trial.suggest_categorical("OPTIMIZER", list(config.optimizer_choices))
    params["LR_SCHEDULER"] = trial.suggest_categorical("LR_SCHEDULER", list(config.scheduler_choices))
    
    # Regularization
    params["WEIGHT_DECAY"] = trial.suggest_float("WEIGHT_DECAY", config.weight_decay_range[0], config.weight_decay_range[1], log=True)
    params["GRADIENT_CLIP_NORM"] = trial.suggest_float("GRADIENT_CLIP_NORM", config.gradient_clip_range[0], config.gradient_clip_range[1])
    
    # Dataset
    params["SEQUENCE_LENGTH"] = trial.suggest_categorical("SEQUENCE_LENGTH", list(config.sequence_length_choices))
    
    # Additional Transformer-specific settings if chosen
    if params["MODEL_TYPE"] == "Transformer":
        # Ensure heads evenly divide hidden size. Simplest way: suggest heads from common divisors
        heads = trial.suggest_categorical("TRANSFORMER_HEADS", [2, 4, 8])
        # If the generated hidden size isn't divisible by heads, we adjust it dynamically.
        if params["HIDDEN_SIZE"] % heads != 0:
            params["HIDDEN_SIZE"] = (params["HIDDEN_SIZE"] // heads) * heads
            if params["HIDDEN_SIZE"] == 0:
                params["HIDDEN_SIZE"] = heads
        params["TRANSFORMER_HEADS"] = heads
        params["TRANSFORMER_FF_DIM"] = trial.suggest_int("TRANSFORMER_FF_DIM", 64, 512, step=64)
        params["TRANSFORMER_DEPTH"] = params["NUM_LAYERS"]

    return params
