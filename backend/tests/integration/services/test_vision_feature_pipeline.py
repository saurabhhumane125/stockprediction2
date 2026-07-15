import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

from app.schemas import VisionSession, ChartMetadata, ExtractedField, NormalizedOHLC, ValidationResult
from app.services.vision.feature_pipeline import feature_pipeline

def test_feature_pipeline_no_ohlc():
    session = VisionSession(
        request_id="test1",
        upload_metadata={},
        ocr_metadata=ChartMetadata(),
        validation_result=ValidationResult(is_valid=True),
        processing_time_ms=10.0,
        resolved_ohlc=None
    )
    
    result = feature_pipeline.process(session)
    assert result.is_valid is False
    assert "no resolved_ohlc" in result.warnings[0]
    
@patch("ml_engine.data.download.yfinance_downloader.YFinanceDownloader.download")
def test_feature_pipeline_valid(mock_download):
    np.random.seed(42)
    dates = pd.date_range("2026-01-01", periods=150, tz=None)
    data = {
        "open": np.random.uniform(10, 20, 150),
        "high": np.random.uniform(20, 25, 150),
        "low": np.random.uniform(5, 10, 150),
        "close": np.random.uniform(10, 20, 150),
        "volume": np.random.uniform(1000, 5000, 150)
    }
    df = pd.DataFrame(data, index=dates)
    mock_download.return_value = df
    
    # We choose a target timestamp that allows exactly required_rows (49) backwards
    # 2026-01-01 + 140 days = 2026-05-21
    target_dt = "2026-05-21T00:00:00"
    
    session = VisionSession(
        request_id="test2",
        upload_metadata={},
        ocr_metadata=ChartMetadata(symbol=ExtractedField(value="RELIANCE", confidence=1.0, source_engine="test")),
        resolved_ohlc=NormalizedOHLC(open=15, high=22, low=8, close=18, volume=2000, timestamp=target_dt),
        provider_used="yfinance",
        validation_result=ValidationResult(is_valid=True),
        processing_time_ms=10.0
    )
    
    result = feature_pipeline.process(session)
    assert result.is_valid is True
    assert len(result.features) == feature_pipeline.sequence_length + 1
    assert result.feature_hash != ""
    assert len(result.provenance) > 0
    assert result.provenance[0].feature_name in result.feature_names

@patch("ml_engine.data.download.yfinance_downloader.YFinanceDownloader.download")
def test_feature_pipeline_insufficient_data(mock_download):
    # Only 30 days of data provided, not enough for lookbacks or sequences
    dates = pd.date_range("2026-01-01", periods=30, tz=None)
    data = {
        "open": np.random.uniform(10, 20, 30),
        "high": np.random.uniform(20, 25, 30),
        "low": np.random.uniform(5, 10, 30),
        "close": np.random.uniform(10, 20, 30),
        "volume": np.random.uniform(1000, 5000, 30)
    }
    df = pd.DataFrame(data, index=dates)
    mock_download.return_value = df
    
    target_dt = "2026-01-20T00:00:00"
    
    session = VisionSession(
        request_id="test3",
        upload_metadata={},
        ocr_metadata=ChartMetadata(symbol=ExtractedField(value="RELIANCE", confidence=1.0, source_engine="test")),
        resolved_ohlc=NormalizedOHLC(open=15, high=22, low=8, close=18, volume=2000, timestamp=target_dt),
        provider_used="yfinance",
        validation_result=ValidationResult(is_valid=True),
        processing_time_ms=10.0
    )
    
    result = feature_pipeline.process(session)
    assert result.is_valid is False
    assert any("Insufficient rows" in w or "was lost after feature generation" in w for w in result.warnings)
