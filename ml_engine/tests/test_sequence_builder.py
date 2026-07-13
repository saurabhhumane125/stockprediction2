import os
import tempfile
import json
import pandas as pd
import numpy as np
import pytest
from typing import Dict, Any

from ml_engine.data.storage.parquet_storage import ParquetStorage
from ml_engine.data.storage.numpy_storage import NumpyStorage
from ml_engine.data.datasets.sequence_builder import SequenceBuilder


@pytest.fixture
def dummy_data_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tabular_storage = ParquetStorage(base_path=tmpdir)
        tensor_storage = NumpyStorage(base_path=tmpdir)
        
        # Create dummy tabular data
        # Sequence length is 60, we need > 60 rows.
        rows = 100
        df = pd.DataFrame({
            "feat1": np.arange(rows),
            "feat2": np.arange(rows) * 2,
            "target": np.random.randint(0, 2, size=rows)
        }, index=pd.date_range("2020-01-01", periods=rows))
        
        # Split into train/val/test
        train_df = df.iloc[:70]
        val_df = df.iloc[70:85]
        test_df = df.iloc[85:]
        
        base_path = "MOCK/v1"
        tabular_storage.save_dataframe(train_df, f"{base_path}/train.parquet")
        tabular_storage.save_dataframe(val_df, f"{base_path}/val.parquet")
        tabular_storage.save_dataframe(test_df, f"{base_path}/test.parquet")
        
        yield tabular_storage, tensor_storage, tmpdir


def test_sequence_builder_execution(dummy_data_dir, monkeypatch):
    tabular_storage, tensor_storage, tmpdir = dummy_data_dir
    
    # Patch sequence length to 10 for faster testing, instead of default 60
    from ml_engine.config.training_config import training_config
    monkeypatch.setattr(training_config, "SEQUENCE_LENGTH", 10)
    
    builder = SequenceBuilder(tabular_storage, tensor_storage, dataset_version="v1")
    metadata = builder.build_sequences("MOCK")
    
    assert metadata is not None
    assert metadata["sequence_config"]["sequence_length"] == 10
    assert metadata["sequence_config"]["num_features"] == 2
    assert "feat1" in metadata["sequence_config"]["feature_order"]
    
    # Check if files were created
    base_path = os.path.join(tmpdir, "MOCK/v1")
    assert os.path.exists(f"{base_path}/train.npz")
    assert os.path.exists(f"{base_path}/val.npz")
    assert os.path.exists(f"{base_path}/test.npz")
    assert os.path.exists(f"{base_path}/sequences_metadata.json")
    
    # Verify exact tensor shapes
    # Train had 70 rows, seq_len=10 => 70 - 10 = 60 samples
    arrays = tensor_storage.load_arrays("MOCK/v1/train.npz")
    X_train, y_train = arrays["X"], arrays["y"]
    assert X_train.shape == (60, 10, 2)
    assert y_train.shape == (60,)
    
    # Val had 15 rows, seq_len=10 => 15 - 10 = 5 samples
    val_arrays = tensor_storage.load_arrays("MOCK/v1/val.npz")
    X_val = val_arrays["X"]
    assert X_val.shape == (5, 10, 2)


def test_sequence_builder_insufficient_data(dummy_data_dir, monkeypatch):
    tabular_storage, tensor_storage, tmpdir = dummy_data_dir
    
    # Set sequence length longer than train_df (70)
    from ml_engine.config.training_config import training_config
    monkeypatch.setattr(training_config, "SEQUENCE_LENGTH", 100)
    
    builder = SequenceBuilder(tabular_storage, tensor_storage, dataset_version="v1")
    metadata = builder.build_sequences("MOCK")
    
    # Should fail and return None
    assert metadata is None


def test_numpy_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = NumpyStorage(base_path=tmpdir)
        
        X = np.ones((10, 5, 2))
        y = np.zeros(10)
        
        storage.save_arrays("test.npz", X=X, y=y)
        assert storage.exists("test.npz")
        
        arrays = storage.load_arrays("test.npz")
        assert "X" in arrays
        assert "y" in arrays
        assert np.array_equal(arrays["X"], X)
        assert np.array_equal(arrays["y"], y)
        
        storage.save_metadata({"key": "val"}, "meta.json")
        with open(os.path.join(tmpdir, "meta.json"), "r") as f:
            assert json.load(f)["key"] == "val"
