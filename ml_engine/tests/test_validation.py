import os
import tempfile
import pandas as pd
import numpy as np
import pytest

from ml_engine.data.validation.validators import ProductionDataValidator
from ml_engine.data.validation.exceptions import DatasetValidationError, SchemaValidationError


@pytest.fixture
def validator():
    return ProductionDataValidator(dataset_version="test_v1", pipeline_version="test_1.0")


@pytest.fixture
def valid_raw_ohlc():
    dates = pd.date_range("2023-01-01", periods=3)
    return pd.DataFrame({
        "open": [100.0, 102.0, 104.0],
        "high": [105.0, 106.0, 108.0],
        "low": [98.0, 101.0, 103.0],
        "close": [102.0, 104.0, 106.0],
        "volume": [1000, 1500, 2000],
        "stock_splits": [0.0, 0.0, 0.0],
        "dividends": [0.0, 0.5, 0.0]
    }, index=dates)


def check_log_exists(report, substring: str, severity: str = None) -> bool:
    for log in report["logs"]:
        if severity and log["severity"] != severity:
            continue
        if substring.lower() in log["message"].lower():
            return True
    return False


def test_valid_dataset(validator, valid_raw_ohlc):
    passed, report = validator.validate(valid_raw_ohlc, "raw_ohlc")
    assert passed is True
    assert report["status"] == "PASSED"
    assert report["stats"]["rows_processed"] == 3


def test_empty_dataframe(validator):
    df = pd.DataFrame()
    passed, report = validator.validate(df, "raw_ohlc")
    assert passed is False
    assert check_log_exists(report, "empty")


def test_missing_columns(validator, valid_raw_ohlc):
    df = valid_raw_ohlc.drop(columns=["open"])
    passed, report = validator.validate(df, "raw_ohlc")
    assert passed is False
    assert check_log_exists(report, "missing")


def test_duplicate_timestamps(validator, valid_raw_ohlc):
    # Duplicate the last row exactly
    df = pd.concat([valid_raw_ohlc, valid_raw_ohlc.iloc[[-1]]])
    passed, report = validator.validate(df, "raw_ohlc")
    assert passed is False
    assert check_log_exists(report, "duplicate")
    assert report["stats"]["duplicate_rows"] == 1


def test_invalid_ohlc(validator, valid_raw_ohlc):
    df = valid_raw_ohlc.copy()
    df.iloc[0, df.columns.get_loc("high")] = 50.0  # High < Low (98.0)
    passed, report = validator.validate(df, "raw_ohlc")
    assert passed is False
    assert report["stats"]["ohlc_violations"] > 0
    
    # Negative close
    df2 = valid_raw_ohlc.copy()
    df2.iloc[0, df2.columns.get_loc("close")] = -10.0
    passed2, report2 = validator.validate(df2, "raw_ohlc")
    assert passed2 is False
    assert report2["stats"]["ohlc_violations"] > 0


def test_negative_volume(validator, valid_raw_ohlc):
    df = valid_raw_ohlc.copy()
    df.iloc[1, df.columns.get_loc("volume")] = -500
    passed, report = validator.validate(df, "raw_ohlc")
    assert passed is False
    assert check_log_exists(report, "negative volume")


def test_invalid_dividends(validator, valid_raw_ohlc):
    df = valid_raw_ohlc.copy()
    df.iloc[1, df.columns.get_loc("dividends")] = -0.5
    passed, report = validator.validate(df, "raw_ohlc")
    assert passed is False
    assert check_log_exists(report, "negative dividends")


def test_invalid_splits(validator, valid_raw_ohlc):
    df = valid_raw_ohlc.copy()
    df.iloc[1, df.columns.get_loc("stock_splits")] = -2.0
    passed, report = validator.validate(df, "raw_ohlc")
    assert passed is False
    assert check_log_exists(report, "negative stock splits")


def test_feature_nan_values(validator, valid_raw_ohlc):
    df = valid_raw_ohlc.copy()
    df["rsi"] = [np.nan, 50.0, 60.0]
    passed, report = validator.validate(df, "engineered_features")
    assert passed is False
    assert check_log_exists(report, "NaN values")


def test_feature_infinite_values(validator, valid_raw_ohlc):
    df = valid_raw_ohlc.copy()
    df["rsi"] = [np.inf, 50.0, 60.0]
    passed, report = validator.validate(df, "engineered_features")
    assert passed is False
    assert check_log_exists(report, "infinite")


def test_training_validation(validator, valid_raw_ohlc):
    df = valid_raw_ohlc.copy()
    
    # Missing target
    passed, report = validator.validate(df, "training")
    assert passed is False
    assert check_log_exists(report, "missing 'target'")
    
    # Valid target
    df["target"] = [1, 0, 1]
    passed2, report2 = validator.validate(df, "training")
    assert passed2 is True
    assert "target_balance" in report2["stats"]


def test_validation_report_generation(validator, valid_raw_ohlc):
    # Manually instantiate report and save
    validator.validate(valid_raw_ohlc, "raw_ohlc")
    from ml_engine.data.validation.reports import ValidationReport
    rep = ValidationReport("vtest", "1.0")
    rep.stats["rows_processed"] = 100
    rep.add_log("ERROR", "Test Error")
    rep.add_log("WARNING", "Test Warning")
    rep.finalize(False)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "report.json")
        md_path = os.path.join(tmpdir, "report.md")
        
        rep.save_json(json_path)
        rep.save_markdown(md_path)
        
        assert os.path.exists(json_path)
        assert os.path.exists(md_path)
        
        with open(md_path, "r") as f:
            content = f.read()
            assert "Test Error" in content
            assert "Test Warning" in content
