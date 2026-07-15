"""
ml_engine/tests/test_generate_dataset.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for Production Dataset Generation orchestration script.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock

import pandas as pd

from ml_engine.scripts.generate_dataset import generate_manifest, main


def test_generate_manifest(tmp_path):
    out_dir = str(tmp_path)
    stats = {"total_rows_final": 1000}
    
    path = generate_manifest(
        output_dir=out_dir,
        universe="CORE",
        dataset_version="v1.0",
        stats=stats,
        checksum="dummy_checksum",
        tickers=["TCS.NS"]
    )
    
    assert os.path.exists(path)
    with open(path, "r") as f:
        data = json.load(f)
        
    assert data["dataset_version"] == "v1.0"
    assert data["universe"] == "CORE"
    assert data["checksums"] == "dummy_checksum"
    assert "TCS.NS" in data["ticker_list"]


@patch("ml_engine.scripts.generate_dataset.sys.argv", ["generate_dataset.py", "--universe", "CORE", "--dataset-version", "v1.0", "--start-date", "2024-01-01", "--end-date", "2024-01-02", "--dry-run"])
@patch("ml_engine.scripts.generate_dataset.UniverseManager.get_universe")
@patch("ml_engine.scripts.generate_dataset.ParallelDownloadEngine.download_parallel")
@patch("ml_engine.scripts.generate_dataset.ProductionDataValidator.validate")
@patch("ml_engine.scripts.generate_dataset.FeatureGenerator.generate_all_features")
def test_generate_dataset_dry_run_success(mock_feat, mock_val, mock_dl, mock_uni):
    mock_uni.return_value = ["TCS.NS"]
    
    # Mock download to return some dummy data
    dates = pd.date_range("2024-01-01", periods=2)
    df = pd.DataFrame({
        "open": [100, 101], "high": [102, 103], "low": [99, 100], "close": [101, 102], "volume": [1000, 2000]
    }, index=dates)
    mock_dl.return_value = {"TCS.NS": df}
    
    # Mock validation success
    mock_val.return_value = (True, {})
    
    # Mock features
    mock_feat.return_value = df.copy()
    
    # Because it's a dry-run, sys.exit(0) is called at the end
    with pytest.raises(SystemExit) as excinfo:
        main()
        
    assert excinfo.value.code == 0
    assert mock_dl.called
    assert mock_val.called


@patch("ml_engine.scripts.generate_dataset.sys.argv", ["generate_dataset.py", "--universe", "CORE", "--dataset-version", "v1.0", "--start-date", "2024-01-01", "--end-date", "2024-01-02"])
@patch("ml_engine.scripts.generate_dataset.UniverseManager.get_universe")
@patch("ml_engine.scripts.generate_dataset.ParallelDownloadEngine.download_parallel")
@patch("ml_engine.scripts.generate_dataset.ProductionDataValidator.validate")
def test_generate_dataset_fail_fast(mock_val, mock_dl, mock_uni):
    mock_uni.return_value = ["TCS.NS"]
    
    dates = pd.date_range("2024-01-01", periods=2)
    df = pd.DataFrame({
        "open": [100, 101], "high": [102, 103], "low": [99, 100], "close": [101, 102], "volume": [1000, 2000]
    }, index=dates)
    mock_dl.return_value = {"TCS.NS": df}
    
    # Mock validation FAILURE
    mock_val.return_value = (False, {})
    
    # Should exit with code 1 due to fail-fast
    with pytest.raises(SystemExit) as excinfo:
        main()
        
    assert excinfo.value.code == 1
