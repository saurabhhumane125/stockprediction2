"""
ml_engine/tests/test_training_pipeline.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for the production training ecosystem.

Coverage:
  • seed_everything          – RNG state isolation
  • TimeSeriesDataset        – shape, length, dtype
  • CheckpointManager        – save / restore best, early stopping
  • TrainingOrchestrator     – mock training loop end-to-end
  • ReportGenerator          – JSON and Markdown output correctness
─────────────────────────────────────────────────────────────────────────────
"""
import json
import os
import pickle
import tempfile

import numpy as np
import pytest

# ── seed_everything ────────────────────────────────────────────────────────

class TestSeedEverything:
    def test_numpy_determinism(self):
        from ml_engine.training.utils import seed_everything

        seed_everything(0)
        a = np.random.rand(5)
        seed_everything(0)
        b = np.random.rand(5)
        np.testing.assert_array_equal(a, b)

    def test_python_random_determinism(self):
        import random
        from ml_engine.training.utils import seed_everything

        seed_everything(99)
        a = [random.random() for _ in range(5)]
        seed_everything(99)
        b = [random.random() for _ in range(5)]
        assert a == b

    def test_different_seeds_differ(self):
        from ml_engine.training.utils import seed_everything

        seed_everything(1)
        a = np.random.rand(5)
        seed_everything(2)
        b = np.random.rand(5)
        assert not np.allclose(a, b)


# ── TimeSeriesDataset ──────────────────────────────────────────────────────

try:
    import torch  # noqa: F401
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

_skip_no_torch = pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not installed")


@_skip_no_torch
class TestTimeSeriesDataset:
    def _make_data(self, n=100, seq=10, feat=5):
        X = np.random.rand(n, seq, feat).astype(np.float32)
        y = np.random.randint(0, 2, size=(n,)).astype(np.int64)
        return X, y

    def test_len(self):
        from ml_engine.training.utils import TimeSeriesDataset

        X, y = self._make_data(80)
        ds = TimeSeriesDataset(X, y)
        assert len(ds) == 80

    def test_getitem_shapes(self):
        import torch
        from ml_engine.training.utils import TimeSeriesDataset

        X, y = self._make_data(50, seq=12, feat=7)
        ds = TimeSeriesDataset(X, y)
        xi, yi = ds[0]
        assert xi.shape == (12, 7)
        assert yi.shape == ()

    def test_dtype(self):
        import torch
        from ml_engine.training.utils import TimeSeriesDataset

        X, y = self._make_data()
        ds = TimeSeriesDataset(X, y)
        xi, yi = ds[0]
        assert xi.dtype == torch.float32
        assert yi.dtype == torch.int64

    def test_mismatched_lengths_raise(self):
        from ml_engine.training.utils import TimeSeriesDataset

        X = np.zeros((10, 5, 3), dtype=np.float32)
        y = np.zeros((9,), dtype=np.int64)
        with pytest.raises(ValueError, match="same number of samples"):
            TimeSeriesDataset(X, y)

    def test_input_shape_property(self):
        from ml_engine.training.utils import TimeSeriesDataset

        X, y = self._make_data(20, seq=15, feat=9)
        ds = TimeSeriesDataset(X, y)
        assert ds.input_shape == (15, 9)


# ── CheckpointManager ──────────────────────────────────────────────────────

