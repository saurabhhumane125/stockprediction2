from typing import Dict, Any, Literal


class ModelConfig:
    """
    Unified configuration for all production model architectures.

    All model hyperparameters are defined here as a single source of truth.
    The existing ``GRU_HIDDEN_DIM`` / ``BIGRU_*`` fields are preserved for
    backward compatibility with the legacy Keras GRU builder.
    """

    # ── Architecture selection ───────────────────────────────────────────────
    # Supported: "GRU" | "BiGRU" | "LSTM" | "Transformer"
    MODEL_TYPE: str = "GRU"

    # ── Shared / common settings ─────────────────────────────────────────────
    HIDDEN_SIZE: int = 64          # hidden dimension for recurrent layers
    NUM_LAYERS: int = 2            # stacked recurrent or encoder depth
    DROPOUT: float = 0.2           # dropout applied after each recurrent block
    BIDIRECTIONAL: bool = False    # used by BiGRU; ignored by others
    ACTIVATION: str = "relu"       # activation for classification head: "relu" | "gelu"
    NORMALIZATION: str = "layer"   # "batch" | "layer" | "none"
    DEVICE: str = "cpu"            # "cpu" | "cuda" | "mps"

    # ── Weight initialisation ────────────────────────────────────────────────
    # Supported: "xavier_uniform" | "xavier_normal" | "kaiming_uniform"
    #            | "kaiming_normal" | "orthogonal" | "default"
    WEIGHT_INIT: str = "xavier_uniform"

    # ── Transformer-specific ─────────────────────────────────────────────────
    TRANSFORMER_HEADS: int = 4     # number of attention heads (must divide HIDDEN_SIZE)
    TRANSFORMER_FF_DIM: int = 256  # feed-forward inner dimension
    TRANSFORMER_DEPTH: int = 2     # number of encoder blocks

    # ── Legacy fields (kept for Keras GRU builder backward compatibility) ────
    GRU_HIDDEN_DIM: int = 64
    GRU_LAYERS: int = 2
    GRU_DROPOUT: float = 0.2

    BIGRU_HIDDEN_DIM: int = 128
    BIGRU_LAYERS: int = 2
    BIGRU_DROPOUT: float = 0.3

    def to_dict(self) -> Dict[str, Any]:
        """Serialise all config fields to a plain dict (JSON-safe)."""
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }


model_config = ModelConfig()
