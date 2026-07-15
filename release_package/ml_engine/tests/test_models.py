"""
ml_engine/tests/test_models.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for Milestone 17 – Production Model Architecture.

Coverage:
  • ModelConfig       – required fields, JSON serialisability
  • WeightInit        – all strategies apply without error, invalid raises
  • BaseModel         – save / load / predict / parameter_count / summary
  • GRUClassifier     – forward shape, config-driven dimensions
  • BiGRUClassifier   – forward shape, bidirectional hidden concat
  • LSTMClassifier    – forward shape
  • TransformerClassifier  – forward shape, bad head count raises
  • ModelFactory      – create, list_models, make_builder, bad key raises
─────────────────────────────────────────────────────────────────────────────
"""
import os
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# All tests require PyTorch
# ─────────────────────────────────────────────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

skip_no_torch = pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not installed")

# Convenience: shapes used throughout
BATCH, SEQ, FEAT = 8, 48, 23
CLASSES = 2


# ── Helpers ────────────────────────────────────────────────────────────────

def _dummy_input() -> "torch.Tensor":
    import torch
    return torch.randn(BATCH, SEQ, FEAT)


# ── ModelConfig ───────────────────────────────────────────────────────────

class TestModelConfig:
    def test_required_fields_present(self):
        from ml_engine.config.model_config import model_config
        d = model_config.to_dict()
        for field in [
            "MODEL_TYPE", "HIDDEN_SIZE", "NUM_LAYERS", "DROPOUT",
            "OUTPUT_CLASSES", "BIDIRECTIONAL", "ACTIVATION",
            "NORMALIZATION", "DEVICE", "WEIGHT_INIT",
            "TRANSFORMER_HEADS", "TRANSFORMER_FF_DIM", "TRANSFORMER_DEPTH",
            # Legacy fields preserved for Keras compatibility
            "GRU_HIDDEN_DIM", "GRU_LAYERS", "GRU_DROPOUT",
            "BIGRU_HIDDEN_DIM", "BIGRU_LAYERS", "BIGRU_DROPOUT",
        ]:
            assert field in d, f"Missing field: {field}"

    def test_json_serialisable(self):
        import json
        from ml_engine.config.model_config import model_config
        json.dumps(model_config.to_dict())  # must not raise


# ── WeightInit ────────────────────────────────────────────────────────────

@skip_no_torch
class TestWeightInit:
    def _simple_model(self):
        return nn.GRU(input_size=5, hidden_size=8, num_layers=1, batch_first=True)

    def test_all_strategies_apply_without_error(self):
        from ml_engine.models.weight_init import apply_weight_init

        strategies = [
            "xavier_uniform", "xavier_normal",
            "kaiming_uniform", "kaiming_normal",
            "orthogonal", "default",
        ]
        for s in strategies:
            model = self._simple_model()
            apply_weight_init(model, s)  # must not raise

    def test_invalid_strategy_raises(self):
        from ml_engine.models.weight_init import apply_weight_init
        with pytest.raises(ValueError, match="Unknown weight init"):
            apply_weight_init(self._simple_model(), "nonexistent_strategy")

    def test_linear_xavier_zeros_bias(self):
        from ml_engine.models.weight_init import apply_weight_init
        lin = nn.Linear(4, 4)
        apply_weight_init(lin, "xavier_uniform")
        import torch
        assert torch.all(lin.bias == 0), "Bias should be zeroed by xavier_uniform"


# ── BaseModel ─────────────────────────────────────────────────────────────

@skip_no_torch
class TestBaseModel:
    def _make_gru(self):
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        return GRUClassifier(input_size=FEAT, hidden_size=16, num_layers=1, output_classes=CLASSES)

    def test_parameter_count_positive(self):
        m = self._make_gru()
        counts = m.parameter_count()
        assert counts["total"] > 0
        assert counts["trainable"] > 0
        assert counts["non_trainable"] == 0

    def test_summary_keys(self):
        m = self._make_gru()
        s = m.summary()
        for key in ["architecture", "input_size", "output_classes",
                    "trainable_params", "total_params", "estimated_memory_mb"]:
            assert key in s, f"Missing summary key: {key}"

    def test_summary_memory_positive(self):
        m = self._make_gru()
        assert m.summary()["estimated_memory_mb"] > 0

    def test_save_and_load(self, tmp_path):
        import torch
        m = self._make_gru()
        path = str(tmp_path / "model.pt")
        m.save(path)
        assert os.path.exists(path)

        m2 = self._make_gru()
        m2.load(path, device="cpu")
        # Verify weights are identical
        for p1, p2 in zip(m.parameters(), m2.parameters()):
            assert torch.allclose(p1, p2), "Loaded weights differ"

    def test_load_missing_file_raises(self, tmp_path):
        m = self._make_gru()
        with pytest.raises(FileNotFoundError):
            m.load(str(tmp_path / "nonexistent.pt"))

    def test_predict_returns_correct_shapes(self):
        import torch
        m = self._make_gru()
        X = torch.randn(BATCH, SEQ, FEAT)
        labels, probs = m.predict(X, device="cpu")
        assert labels.shape == (BATCH,)
        assert probs.shape == (BATCH, CLASSES)

    def test_predict_probabilities_sum_to_one(self):
        import torch
        m = self._make_gru()
        X = torch.randn(BATCH, SEQ, FEAT)
        _, probs = m.predict(X)
        row_sums = probs.sum(dim=1)
        torch.testing.assert_close(row_sums, torch.ones(BATCH), atol=1e-5, rtol=1e-5)