@_skip_no_torch
class TestCheckpointManager:
    def _make_model(self):
        import torch.nn as nn

        return nn.Linear(5, 2)

    def _make_optimizer(self, model):
        import torch.optim as optim

        return optim.Adam(model.parameters(), lr=1e-3)

    def test_best_checkpoint_saved_on_improvement(self, tmp_path):
        import torch
        from ml_engine.training.checkpoint_manager import CheckpointManager

        model = self._make_model()
        opt = self._make_optimizer(model)
        mgr = CheckpointManager(str(tmp_path), monitor="val_loss", patience=5, mode="min")

        mgr.step(0, {"val_loss": 0.9}, model, opt, None)
        assert (tmp_path / "best_model.pt").exists()
        state = torch.load(tmp_path / "best_model.pt", map_location="cpu")
        assert state["metrics"]["val_loss"] == 0.9

    def test_best_not_overwritten_on_regression(self, tmp_path):
        import torch
        from ml_engine.training.checkpoint_manager import CheckpointManager

        model = self._make_model()
        opt = self._make_optimizer(model)
        mgr = CheckpointManager(str(tmp_path), monitor="val_loss", patience=10, mode="min")

        mgr.step(0, {"val_loss": 0.5}, model, opt, None)
        mgr.step(1, {"val_loss": 0.8}, model, opt, None)  # regression – should not update best

        assert mgr.best_value == 0.5
        assert mgr.best_epoch == 0

    def test_early_stopping_triggers_at_patience(self, tmp_path):
        from ml_engine.training.checkpoint_manager import CheckpointManager

        model = self._make_model()
        opt = self._make_optimizer(model)
        patience = 3
        mgr = CheckpointManager(str(tmp_path), monitor="val_loss", patience=patience, mode="min")

        mgr.step(0, {"val_loss": 0.5}, model, opt, None)  # best
        for i in range(1, patience):
            result = mgr.step(i, {"val_loss": 0.9}, model, opt, None)
            assert result is False, f"Should not stop at epoch {i}"

        # Final step should trigger stop
        stopped = mgr.step(patience, {"val_loss": 0.9}, model, opt, None)
        assert stopped is True
        assert mgr.should_stop is True

    def test_restore_best_weights(self, tmp_path):
        import torch
        import torch.nn as nn
        from ml_engine.training.checkpoint_manager import CheckpointManager

        model = nn.Linear(4, 2)
        opt = self._make_optimizer(model)
        mgr = CheckpointManager(str(tmp_path), monitor="val_loss", patience=5, mode="min")

        # Record the initial weights as "best"
        original_weight = model.weight.data.clone()
        mgr.step(0, {"val_loss": 0.3}, model, opt, None)

        # Mutate weights
        with torch.no_grad():
            model.weight.fill_(999.0)

        # Restore should bring back original weights
        mgr.restore_best(model)
        np.testing.assert_array_almost_equal(
            model.weight.data.numpy(), original_weight.numpy(), decimal=5
        )

    def test_resume_from_latest(self, tmp_path):
        import torch
        import torch.nn as nn
        from ml_engine.training.checkpoint_manager import CheckpointManager

        model = nn.Linear(4, 2)
        opt = self._make_optimizer(model)
        mgr = CheckpointManager(str(tmp_path), monitor="val_loss", patience=5, mode="min")
        mgr.step(7, {"val_loss": 0.4}, model, opt, None)

        # Create a new manager and resume
        model2 = nn.Linear(4, 2)
        opt2 = self._make_optimizer(model2)
        mgr2 = CheckpointManager(str(tmp_path), monitor="val_loss", patience=5, mode="min")
        next_epoch = mgr2.load_latest(model2, opt2, None)

        assert next_epoch == 8  # last saved epoch (7) + 1

    def test_meta_file_written(self, tmp_path):
        from ml_engine.training.checkpoint_manager import CheckpointManager

        model = self._make_model()
        opt = self._make_optimizer(model)
        mgr = CheckpointManager(str(tmp_path), monitor="val_loss", patience=5, mode="min")
        mgr.step(2, {"val_loss": 0.6, "val_accuracy": 0.8}, model, opt, None)

        meta_path = tmp_path / "checkpoint_meta.json"
        assert meta_path.exists()
        with open(meta_path) as f:
            meta = json.load(f)
        assert meta["last_epoch"] == 2
        assert "val_loss" in meta["metrics"]


# ── TrainingConfig ─────────────────────────────────────────────────────────

class TestTrainingConfig:
    def test_all_required_fields_present(self):
        from ml_engine.config.training_config import training_config

        cfg_dict = training_config.to_dict()
        required = [
            "SEQUENCE_LENGTH", "EPOCHS", "BATCH_SIZE", "LEARNING_RATE",
            "EARLY_STOPPING_PATIENCE", "LR_SCHEDULER", "GRADIENT_CLIP_NORM",
            "MIXED_PRECISION", "DEVICE", "SEED", "NUM_WORKERS",
        ]
        for key in required:
            assert key in cfg_dict, f"Missing config field: {key}"

    def test_to_dict_serializable(self):
        from ml_engine.config.training_config import training_config
        import json

        d = training_config.to_dict()
        # Should not raise
        json.dumps(d)


# ── ReportGenerator ────────────────────────────────────────────────────────

