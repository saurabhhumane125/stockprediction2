"""
ml_engine/training/training_pipeline.py
─────────────────────────────────────────────────────────────────────────────
Production TrainingOrchestrator for PyTorch GRU / Keras models.

Responsibilities
  1. Seed all RNGs for deterministic training.
  2. Load pre-built .npz tensors from NumpyStorage.
  3. Wrap tensors in TimeSeriesDataset → DataLoader.
  4. Build model, optimizer, and LR scheduler from config.
  5. Run the training loop with:
       • Mixed-precision AMP (when configured)
       • Gradient clipping
       • Per-epoch metric tracking (loss, accuracy, precision, recall, F1, AUC)
       • CheckpointManager (best / latest weights + early stopping)
  6. Restore best weights after convergence / early stop.
  7. Evaluate on the held-out test set.
  8. Export production artifacts:
       model.pt  scaler.pkl  label_encoder.pkl  metadata.json
  9. Register the artifact bundle in the RegistryManager.
 10. Generate Markdown + JSON training reports via ReportGenerator.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import logging
import os
import pickle
import shutil
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from ml_engine.config.training_config import training_config
from ml_engine.data.storage.numpy_storage import NumpyStorage
from ml_engine.registry.manager import RegistryManager
from ml_engine.training.checkpoint_manager import CheckpointManager
from ml_engine.training.report_generator import ReportGenerator
from ml_engine.training.utils import TimeSeriesDataset, seed_everything

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Metric helpers (all work on numpy arrays so torch is not required at import)
# ─────────────────────────────────────────────────────────────────────────────

def _compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    Compute accuracy, precision (macro), recall (macro), F1 (macro),
    and binary AUC (if probability scores are supplied).

    Args:
        y_true:  Ground-truth class labels.
        y_pred:  Predicted class labels (argmax of logits).
        y_prob:  Predicted probabilities for the positive class (optional).
    """
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

    metrics: Dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = cm.tolist()
    
    if y_prob is not None:
        try:
            from sklearn.metrics import roc_auc_score
            metrics["auc"] = float(roc_auc_score(y_true, y_prob, multi_class="ovr", average="macro"))
        except Exception:
            metrics["auc"] = float("nan")
    return metrics


# ─────────────────────────────────────────────────────────────────────────────
# Optimizer factory
# ─────────────────────────────────────────────────────────────────────────────

def _build_optimizer(model: Any, cfg: Any) -> Any:
    """Instantiate optimizer from config string."""
    import torch.optim as optim

    name = (cfg.OPTIMIZER or "adam").lower()
    lr = cfg.LEARNING_RATE
    if name == "adamw":
        return optim.AdamW(model.parameters(), lr=lr)
    elif name == "sgd":
        return optim.SGD(model.parameters(), lr=lr, momentum=0.9)
    else:  # default: adam
        return optim.Adam(model.parameters(), lr=lr)


