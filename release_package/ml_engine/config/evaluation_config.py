from typing import Dict, Any, List


class EvaluationConfig:
    """
    Unified configuration for model evaluation, visualisation, and production gating.

    Existing fields (``DECISION_THRESHOLD``, ``PLOT_DPI``, ``PLOT_STYLE``,
    ``COLOR_PALETTE``, ``NUM_CALIBRATION_BINS``) are preserved for backward
    compatibility with the legacy Keras ``ProductionEvaluator``.
    """

    # ── Classification threshold ─────────────────────────────────────────────
    DECISION_THRESHOLD: float = 0.5

    # ── Plotting ─────────────────────────────────────────────────────────────
    PLOT_DPI: int = 150           # reduced from 300 for fast CI; override for reports
    PLOT_STYLE: str = "seaborn-v0_8-whitegrid"
    COLOR_PALETTE: str = "viridis"

    # ── Calibration ──────────────────────────────────────────────────────────
    NUM_CALIBRATION_BINS: int = 10
    CALIBRATION_METHOD: str = "isotonic"       # "isotonic" | "platt" | "none"
    CALIBRATION_PERSIST_SEPARATELY: bool = True


    # ── Production Acceptance Thresholds ────────────────────────────────────
    # A model PASSES only when ALL thresholds are satisfied simultaneously.
    MIN_ROC_AUC: float = 0.60          # minimum acceptable ROC-AUC
    MIN_F1: float = 0.50               # minimum acceptable F1 (macro)
    MIN_ACCURACY: float = 0.55         # minimum acceptable accuracy
    MIN_PR_AUC: float = 0.45           # minimum acceptable PR-AUC
    MAX_LOG_LOSS: float = 0.70         # maximum acceptable log-loss
    MAX_BRIER_SCORE: float = 0.25      # maximum acceptable Brier score
    MAX_ECE: float = 0.15              # maximum Expected Calibration Error

    # ── Walk-forward Validation ──────────────────────────────────────────────
    WALK_FORWARD_WINDOW: int = 50      # number of samples per rolling fold
    WALK_FORWARD_STEP: int = 10        # step size between folds
    WALK_FORWARD_MIN_SAMPLES: int = 20 # minimum samples required in a fold

    # ── Comparator ranking ───────────────────────────────────────────────────
    # Primary metric used to rank models during comparison
    COMPARATOR_PRIMARY_METRIC: str = "roc_auc"  # higher is better
    # Metrics included in the comparison table
    COMPARATOR_METRICS: List[str] = [
        "roc_auc", "f1", "accuracy", "pr_auc", "log_loss", "mcc", "brier_score"
    ]

    def to_dict(self) -> Dict[str, Any]:
        """Serialise all config fields to a plain dict (JSON-safe)."""
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }


evaluation_config = EvaluationConfig()