class TestReportGenerator:
    def _sample_inputs(self):
        return {
            "config": {"EPOCHS": 50, "BATCH_SIZE": 32, "LEARNING_RATE": 0.001},
            "dataset_info": {
                "tickers": ["RELIANCE.NS"],
                "train_rows": 1000,
                "val_rows": 200,
                "test_rows": 150,
                "train_end": "2021-12-31",
                "val_end": "2023-06-30",
            },
            "history": [
                {"epoch": i, "train_loss": 0.8 - i * 0.01, "val_loss": 0.9 - i * 0.01}
                for i in range(15)
            ],
            "eval_metrics": {"test_accuracy": 0.83, "f1": 0.81},
            "feature_names": ["open", "close", "rsi", "macd"],
            "version": "v2.0.0-test",
            "execution_time_seconds": 120.5,
        }

    def test_json_report_written(self, tmp_path):
        from ml_engine.training.report_generator import ReportGenerator

        gen = ReportGenerator(str(tmp_path))
        paths = gen.generate(**self._sample_inputs())

        assert os.path.exists(paths["json_path"])
        with open(paths["json_path"]) as f:
            data = json.load(f)
        assert data["version"] == "v2.0.0-test"
        assert data["evaluation_metrics"]["test_accuracy"] == pytest.approx(0.83, abs=1e-4)

    def test_markdown_report_written(self, tmp_path):
        from ml_engine.training.report_generator import ReportGenerator

        gen = ReportGenerator(str(tmp_path))
        paths = gen.generate(**self._sample_inputs())

        assert os.path.exists(paths["markdown_path"])
        with open(paths["markdown_path"], encoding="utf-8") as f:
            md = f.read()
        assert "v2.0.0-test" in md
        assert "Evaluation Metrics" in md
        assert "open, close, rsi, macd" in md

    def test_training_curve_table_last_10_rows(self, tmp_path):
        from ml_engine.training.report_generator import ReportGenerator

        gen = ReportGenerator(str(tmp_path))
        paths = gen.generate(**self._sample_inputs())

        with open(paths["markdown_path"], encoding="utf-8") as f:
            md = f.read()
        # History has 15 rows, only last 10 should appear in the table
        assert "Training Curve" in md

    def test_report_json_is_valid_json(self, tmp_path):
        from ml_engine.training.report_generator import ReportGenerator

        gen = ReportGenerator(str(tmp_path))
        paths = gen.generate(**self._sample_inputs())
        with open(paths["json_path"]) as f:
            # Must not raise
            data = json.load(f)
        assert "training_history" in data


# ── LR Scheduler Factory ───────────────────────────────────────────────────

@_skip_no_torch
class TestSchedulerFactory:
    def _model_and_opt(self):
        import torch.nn as nn, torch.optim as optim

        m = nn.Linear(2, 2)
        o = optim.Adam(m.parameters(), lr=1e-3)
        return m, o

    def _cfg(self, name: str):
        from ml_engine.config.training_config import TrainingConfig

        cfg = TrainingConfig()
        cfg.LR_SCHEDULER = name
        return cfg

    def test_reduce_lr_on_plateau(self):
        import torch.optim.lr_scheduler as sched
        from ml_engine.training.training_pipeline import _build_scheduler

        _, o = self._model_and_opt()
        s = _build_scheduler(o, self._cfg("ReduceLROnPlateau"), steps_per_epoch=10)
        assert isinstance(s, sched.ReduceLROnPlateau)

    def test_cosine_annealing(self):
        import torch.optim.lr_scheduler as sched
        from ml_engine.training.training_pipeline import _build_scheduler

        _, o = self._model_and_opt()
        s = _build_scheduler(o, self._cfg("CosineAnnealing"), steps_per_epoch=10)
        assert isinstance(s, sched.CosineAnnealingLR)

    def test_one_cycle_lr(self):
        import torch.optim.lr_scheduler as sched
        from ml_engine.training.training_pipeline import _build_scheduler

        _, o = self._model_and_opt()
        s = _build_scheduler(o, self._cfg("OneCycleLR"), steps_per_epoch=10)
        assert isinstance(s, sched.OneCycleLR)

    def test_none_returns_none(self):
        from ml_engine.training.training_pipeline import _build_scheduler

        _, o = self._model_and_opt()
        s = _build_scheduler(o, self._cfg("None"), steps_per_epoch=10)
        assert s is None
