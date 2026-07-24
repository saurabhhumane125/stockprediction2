from typing import Dict, Any, List, Literal
from ml_engine.core.types import TaskType
class TrainingConfig:
    """
    Unified configuration for dataset building, splitting, and training loops.
    All fields are used by the production TrainingOrchestrator.
    Existing fields are preserved for backward compatibility with the legacy KerasTrainer.
    """

    # ── Dataset ─────────────────────────────────────────────────────────────────
    SEQUENCE_LENGTH: int = 48
    
    # ── Target Configuration ────────────────────────────────────────────────────
    class target:
        task_type: TaskType = TaskType.REGRESSION
        target_type: str = "RETURN" # LOG_RETURN, RETURN, PRICE, CLASS
        horizons: List[int] = [5]
        primary_horizon: int = 5
        thresholds: List[float] = [0.0]

    # Legacy attributes for backward compatibility
    FORECAST_HORIZON: int = 5
    RETURN_THRESHOLD_BPS: float = 0.0

    # Temporal splitting (inclusive end dates)
    TRAIN_END_DATE: str = "2021-12-31"
    VAL_END_DATE: str = "2023-06-30"

    # ── Training Loop ────────────────────────────────────────────────────────────
    BATCH_SIZE: int = 64
    EPOCHS: int = 100
    LEARNING_RATE: float = 1e-3

    # ── Early Stopping ───────────────────────────────────────────────────────────
    EARLY_STOPPING_PATIENCE: int = 15
    EARLY_STOPPING_MONITOR: str = "val_loss"   # metric key watched by EarlyStopper

    # ── LR Scheduler ─────────────────────────────────────────────────────────────
    # Supported: "ReduceLROnPlateau" | "CosineAnnealing" | "OneCycleLR" | "None"
    LR_SCHEDULER: str = "ReduceLROnPlateau"
    LR_SCHEDULER_PATIENCE: int = 5             # used by ReduceLROnPlateau
    LR_SCHEDULER_FACTOR: float = 0.5           # used by ReduceLROnPlateau
    LR_SCHEDULER_MIN_LR: float = 1e-6          # used by ReduceLROnPlateau
    LR_SCHEDULER_T_MAX: int = 50               # used by CosineAnnealing (T_max in epochs)
    LR_SCHEDULER_MAX_LR: float = 1e-2          # used by OneCycleLR

    # ── Regularisation ───────────────────────────────────────────────────────────
    DROPOUT: float = 0.2
    GRADIENT_CLIP_NORM: float = 1.0            # max-norm gradient clipping (0 = disabled)

    # ── Model Architecture ───────────────────────────────────────────────────────
    OPTIMIZER: str = "adam"                    # "adam" | "adamw" | "sgd"
    HIDDEN_SIZE: int = 64

    # ── Precision & Hardware ─────────────────────────────────────────────────────
    MIXED_PRECISION: bool = False              # enable torch.cuda.amp if True
    DEVICE: str = "auto"                       # "auto" | "cpu" | "cuda" | "mps"
    CUDNN_BENCHMARK: bool = True               # optimise cudnn for fixed input sizes

    # ── Reproducibility ──────────────────────────────────────────────────────────
    SEED: int = 42

    # ── DataLoader ───────────────────────────────────────────────────────────────
    NUM_WORKERS: int = 0                       # 0 = main-process only (safe on Windows)
    PIN_MEMORY: bool = False                   # True only with CUDA device

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }


training_config = TrainingConfig()