# ── GRUClassifier ─────────────────────────────────────────────────────────

@skip_no_torch
class TestGRUClassifier:
    def test_output_shape(self):
        import torch
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        m = GRUClassifier(input_size=FEAT, hidden_size=32, num_layers=2, output_classes=CLASSES)
        out = m(_dummy_input())
        assert out.shape == (BATCH, CLASSES)

    def test_single_layer_no_dropout_on_gru(self):
        """nn.GRU raises if dropout > 0 and num_layers == 1."""
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        m = GRUClassifier(input_size=FEAT, hidden_size=16, num_layers=1, dropout=0.5)
        # Should not raise
        out = m(_dummy_input())
        assert out.shape == (BATCH, CLASSES)

    def test_layer_norm_applied(self):
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        m = GRUClassifier(input_size=FEAT, normalization="layer")
        assert isinstance(m.norm, __import__("torch.nn", fromlist=["LayerNorm"]).LayerNorm)

    def test_batch_norm_applied(self):
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        m = GRUClassifier(input_size=FEAT, normalization="batch")
        assert isinstance(m.norm, __import__("torch.nn", fromlist=["BatchNorm1d"]).BatchNorm1d)

    def test_no_norm(self):
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        m = GRUClassifier(input_size=FEAT, normalization="none")
        assert m.norm is None

    def test_custom_classes(self):
        import torch
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        m = GRUClassifier(input_size=FEAT, output_classes=3)
        out = m(_dummy_input())
        assert out.shape == (BATCH, 3)


# ── BiGRUClassifier ───────────────────────────────────────────────────────

@skip_no_torch
class TestBiGRUClassifier:
    def test_output_shape(self):
        from ml_engine.models.bigru.bigru_classifier import BiGRUClassifier
        m = BiGRUClassifier(input_size=FEAT, hidden_size=32, num_layers=2, output_classes=CLASSES)
        out = m(_dummy_input())
        assert out.shape == (BATCH, CLASSES)

    def test_classifier_input_is_doubled(self):
        from ml_engine.models.bigru.bigru_classifier import BiGRUClassifier
        hidden = 16
        m = BiGRUClassifier(input_size=FEAT, hidden_size=hidden)
        # Classifier in-features should be 2 * hidden_size
        assert m.classifier.in_features == hidden * 2

    def test_gru_is_bidirectional(self):
        from ml_engine.models.bigru.bigru_classifier import BiGRUClassifier
        m = BiGRUClassifier(input_size=FEAT)
        assert m.gru.bidirectional is True


# ── LSTMClassifier ────────────────────────────────────────────────────────

@skip_no_torch
class TestLSTMClassifier:
    def test_output_shape(self):
        from ml_engine.models.lstm.lstm_classifier import LSTMClassifier
        m = LSTMClassifier(input_size=FEAT, hidden_size=32, num_layers=2, output_classes=CLASSES)
        out = m(_dummy_input())
        assert out.shape == (BATCH, CLASSES)

    def test_uses_lstm_module(self):
        from ml_engine.models.lstm.lstm_classifier import LSTMClassifier
        m = LSTMClassifier(input_size=FEAT)
        assert isinstance(m.lstm, __import__("torch.nn", fromlist=["LSTM"]).LSTM)

    def test_custom_hidden_size(self):
        import torch
        from ml_engine.models.lstm.lstm_classifier import LSTMClassifier
        m = LSTMClassifier(input_size=FEAT, hidden_size=128)
        out = m(torch.randn(4, SEQ, FEAT))
        assert out.shape == (4, CLASSES)


# ── TransformerClassifier ─────────────────────────────────────────────────

