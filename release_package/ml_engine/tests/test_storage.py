import os
import tempfile
import json
import pandas as pd
import pytest

from ml_engine.data.storage.parquet_storage import ParquetStorage


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4.0, 5.0, 6.0]
    }, index=pd.date_range("2023-01-01", periods=3))


@pytest.fixture
def storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield ParquetStorage(base_path=tmpdir)


def test_parquet_storage_save_load(storage, sample_df):
    path = "test_data/data.parquet"
    
    # Save
    storage.save_dataframe(sample_df, path)
    assert storage.exists(path)
    
    # Load
    loaded_df = storage.load_dataframe(path)
    pd.testing.assert_frame_equal(sample_df, loaded_df, check_freq=False)


def test_parquet_storage_metadata(storage):
    path = "test_data/meta.json"
    meta = {"version": "1.0", "hash": "abcdef"}
    
    storage.save_metadata(meta, path)
    assert storage.exists(path)
    
    with open(os.path.join(storage.base_path, path), "r") as f:
        loaded = json.load(f)
        
    assert loaded == meta


def test_parquet_storage_not_found(storage):
    with pytest.raises(FileNotFoundError):
        storage.load_dataframe("non_existent.parquet")
