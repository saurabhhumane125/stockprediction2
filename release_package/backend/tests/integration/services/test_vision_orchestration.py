import pytest
from unittest.mock import patch
import pandas as pd

from app.schemas import OCRResult, ChartMetadata, ExtractedField
from app.services.vision.session_orchestrator import session_orchestrator

def _f(val, conf=0.9, bbox=None, src="tesseract_ltwh"):
    return ExtractedField(value=val, confidence=conf, bounding_box=bbox, source_engine=src)

@pytest.fixture
def valid_ocr_result():
    return OCRResult(
        success=True,
        confidence=0.95,
        metadata=ChartMetadata(
            symbol=_f("RELIANCE", 0.95, [10, 10, 50, 50]),
            timeframe=_f("1D", 0.95, [10, 60, 20, 20]),
            exchange=_f("NSE")
        ),
        raw_text="RELIANCE 1D NSE"
    )
    
@patch("ml_engine.data.download.yfinance_downloader.YFinanceDownloader.download")
def test_orchestrator_valid_session(mock_download, valid_ocr_result):
    dates = pd.date_range("2026-07-10", periods=1, tz=None)
    mock_df = pd.DataFrame({"open": [10], "high": [15], "low": [5], "close": [12], "volume": [100]}, index=dates)
    mock_download.return_value = mock_df
    
    session = session_orchestrator.create_session(valid_ocr_result, {"filename": "test.png"})
    
    assert session.validation_result.is_valid is True
    assert session.provider_used == "yfinance"
    assert session.resolved_ohlc is not None
    assert session.resolved_ohlc.close == 12.0
    
    # Check coordinate normalization
    # tesseract_ltwh: [10, 10, 50, 50] -> [10, 10, 10+50, 10+50] -> [10, 10, 60, 60]
    assert session.ocr_metadata.symbol.bounding_box == [10, 10, 60, 60]

def test_orchestrator_invalid_confidence():
    # Low confidence symbol
    res = OCRResult(
        success=True,
        confidence=0.9,
        metadata=ChartMetadata(
            symbol=_f("???", 0.3),
            timeframe=_f("1D")
        ),
        raw_text="???"
    )
    
    session = session_orchestrator.create_session(res, {"filename": "test.png"})
    
    assert session.validation_result.is_valid is False
    assert any("confidence" in e for e in session.validation_result.errors)
    assert session.resolved_ohlc is None

def test_orchestrator_missing_critical_field():
    res = OCRResult(
        success=True,
        confidence=0.9,
        metadata=ChartMetadata(
            timeframe=_f("1D")
        ),
        raw_text="1D"
    )
    
    session = session_orchestrator.create_session(res, {"filename": "test.png"})
    
    assert session.validation_result.is_valid is False
    assert any("missing" in e for e in session.validation_result.errors)

@patch("ml_engine.data.download.yfinance_downloader.YFinanceDownloader.download")
def test_orchestrator_provider_failure(mock_download, valid_ocr_result):
    mock_download.side_effect = Exception("API down")
    
    session = session_orchestrator.create_session(valid_ocr_result, {"filename": "test.png"})
    
    assert session.validation_result.is_valid is False
    assert session.resolved_ohlc is None
    assert any("OHLC Resolution returned empty data." in e for e in session.validation_result.errors)
