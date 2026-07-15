"""
ml_engine/training/checkpoint_manager.py
─────────────────────────────────────────────────────────────────────────────
Production CheckpointManager for PyTorch training sessions.

Responsibilities
  • Save the best model based on a monitored metric (lower = better for loss,
    higher = better for accuracy / F1 / AUC).
  • Save the latest checkpoint after every epoch so training can be resumed
    exactly where it stopped.
  • Implement early stopping with configurable patience.
  • Restore best weights into the model in-place once training has converged
    or been interrupted.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manages model checkpoints and early stopping for a PyTorch training run.

    Args:
        checkpoint_dir: Directory where checkpoint files will be written.
        monitor:        Metric key to watch (e.g. ``"val_loss"``).
        patience:       Number of epochs without improvement before stopping.
        mode:           ``"min"`` (loss-like) or ``"max"`` (accuracy-like).
        verbose:        Whether to emit INFO-level log lines on improvement.
    """

    BEST_FILE = "best_model.pt"
    LATEST_FILE = "latest_checkpoint.pt"
    META_FILE = "checkpoint_meta.json"

    def __init__(
        self,
        checkpoint_dir: str,
        monitor: str = "val_loss",
        patience: int = 15,
        mode: str = "min",
        verbose: bool = True,
    ) -> None:
        self.checkpoint_dir = checkpoint_dir
        self.monitor = monitor
        self.patience = patience
        self.mode = mode
        self.verbose = verbose

        os.makedirs(self.checkpoint_dir, exist_ok=True)

        self._best_value: float = float("inf") if mode == "min" else float("-inf")
        self._epochs_without_improvement: int = 0
        self._best_epoch: int = 0
        self._stopped_early: bool = False

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def should_stop(self) -> bool:
        """Returns ``True`` once patience is exhausted."""
        return self._stopped_early

    @property
    def best_epoch(self) -> int:
        return self._best_epoch

    @property
    def best_value(self) -> float:
        return self._best_value

    def step(self, epoch: int, metrics: Dict[str, float], model: Any, optimizer: Any, scheduler: Any) -> bool:
        """
        Called at the end of every epoch. Saves the latest checkpoint and,
        if the monitored metric improved, also saves the best checkpoint.

        Args:
            epoch:     Current epoch (0-indexed).
            metrics:   Dictionary containing at least the monitored metric key.
            model:     ``torch.nn.Module`` to checkpoint.
            optimizer: Optimizer whose state should be saved for resuming.
            scheduler: LR scheduler whose state should be saved (can be ``None``).

        Returns:
            ``True`` if training should stop (patience exhausted), else ``False``.
        """
        import torch

        current = metrics.get(self.monitor)
        if current is None:
            logger.warning(
                f"[CheckpointManager] Metric '{self.monitor}' not found in metrics dict. "
                f"Available keys: {list(metrics.keys())}. Skipping checkpoint step."
            )
            return False

        improved = (
            (self.mode == "min" and current < self._best_value)
            or (self.mode == "max" and current > self._best_value)
        )

        # Always save the latest checkpoint so training can be resumed
        self._save_latest(epoch, metrics, model, optimizer, scheduler)

        if improved:
            if self.verbose:
                logger.info(
                    f"[CheckpointManager] Epoch {epoch}: '{self.monitor}' improved "
                    f"{self._best_value:.6f} → {current:.6f}. Saving best model."
                )
            self._best_value = current
            self._best_epoch = epoch
            self._epochs_without_improvement = 0
            self._save_best(epoch, metrics, model)
        else:
            self._epochs_without_improvement += 1
            if self.verbose:
                logger.info(
                    f"[CheckpointManager] Epoch {epoch}: no improvement in '{self.monitor}' "
                    f"({self._epochs_without_improvement}/{self.patience})."
                )
            if self._epochs_without_improvement >= self.patience:
                logger.info(
                    f"[CheckpointManager] Early stopping triggered after epoch {epoch}. "
                    f"Best value: {self._best_value:.6f} at epoch {self._best_epoch}."
                )
                self._stopped_early = True

        self._save_meta(epoch, metrics)
        return self._stopped_early

    def restore_best(self, model: Any) -> None:
        """
        Load the best weights into ``model`` in-place.

        Args:
            model: ``torch.nn.Module`` instance.
        """
        import torch

        best_path = os.path.join(self.checkpoint_dir, self.BEST_FILE)
        if not os.path.exists(best_path):
            logger.warning("[CheckpointManager] No best checkpoint found to restore.")
            return

        state = torch.load(best_path, map_location="cpu")
        model.load_state_dict(state["model_state_dict"])
        logger.info(
            f"[CheckpointManager] Restored best weights from epoch {state.get('epoch', '?')}."
        )

    def load_latest(self, model: Any, optimizer: Any, scheduler: Any) -> int:
        """
        Load the latest checkpoint into model/optimizer/scheduler in-place.

        Returns:
            The epoch number stored in the checkpoint so the training loop
            can resume from the correct position (returns 0 if no checkpoint).
        """
        import torch

        latest_path = os.path.join(self.checkpoint_dir, self.LATEST_FILE)
        if not os.path.exists(latest_path):
            logger.info("[CheckpointManager] No latest checkpoint found. Starting from scratch.")
            return 0

        state = torch.load(latest_path, map_location="cpu")
        model.load_state_dict(state["model_state_dict"])
        optimizer.load_state_dict(state["optimizer_state_dict"])
        if scheduler is not None and state.get("scheduler_state_dict") is not None:
            scheduler.load_state_dict(state["scheduler_state_dict"])

        # Restore internal state
        self._best_value = state.get("best_value", self._best_value)
        self._best_epoch = state.get("best_epoch", 0)
        self._epochs_without_improvement = state.get("epochs_without_improvement", 0)

        resume_epoch = state.get("epoch", 0) + 1
        logger.info(f"[CheckpointManager] Resumed from epoch {state.get('epoch')}. Next epoch: {resume_epoch}.")
        return resume_epoch

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _save_best(self, epoch: int, metrics: Dict[str, float], model: Any) -> None:
        import torch
        best_path = os.path.join(self.checkpoint_dir, self.BEST_FILE)
        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "metrics": metrics,
                "best_value": self._best_value,
            },
            best_path,
        )

    def _save_latest(
        self,
        epoch: int,
        metrics: Dict[str, float],
        model: Any,
        optimizer: Any,
        scheduler: Any,
    ) -> None:
        import torch
        latest_path = os.path.join(self.checkpoint_dir, self.LATEST_FILE)
        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "scheduler_state_dict": scheduler.state_dict() if scheduler is not None else None,
                "best_value": self._best_value,
                "best_epoch": self._best_epoch,
                "epochs_without_improvement": self._epochs_without_improvement,
                "metrics": metrics,
            },
            latest_path,
        )

    def _save_meta(self, epoch: int, metrics: Dict[str, float]) -> None:
        meta = {
            "last_epoch": epoch,
            "best_epoch": self._best_epoch,
            "best_value": self._best_value,
            "monitor": self.monitor,
            "mode": self.mode,
            "epochs_without_improvement": self._epochs_without_improvement,
            "stopped_early": self._stopped_early,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        meta_path = os.path.join(self.checkpoint_dir, self.META_FILE)
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=4)
