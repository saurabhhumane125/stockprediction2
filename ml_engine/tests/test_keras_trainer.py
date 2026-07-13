import os
import tempfile
import json
import numpy as np
import pytest

# Reduce TF logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from ml_engine.data.storage.numpy_storage import NumpyStorage
from ml_engine.training.keras_trainer import KerasTrainer
from ml_engine.models.gru.builder import build_gru_model
from ml_engine.config.training_config import training_config


@pytest.fixture
def dummy_data_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = NumpyStorage(base_path=tmpdir)
        base_path = "MOCK/v1"
        
        # 10 samples, sequence length 5, 2 features
        X_train = np.random.rand(10, 5, 2).astype(np.float32)
        y_train = np.random.randint(0, 2, size=(10,)).astype(np.float32)
        
        X_val = np.random.rand(5, 5, 2).astype(np.float32)
        y_val = np.random.randint(0, 2, size=(5,)).astype(np.float32)
        
        X_test = np.random.rand(5, 5, 2).astype(np.float32)
        y_test = np.random.randint(0, 2, size=(5,)).astype(np.float32)
        
        storage.save_arrays(f"{base_path}/train.npz", X=X_train, y=y_train)
        storage.save_arrays(f"{base_path}/val.npz", X=X_val, y=y_val)
        storage.save_arrays(f"{base_path}/test.npz", X=X_test, y=y_test)
        
        yield storage, tmpdir


def test_keras_trainer_e2e(dummy_data_dir, monkeypatch):
    storage, tmpdir = dummy_data_dir
    
    # Patch epochs for fast testing
    monkeypatch.setattr(training_config, "EPOCHS", 2)
    monkeypatch.setattr(training_config, "BATCH_SIZE", 2)
    
    artifact_dir = os.path.join(tmpdir, "artifacts")
    trainer = KerasTrainer(tensor_storage=storage, artifact_dir=artifact_dir)
    
    # 1. Train Model
    model = trainer.train(model_builder=build_gru_model, data_path="MOCK/v1", resume=False)
    
    # Assert artifacts created
    assert os.path.exists(os.path.join(artifact_dir, "best_model.keras"))
    assert os.path.exists(os.path.join(artifact_dir, "training_history.json"))
    assert os.path.exists(os.path.join(artifact_dir, "training_summary.json"))
    
    # Check history structure
    with open(os.path.join(artifact_dir, "training_history.json"), "r") as f:
        history = json.load(f)
        assert "loss" in history
        assert "val_loss" in history
        assert len(history["loss"]) > 0
        
    # Check summary structure
    with open(os.path.join(artifact_dir, "training_summary.json"), "r") as f:
        summary = json.load(f)
        assert "best_val_loss" in summary
        
    # 2. Evaluate Model
    metrics = trainer.evaluate(model, data_path="MOCK/v1")
    assert "loss" in metrics
    assert "accuracy" in metrics
    
    # 3. Resume Training
    monkeypatch.setattr(training_config, "EPOCHS", 1)
    resumed_model = trainer.train(model_builder=build_gru_model, data_path="MOCK/v1", resume=True)
    assert resumed_model is not None


def test_keras_trainer_insufficient_data(dummy_data_dir):
    storage, tmpdir = dummy_data_dir
    
    # Create empty arrays
    storage.save_arrays("EMPTY/v1/train.npz", X=np.array([]), y=np.array([]))
    storage.save_arrays("EMPTY/v1/val.npz", X=np.array([]), y=np.array([]))
    
    artifact_dir = os.path.join(tmpdir, "artifacts_empty")
    trainer = KerasTrainer(tensor_storage=storage, artifact_dir=artifact_dir)
    
    with pytest.raises(ValueError, match="Insufficient data"):
        trainer.train(model_builder=build_gru_model, data_path="EMPTY/v1")