@skip_no_torch
class TestTransformerClassifier:
    def test_output_shape(self):
        from ml_engine.models.transformer.transformer_classifier import TransformerClassifier
        m = TransformerClassifier(
            input_size=FEAT, hidden_size=64, num_heads=4,
            ff_dim=128, num_layers=2, output_classes=CLASSES
        )
        out = m(_dummy_input())
        assert out.shape == (BATCH, CLASSES)

    def test_bad_head_count_raises(self):
        from ml_engine.models.transformer.transformer_classifier import TransformerClassifier
        with pytest.raises(ValueError, match="divisible by num_heads"):
            TransformerClassifier(input_size=FEAT, hidden_size=64, num_heads=7)

    def test_positional_encoding_registered_buffer(self):
        from ml_engine.models.transformer.transformer_classifier import (
            TransformerClassifier, SinusoidalPositionalEncoding
        )
        pe = SinusoidalPositionalEncoding(hidden_size=16, max_len=100)
        assert "pe" in dict(pe.named_buffers())

    def test_custom_depth(self):
        import torch
        from ml_engine.models.transformer.transformer_classifier import TransformerClassifier
        m = TransformerClassifier(
            input_size=FEAT, hidden_size=32, num_heads=4,
            ff_dim=64, num_layers=4, output_classes=CLASSES
        )
        out = m(torch.randn(4, SEQ, FEAT))
        assert out.shape == (4, CLASSES)


# ── ModelFactory ──────────────────────────────────────────────────────────

@skip_no_torch
class TestModelFactory:
    def test_list_models_contains_all_builtins(self):
        from ml_engine.models.model_factory import ModelFactory
        models = ModelFactory.list_models()
        for key in ["gru", "bigru", "lstm", "transformer"]:
            assert key in models, f"Missing: {key}"

    def test_create_gru(self):
        from ml_engine.models.model_factory import ModelFactory
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        m = ModelFactory.create(input_size=FEAT, model_type="GRU")
        assert isinstance(m, GRUClassifier)

    def test_create_bigru(self):
        from ml_engine.models.model_factory import ModelFactory
        from ml_engine.models.bigru.bigru_classifier import BiGRUClassifier
        m = ModelFactory.create(input_size=FEAT, model_type="BiGRU")
        assert isinstance(m, BiGRUClassifier)

    def test_create_lstm(self):
        from ml_engine.models.model_factory import ModelFactory
        from ml_engine.models.lstm.lstm_classifier import LSTMClassifier
        m = ModelFactory.create(input_size=FEAT, model_type="LSTM")
        assert isinstance(m, LSTMClassifier)

    def test_create_transformer(self):
        from ml_engine.models.model_factory import ModelFactory
        from ml_engine.models.transformer.transformer_classifier import TransformerClassifier
        m = ModelFactory.create(input_size=FEAT, model_type="Transformer")
        assert isinstance(m, TransformerClassifier)

    def test_overrides_applied(self):
        from ml_engine.models.model_factory import ModelFactory
        m = ModelFactory.create(
            input_size=FEAT, model_type="GRU",
            overrides={"hidden_size": 99}
        )
        assert m.hidden_size == 99

    def test_unknown_key_raises(self):
        from ml_engine.models.model_factory import ModelFactory
        with pytest.raises(KeyError, match="not registered"):
            ModelFactory.create(input_size=FEAT, model_type="NonExistentArch")

    def test_make_builder_returns_callable(self):
        from ml_engine.models.model_factory import ModelFactory
        builder = ModelFactory.make_builder(model_type="GRU")
        assert callable(builder)

    def test_make_builder_produces_correct_model(self):
        from ml_engine.models.model_factory import ModelFactory
        from ml_engine.models.gru.gru_classifier import GRUClassifier
        builder = ModelFactory.make_builder(model_type="GRU")
        model = builder(input_shape=(SEQ, FEAT))
        assert isinstance(model, GRUClassifier)

    def test_make_builder_forward_pass(self):
        import torch
        from ml_engine.models.model_factory import ModelFactory
        builder = ModelFactory.make_builder(model_type="LSTM")
        model = builder(input_shape=(SEQ, FEAT))
        out = model(torch.randn(4, SEQ, FEAT))
        assert out.shape == (4, CLASSES)

    def test_factory_model_serialisation(self, tmp_path):
        import torch
        from ml_engine.models.model_factory import ModelFactory
        model = ModelFactory.create(input_size=FEAT, model_type="GRU")
        path = str(tmp_path / "factory_model.pt")
        model.save(path)
        assert os.path.exists(path)
