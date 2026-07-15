"""
ml_engine/optimization/callbacks.py
─────────────────────────────────────────────────────────────────────────────
Optuna pruners and tracking callbacks.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
from typing import Optional
import optuna

logger = logging.getLogger(__name__)


def build_pruner(pruner_type: str) -> Optional[optuna.pruners.BasePruner]:
    """
    Instantiate an Optuna pruner by name.
    """
    ptype = pruner_type.lower().replace(" ", "")
    
    if ptype == "median":
        return optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=10)
    elif ptype == "successivehalving":
        return optuna.pruners.SuccessiveHalvingPruner()
    elif ptype == "hyperband":
        return optuna.pruners.HyperbandPruner(min_resource=1, max_resource=100)
    elif ptype in ("none", ""):
        return optuna.pruners.NopPruner()
    else:
        logger.warning(f"[Optimization] Unknown pruner type '{pruner_type}'. Defaulting to None.")
        return optuna.pruners.NopPruner()


class LoggingCallback:
    """
    Logs trial results as they complete.
    """
    def __call__(self, study: optuna.Study, trial: optuna.trial.FrozenTrial) -> None:
        if trial.state == optuna.trial.TrialState.COMPLETE:
            logger.info(
                f"[Optimization] Trial {trial.number} finished with value: {trial.value:.4f} "
                f"and parameters: {trial.params}."
            )
        elif trial.state == optuna.trial.TrialState.PRUNED:
            logger.info(f"[Optimization] Trial {trial.number} pruned.")
        elif trial.state == optuna.trial.TrialState.FAIL:
            logger.warning(f"[Optimization] Trial {trial.number} failed.")