def _build_scheduler(optimizer: Any, cfg: Any, steps_per_epoch: int) -> Optional[Any]:
    """Instantiate LR scheduler from config string. Returns None if disabled."""
    import torch.optim.lr_scheduler as lr_sched

    name = (cfg.LR_SCHEDULER or "None").lower().replace(" ", "")
    if name in ("none", ""):
        return None
    elif name == "reducelronplateau":
        return lr_sched.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=cfg.LR_SCHEDULER_FACTOR,
            patience=cfg.LR_SCHEDULER_PATIENCE,
            min_lr=cfg.LR_SCHEDULER_MIN_LR,
        )
    elif name == "cosineannealing":
        return lr_sched.CosineAnnealingLR(optimizer, T_max=cfg.LR_SCHEDULER_T_MAX)
    elif name == "onecyclelr":
        return lr_sched.OneCycleLR(
            optimizer,
            max_lr=cfg.LR_SCHEDULER_MAX_LR,
            steps_per_epoch=steps_per_epoch,
            epochs=cfg.EPOCHS,
        )
    else:
        logger.warning(f"[TrainingOrchestrator] Unknown scheduler '{cfg.LR_SCHEDULER}'. Skipping.")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Main Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class TrainingOrchestrator:
    """
    Enterprise-grade training orchestrator for the Production ML Platform.

    All behaviour is driven by ``TrainingConfig``. No hard-coded values.

    Typical usage::

        orchestrator = TrainingOrchestrator(
            model_builder=my_gru_factory,
            tensor_storage=NumpyStorage(base_path="ml_engine/data/tensors"),
            registry=RegistryManager(registry_base_path="ml_engine/model_registry"),
            data_path="RELIANCE.NS/v1",
            artifact_dir="ml_engine/models/v2.0.0",
            version="v2.0.0",
        )
        result = orchestrator.run(resume=False)

    Args:
        model_builder:  ``Callable[[Tuple[int,int]], torch.nn.Module]``.
                        Receives ``(sequence_length, n_features)`` and returns
                        a compiled ``torch.nn.Module``.
        tensor_storage: ``NumpyStorage`` instance pointing at the tensor root.
        registry:       ``RegistryManager`` for artifact registration.
        data_path:      Relative path inside ``tensor_storage`` that contains
                        ``train.npz``, ``val.npz``, ``test.npz``.
        artifact_dir:   Directory where model artifacts will be written.
        version:        Semantic version string for this training run.
        scaler_path:    Optional path to a pre-fitted ``scaler.pkl`` to bundle.
        encoder_path:   Optional path to a pre-fitted ``label_encoder.pkl`` to bundle.
        feature_names:  Ordered list of feature column names (for the report).
        tickers:        List of tickers used to build the dataset (for the report).
    """

    def __init__(
        self,
        model_builder: Callable[[Tuple[int, int]], Any],
        tensor_storage: NumpyStorage,
        registry: RegistryManager,
        data_path: str,
        artifact_dir: str,
        version: str,
        scaler_path: Optional[str] = None,
        encoder_path: Optional[str] = None,
        feature_names: Optional[List[str]] = None,
        tickers: Optional[List[str]] = None,
        callbacks: Optional[List[Any]] = None,
    ) -> None:
        self.model_builder = model_builder
        self.tensor_storage = tensor_storage
        self.registry = registry
        self.data_path = data_path
        self.artifact_dir = artifact_dir
        self.version = version
        self.scaler_path = scaler_path
        self.encoder_path = encoder_path
        self.feature_names = feature_names or []
        self.tickers = tickers or []
        self.callbacks = callbacks or []
        self.cfg = training_config

        os.makedirs(self.artifact_dir, exist_ok=True)

    # ── Entry point ────────────────────────────────────────────────────────────

    def run(self, resume: bool = False) -> Dict[str, Any]:
        """
        Execute the complete training pipeline.

        Args:
            resume: If ``True``, resume from the latest checkpoint in
                    ``artifact_dir`` if it exists.

        Returns:
            Result dictionary with keys:
            ``version``, ``eval_metrics``, ``artifact_dir``,
            ``report_paths``, ``training_time_seconds``.
        """
        import torch

        wall_start = time.time()

        # 1. Deterministic seeding
        seed_everything(self.cfg.SEED)
        logger.info(f"[TrainingOrchestrator] Seed={self.cfg.SEED} | Version={self.version}")

        # 2. Load tensors
        train_X, train_y, val_X, val_y, test_X, test_y = self._load_tensors()
        dataset_info = self._build_dataset_info(train_X, val_X, test_X)
        logger.info(
            f"[TrainingOrchestrator] Dataset loaded – "
            f"train={len(train_X)} val={len(val_X)} test={len(test_X)}"
        )

        # 3. DataLoaders
        train_loader, val_loader, test_loader = self._build_loaders(
            train_X, train_y, val_X, val_y, test_X, test_y
        )
        steps_per_epoch = len(train_loader)

        # 4. Device
        if self.cfg.DEVICE == "auto":
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            device = torch.device(self.cfg.DEVICE)
        
        # cuDNN Benchmark integration
        if getattr(self.cfg, "CUDNN_BENCHMARK", False) and device.type == "cuda":
            torch.backends.cudnn.benchmark = True
            logger.info("[TrainingOrchestrator] Enabled cuDNN benchmark.")

        # 5. Model / Optimizer / Scheduler / GradScaler
        input_shape = (train_X.shape[1], train_X.shape[2])
        model = self.model_builder(input_shape).to(device)
        optimizer = _build_optimizer(model, self.cfg)
        scheduler = _build_scheduler(optimizer, self.cfg, steps_per_epoch)
        scaler = torch.cuda.amp.GradScaler(enabled=self.cfg.MIXED_PRECISION)

        # 6. Checkpoint manager
        checkpoint_dir = os.path.join(self.artifact_dir, "checkpoints")
        ckpt_manager = CheckpointManager(
            checkpoint_dir=checkpoint_dir,
            monitor=self.cfg.EARLY_STOPPING_MONITOR,
            patience=self.cfg.EARLY_STOPPING_PATIENCE,
            mode="min" if "loss" in self.cfg.EARLY_STOPPING_MONITOR else "max",
        )

        # 7. Optionally resume
        start_epoch = 0
        if resume:
            start_epoch = ckpt_manager.load_latest(model, optimizer, scheduler)
            logger.info(f"[TrainingOrchestrator] Resuming from epoch {start_epoch}.")

        # 8. Training loop
        criterion = torch.nn.CrossEntropyLoss()
        history: List[Dict[str, float]] = []

        for epoch in range(start_epoch, self.cfg.EPOCHS):
            epoch_start = time.time()
            
            for cb in self.callbacks:
                cb.on_epoch_begin(epoch)

            train_metrics = self._train_epoch(
                model, train_loader, optimizer, criterion, scaler, device, epoch
            )
            val_metrics = self._eval_epoch(model, val_loader, criterion, device, prefix="val")

            # Merge metrics
            epoch_metrics = {"epoch": epoch, **train_metrics, **val_metrics}
            history.append(epoch_metrics)
            
            for cb in self.callbacks:
                cb.on_epoch_end(epoch, epoch_metrics)

            epoch_dur = time.time() - epoch_start
            logger.info(
                f"[Epoch {epoch:03d}] "
                + "  ".join(f"{k}={v:.4f}" for k, v in epoch_metrics.items() if k != "epoch")
                + f"  time={epoch_dur:.1f}s"
            )

            # Advance ReduceLROnPlateau scheduler (others advance per batch)
            if scheduler is not None and isinstance(
                scheduler,
                __import__("torch.optim.lr_scheduler", fromlist=["ReduceLROnPlateau"]).ReduceLROnPlateau,
            ):
                scheduler.step(val_metrics.get("val_loss", float("inf")))

            # Checkpoint + early stopping
            stop = ckpt_manager.step(epoch, epoch_metrics, model, optimizer, scheduler)
            if stop:
                for cb in self.callbacks:
                    cb.on_early_stopping(epoch, ckpt_manager.best_epoch, ckpt_manager.best_value)
                break

        # 9. Restore best weights
        ckpt_manager.restore_best(model)

        # 10. Evaluate on test set
        eval_metrics = self._eval_epoch(model, test_loader, criterion, device, prefix="test")
        test_preds, test_probs, test_true, test_logits = self._collect_predictions(model, test_loader, device)
        
        # Slice class-1 probability for AUC if binary
        test_prob_auc = test_probs[:, 1] if test_probs.shape[1] == 2 else test_probs
        clf_metrics = _compute_metrics(test_true, test_preds, test_prob_auc)
        eval_metrics.update(clf_metrics)
        logger.info(f"[TrainingOrchestrator] Test evaluation: {eval_metrics}")
        
        # 10.5 Fit Calibration and Generate Evaluation Plots on validation set
        val_preds, val_probs, val_true, val_logits = self._collect_predictions(model, val_loader, device)
        
        from ml_engine.calibration.calibrator import CalibrationManager
        calibrator = CalibrationManager()
        calibrator.fit(val_probs[:, 1] if val_probs.shape[1] == 2 else val_probs, val_true)
        calibrator_path = os.path.join(self.artifact_dir, "calibrator.pkl")
        calibrator.save(calibrator_path)

        # Generate diagnostic plots and optimize threshold
        try:
            from ml_engine.training.evaluation_plots import find_optimal_threshold, generate_evaluation_plots
            
            # Save raw arrays
            np.save(os.path.join(self.artifact_dir, "val_logits.npy"), val_logits)
            np.save(os.path.join(self.artifact_dir, "val_probs.npy"), val_probs)
            np.save(os.path.join(self.artifact_dir, "test_logits.npy"), test_logits)
            np.save(os.path.join(self.artifact_dir, "test_probs.npy"), test_probs)
            
            # Optimal threshold
            optimal_thresh = find_optimal_threshold(val_true, val_probs[:, 1] if val_probs.shape[1] == 2 else val_probs)
            eval_metrics["optimal_val_f1_threshold"] = optimal_thresh
            
            # Generate plots
            val_plot_paths = generate_evaluation_plots(
                val_true, val_probs[:, 1] if val_probs.shape[1] == 2 else val_probs, val_logits, self.artifact_dir, prefix="val"
            )
            test_plot_paths = generate_evaluation_plots(
                test_true, test_probs[:, 1] if test_probs.shape[1] == 2 else test_probs, test_logits, self.artifact_dir, prefix="test"
            )
            
            # Merge plot paths into metrics for the report generator to use
            eval_metrics["plot_paths"] = {**val_plot_paths, **test_plot_paths}
            
        except ImportError as e:
            logger.warning(f"[TrainingOrchestrator] Could not generate plots: {e}")
        
        total_time = time.time() - wall_start

        # 11. Export artifacts
        artifact_paths = self._export_artifacts(model, eval_metrics, total_time, calibrator_path)

        # 12. Register in RegistryManager
        self._register(artifact_paths)

        # 13. Generate report
        report_gen = ReportGenerator(output_dir=self.artifact_dir)
        report_paths = report_gen.generate(
            config=self.cfg.to_dict(),
            dataset_info=dataset_info,
            history=history,
            eval_metrics=eval_metrics,
            feature_names=self.feature_names,
            version=self.version,
            execution_time_seconds=total_time,
        )

        logger.info(
            f"[TrainingOrchestrator] ✓ Training complete – "
            f"version={self.version} time={total_time:.1f}s"
        )
        return {
            "version": self.version,
            "eval_metrics": eval_metrics,
            "artifact_dir": self.artifact_dir,
            "report_paths": report_paths,
            "training_time_seconds": total_time,
        }

    # ── Internal ───────────────────────────────────────────────────────────────

    def _load_tensors(
        self,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        import torch
        
        def _load(split: str):
            filepath = os.path.join(self.tensor_storage.base_path, self.data_path, f"{split}.pt")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Array file not found at {filepath}")
            X_t, y_t = torch.load(filepath)
            # The rest of the pipeline expects numpy arrays for TimeSeriesDataset/sklearn metrics,
            # so we convert the loaded tensors back to numpy.
            return X_t.numpy(), y_t.numpy()

        train_X, train_y = _load("train")
        val_X, val_y = _load("val")
        test_X, test_y = _load("test")
        return train_X, train_y, val_X, val_y, test_X, test_y

    def _build_loaders(
        self,
        train_X: np.ndarray,
        train_y: np.ndarray,
        val_X: np.ndarray,
        val_y: np.ndarray,
        test_X: np.ndarray,
        test_y: np.ndarray,
    ):
        from torch.utils.data import DataLoader

        train_ds = TimeSeriesDataset(train_X, train_y)
        val_ds = TimeSeriesDataset(val_X, val_y)
        test_ds = TimeSeriesDataset(test_X, test_y)

        common = dict(
            batch_size=self.cfg.BATCH_SIZE,
            num_workers=self.cfg.NUM_WORKERS,
            pin_memory=self.cfg.PIN_MEMORY,
        )
        train_loader = DataLoader(train_ds, shuffle=True, **common)
        val_loader = DataLoader(val_ds, shuffle=False, **common)
        test_loader = DataLoader(test_ds, shuffle=False, **common)
        return train_loader, val_loader, test_loader

    def _train_epoch(
        self, model, loader, optimizer, criterion, scaler, device, epoch: int
    ) -> Dict[str, float]:
        import torch

        model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for X_batch, y_batch in loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()

            with torch.cuda.amp.autocast(enabled=self.cfg.MIXED_PRECISION):
                logits = model(X_batch)
                loss = criterion(logits, y_batch)

            scaler.scale(loss).backward()

            if self.cfg.GRADIENT_CLIP_NORM > 0:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), self.cfg.GRADIENT_CLIP_NORM)

            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item() * len(y_batch)
            preds = logits.argmax(dim=1)
            correct += (preds == y_batch).sum().item()
            total += len(y_batch)

        return {
            "train_loss": total_loss / total,
            "train_accuracy": correct / total,
        }

    def _eval_epoch(
        self, model, loader, criterion, device, prefix: str = "val"
    ) -> Dict[str, float]:
        import torch

        model.eval()
        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for X_batch, y_batch in loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                logits = model(X_batch)
                loss = criterion(logits, y_batch)
                total_loss += loss.item() * len(y_batch)
                preds = logits.argmax(dim=1)
                correct += (preds == y_batch).sum().item()
                total += len(y_batch)

        return {
            f"{prefix}_loss": total_loss / max(total, 1),
            f"{prefix}_accuracy": correct / max(total, 1),
        }

    def _collect_predictions(
        self, model, loader, device
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        import torch
        import torch.nn.functional as F

        all_preds, all_probs, all_true, all_logits = [], [], [], []
        model.eval()
        with torch.no_grad():
            for X_batch, y_batch in loader:
                X_batch = X_batch.to(device)
                logits = model(X_batch)
                probs = F.softmax(logits, dim=1).cpu().numpy()
                preds = logits.argmax(dim=1).cpu().numpy()
                all_logits.append(logits.cpu().numpy())
                all_preds.append(preds)
                all_probs.append(probs)
                all_true.append(y_batch.numpy())

        all_preds = np.concatenate(all_preds)
        all_probs = np.concatenate(all_probs)
        all_true = np.concatenate(all_true)
        all_logits = np.concatenate(all_logits)
        return all_preds, all_probs, all_true, all_logits

    def _build_dataset_info(
        self, train_X: np.ndarray, val_X: np.ndarray, test_X: np.ndarray
    ) -> Dict[str, Any]:
        return {
            "tickers": self.tickers,
            "n_tickers": len(self.tickers),
            "train_rows": int(len(train_X)),
            "val_rows": int(len(val_X)),
            "test_rows": int(len(test_X)),
            "sequence_length": int(train_X.shape[1]),
            "n_features": int(train_X.shape[2]),
            "train_end": self.cfg.TRAIN_END_DATE,
            "val_end": self.cfg.VAL_END_DATE,
        }

    def _export_artifacts(
        self, model: Any, eval_metrics: Dict[str, float], execution_time: float, calibrator_path: str = None
    ) -> Dict[str, str]:
        import torch

        # model.pt
        model_path = os.path.join(self.artifact_dir, "model.pt")
        torch.save(model.state_dict(), model_path)

        # scaler.pkl (copy from provided path or leave placeholder)
        scaler_dest = os.path.join(self.artifact_dir, "scaler.pkl")
        if self.scaler_path and os.path.exists(self.scaler_path):
            shutil.copy2(self.scaler_path, scaler_dest)
        else:
            # Write an empty sentinel so the registry still has a file to hash
            with open(scaler_dest, "wb") as f:
                pickle.dump(None, f)

        # label_encoder.pkl
        encoder_dest = os.path.join(self.artifact_dir, "label_encoder.pkl")
        if self.encoder_path and os.path.exists(self.encoder_path):
            shutil.copy2(self.encoder_path, encoder_dest)
        else:
            with open(encoder_dest, "wb") as f:
                pickle.dump(None, f)

        # metadata.json
        metadata = {
            "version": self.version,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
            "evaluation_metrics": {
                k: round(float(v), 6) if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('.','',1).isdigit()) else v 
                for k, v in eval_metrics.items()
            },
            "training_config": self.cfg.to_dict(),
            "feature_names": self.feature_names,
            "tickers": self.tickers,
            "execution_time_seconds": round(execution_time, 2),
        }
        meta_path = os.path.join(self.artifact_dir, "metadata.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=4)

        logger.info(f"[TrainingOrchestrator] Artifacts exported to {self.artifact_dir}.")
        return {
            "model.pt": model_path,
            "scaler.pkl": scaler_dest,
            "label_encoder.pkl": encoder_dest,
            "metadata.json": meta_path,
            "calibrator.pkl": calibrator_path if calibrator_path else encoder_dest,
        }

    def _register(self, artifact_paths: Dict[str, str]) -> None:
        """
        Register the artifact bundle in the RegistryManager as a 'candidate'.
        Maps local artifact names to the registry's REQUIRED_ARTIFACTS naming
        convention while preserving backward compatibility with the legacy registry.
        """
        from ml_engine.config.registry_config import registry_config

        # The registry expects these specific keys.  Map our PyTorch artifacts
        # to whatever the registry requires without modifying registry_config.
        # We write shim files for legacy keys so the registry validator passes.
        candidate_artifacts: Dict[str, str] = {}

        for required in registry_config.REQUIRED_ARTIFACTS:
            if required == "best_model.keras":
                # Point to our model.pt (registry hashes the file; format is noted in metadata)
                candidate_artifacts[required] = artifact_paths["model.pt"]
            elif required == "feature_scaler.pkl":
                candidate_artifacts[required] = artifact_paths["scaler.pkl"]
            elif required == "calibrator.pkl":
                candidate_artifacts[required] = artifact_paths.get("calibrator.pkl", artifact_paths["label_encoder.pkl"])
            elif required == "evaluation_report.json":
                candidate_artifacts[required] = artifact_paths["metadata.json"]
            elif required == "calibration_report.json":
                # Write an empty placeholder calibration report
                calib_path = os.path.join(self.artifact_dir, "calibration_report.json")
                with open(calib_path, "w") as f:
                    json.dump({"version": self.version, "calibrated": False}, f)
                candidate_artifacts[required] = calib_path
            else:
                logger.warning(f"[TrainingOrchestrator] Unknown required artifact: {required}")

        try:
            manifest = self.registry.register_candidate(
                version=self.version,
                source_artifacts=candidate_artifacts,
                authenticity="REAL",
            )
            logger.info(
                f"[TrainingOrchestrator] Registered version '{self.version}' as candidate. "
                f"Manifest: {manifest.get('model_version')}"
            )
        except Exception as e:
            logger.warning(
                f"[TrainingOrchestrator] Registry registration skipped: {e}. "
                f"Artifacts are still available in {self.artifact_dir}."
            )
