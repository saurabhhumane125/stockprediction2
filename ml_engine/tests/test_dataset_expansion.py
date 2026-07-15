"""
ml_engine/tests/test_dataset_expansion.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for Milestone 21 – Production Dataset Expansion.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import json
import pytest
import pandas as pd
import numpy as np

from ml_engine.data.universe.manager import UniverseManager
from ml_engine.data.universe.config import UniverseConfig
from ml_engine.data.download.parallel_downloader import ParallelDownloadEngine
from ml_engine.data.storage.parquet_partitioner import PartitionedParquetStorage
from ml_engine.data.etl.metadata_manager import MetadataManager
from ml_engine.data.etl.incremental_updater import IncrementalETLManager
from ml_engine.data.reports.data_quality import DataQualityReportBuilder


def test_universe_manager():
    # Test valid
    core = UniverseManager.get_universe("CORE")
    assert "RELIANCE.NS" in core
    assert "TCS.NS" in core
    
    # Test invalid
    with pytest.raises(ValueError):
        UniverseManager.get_universe("INVALID_UNIVERSE")


def test_parquet_partitioner(tmp_path):
    root = str(tmp_path)
    storage = PartitionedParquetStorage(root)
    
    # Create dummy DataFrame
    dates = pd.date_range("2026-01-01", periods=3, freq="D")
    df = pd.DataFrame({
        "open": [100, 101, 102],
        "close": [101, 102, 103],
        "volume": [1000, 2000, 3000]
    }, index=dates)
    
    # Test Write
    path = storage.write_partition(df, "TEST_UNIV", "v1", "TEST_TICKER")
    assert os.path.exists(path)
    
    # Test Read
    read_df = storage.read_partition("TEST_UNIV", "v1", "TEST_TICKER")
    assert not read_df.empty
    assert len(read_df) == 3
    
    # Test Append
    dates2 = pd.date_range("2026-01-04", periods=2, freq="D")
    df2 = pd.DataFrame({
        "open": [104, 105],
        "close": [105, 106],
        "volume": [4000, 5000]
    }, index=dates2)
    
    storage.write_partition(df2, "TEST_UNIV", "v1", "TEST_TICKER", mode="append")
    read_df2 = storage.read_partition("TEST_UNIV", "v1", "TEST_TICKER")
    assert len(read_df2) == 5
    
    # Test Latest Date
    latest = storage.get_latest_date("TEST_UNIV", "v1", "TEST_TICKER")
    assert latest.strftime("%Y-%m-%d") == "2026-01-05"


def test_metadata_manager_and_checksum(tmp_path):
    root = str(tmp_path)
    storage = PartitionedParquetStorage(root)
    
    dates = pd.date_range("2026-01-01", periods=2)
    df = pd.DataFrame({"close": [100, 101]}, index=dates)
    storage.write_partition(df, "TEST_UNIV", "v1", "TEST_TICKER")
    
    checksum = storage.generate_checksum("TEST_UNIV", "v1")
    assert len(checksum) == 64  # SHA256 length
    
    meta_manager = MetadataManager(root)
    path = meta_manager.write_metadata("TEST_UNIV", "v1", ["TEST_TICKER"], "hash_123", checksum)
    
    assert os.path.exists(path)
    loaded = meta_manager.read_metadata("TEST_UNIV", "v1")
    assert loaded["ticker_count"] == 1
    assert loaded["data_checksum"] == checksum


def test_incremental_planner(tmp_path):
    root = str(tmp_path)
    etl = IncrementalETLManager(root)
    
    dates = pd.date_range("2026-01-01", "2026-01-05", freq="D")
    df = pd.DataFrame({"close": [1, 2, 3, 4, 5]}, index=dates)
    etl.storage.write_partition(df, "CORE", "v1", "RELIANCE.NS")
    
    tasks = etl._plan_downloads(["RELIANCE.NS", "TCS.NS"], "CORE", "v1", "2026-01-01", "2026-01-10")
    
    # RELIANCE has data up to 2026-01-05, should start from 2026-01-06
    assert tasks["RELIANCE.NS"][0] == "2026-01-06"
    
    # TCS has no data, should start from global start
    assert tasks["TCS.NS"][0] == "2026-01-01"


def test_data_quality_report(tmp_path):
    root = str(tmp_path)
    storage = PartitionedParquetStorage(root)
    
    dates = pd.date_range("2026-01-01", periods=10, freq="B")  # Business days
    df = pd.DataFrame({"close": np.random.rand(10)}, index=dates)
    storage.write_partition(df, "CORE", "v1", "RELIANCE.NS")
    
    builder = DataQualityReportBuilder(storage, root)
    paths = builder.build_report("CORE", "v1", ["RELIANCE.NS", "MISSING.NS"])
    
    assert os.path.exists(paths["json"])
    assert os.path.exists(paths["markdown"])
    
    with open(paths["json"], "r") as f:
        data = json.load(f)
        assert data["expected_count"] == 2
        assert data["actual_count"] == 1
        assert "MISSING.NS" in data["missing_tickers"]
