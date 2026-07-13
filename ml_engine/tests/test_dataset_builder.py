import os
import tempfile
import json
import pandas as pd
import numpy as np
import pytest
from typing import Dict, Any, Optional

from ml_engine.data.datasets.splitter import TemporalSplitter
from ml_engine.data.datasets.builder import DatasetBuilder
from ml_engine.data.storage.parquet_storage import ParquetStorage
from ml_engine.interfaces.base_downloader import BaseDownloader


# Mock downloader to provide controlled dummy data
class MockDownloader(BaseDownloader):
    def download(self, ticker: str) -> Optional[pd.DataFrame]:
        if ticker == "EMPTY":
            return pd.DataFrame()
            
        periods = 100
        dates = pd.date_range("2020-01-01", periods=periods, freq="D", tz="UTC")
        df = pd.DataFrame({
            "open": np.linspace(100, 150, periods),
            "high": np.linspace(102, 152, periods),
            "low": np.linspace(98, 148, periods),
            "close": np.linspace(101, 151, periods),
            "volume": np.full(periods, 1000),
            "dividends": np.zeros(periods),
            "stock_splits": np.zeros(periods)
        }, index=dates)
        return df
        
    def download_batch(self, tickers: list[str]) -> Dict[str, pd.DataFrame]:
        return {t: self.download(t) for t in tickers}
        
    def health_check(self) -> bool:
        return True


def test_temporal_splitter():
    dates = pd.date_range("2021-01-01", "2021-01-10", freq="D")
    df = pd.DataFrame({"val": range(len(dates))}, index=dates)
    
    splitter = TemporalSplitter()
    train_df, val_df, test_df = splitter.split_by_date(df, train_end="2021-01-05", val_end="2021-01-08")
    
    # Train: 01 to 05 (5 days)
    assert len(train_df) == 5
    assert train_df.index.max() == pd.Timestamp("2021-01-05")
    
    # Val: 06 to 08 (3 days)
    assert len(val_df) == 3
    assert val_df.index.max() == pd.Timestamp("2021-01-08")
    
    # Test: 09 to 10 (2 days)
    assert len(test_df) == 2
    assert test_df.index.min() == pd.Timestamp("2021-01-09")


def test_temporal_splitter_errors():
    dates = pd.date_range("2021-01-01", "2021-01-10", freq="D")
    df = pd.DataFrame({"val": range(len(dates))}, index=dates)
    splitter = TemporalSplitter()
    
    with pytest.raises(ValueError, match="strictly before"):
        # Train end >= Val end
        splitter.split_by_date(df, train_end="2021-01-08", val_end="2021-01-05")
        
    df_no_dt_index = pd.DataFrame({"val": range(10)})
    with pytest.raises(ValueError, match="DatetimeIndex"):
        splitter.split_by_date(df_no_dt_index, train_end="2021-01-05", val_end="2021-01-08")


def test_dataset_builder_e2e():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ParquetStorage(base_path=tmpdir)
        downloader = MockDownloader()
        builder = DatasetBuilder(downloader, storage, dataset_version="test_v1")
        
        # We need to monkey-patch training_config to match our mock data bounds (2020-01-01 to ~2020-04-09)
        from ml_engine.config.training_config import training_config
        original_train = training_config.TRAIN_END_DATE
        original_val = training_config.VAL_END_DATE
        
        training_config.TRAIN_END_DATE = "2020-02-15"
        training_config.VAL_END_DATE = "2020-03-15"
        
        try:
            metadata = builder.build_dataset("MOCK")
            
            assert metadata is not None
            assert metadata["ticker"] == "MOCK"
            assert metadata["dataset_version"] == "test_v1"
            assert "train_rows" in metadata["dimensions"]
            
            # Check files were written
            assert storage.exists("MOCK/test_v1/train.parquet")
            assert storage.exists("MOCK/test_v1/val.parquet")
            assert storage.exists("MOCK/test_v1/test.parquet")
            assert storage.exists("MOCK/test_v1/metadata.json")
            
            # Load metadata JSON to confirm atomicity matches
            with open(os.path.join(tmpdir, "MOCK/test_v1/metadata.json"), "r") as f:
                saved_meta = json.load(f)
                assert saved_meta["ticker"] == "MOCK"
                
        finally:
            training_config.TRAIN_END_DATE = original_train
            training_config.VAL_END_DATE = original_val


def test_dataset_builder_empty_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ParquetStorage(base_path=tmpdir)
        downloader = MockDownloader()
        builder = DatasetBuilder(downloader, storage)
        
        metadata = builder.build_dataset("EMPTY")
        assert metadata is None
