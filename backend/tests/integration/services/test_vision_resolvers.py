import pytest
import pandas as pd
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.schemas import ChartMetadata, ExtractedField
from app.services.vision.metadata_resolver import metadata_resolver
from app.services.vision.ohlc_resolver import ohlc_resolver

def _f(val, conf=0.9, bbox=None):
    return ExtractedField(value=val, confidence=conf, bounding_box=bbox, source_engine="mock")

def test_metadata_resolver_valid():
    """Test valid metadata symbol normalization and field copying."""
    meta = ChartMetadata(
        symbol=_f("RELIANCE", 0.95, [0, 0, 10, 10]),
        exchange=_f("NSE", 0.9),
        timeframe=_f("1H"),
    )
    resolved = metadata_resolver.resolve(meta)
    
    assert resolved.symbol.value == "RELIANCE.NS"
    assert resolved.symbol.confidence == 0.95
    assert resolved.symbol.bounding_box == [0, 0, 10, 10]
    assert resolved.timeframe.value == "1h"
    assert resolved.exchange.value == "NSE"

def test_metadata_resolver_unknown_exchange():
    """Test unknown exchange defaults gracefully."""
    meta = ChartMetadata(
        symbol=_f("AAPL"),
        exchange=_f("UNKNOWN"),
    )
    resolved = metadata_resolver.resolve(meta)
    assert resolved.symbol.value == "AAPL" # No suffix added
    assert resolved.exchange.value == "UNKNOWN"

def test_metadata_resolver_missing_metadata():
    """Test missing metadata doesn't crash resolver."""
    meta = ChartMetadata()
    resolved = metadata_resolver.resolve(meta)
    assert resolved.symbol is None
    assert resolved.timeframe is None

@patch("ml_engine.data.download.yfinance_downloader.YFinanceDownloader.download")
def test_ohlc_resolver_valid(mock_download):
    """Test successful OHLC resolution."""
    # Mock YFinance returning data
    dates = pd.date_range("2026-07-10", periods=3, tz=None)
    mock_df = pd.DataFrame({
        "open": [10, 11, 12],
        "high": [15, 16, 17],
        "low": [5, 6, 7],
        "close": [12, 13, 14],
        "volume": [100, 200, 300],
    }, index=dates)
    
    mock_download.return_value = mock_df
    
    meta = ChartMetadata(
        symbol=_f("RELIANCE.NS"),
        timeframe=_f("1d"),
        timestamp=_f("2026-07-12T00:00:00Z") # Matches last row closely
    )
    
    ohlc = ohlc_resolver.resolve(meta)
    
    assert ohlc is not None
    assert ohlc.close == 14.0
    assert ohlc.volume == 300.0

@patch("ml_engine.data.download.yfinance_downloader.YFinanceDownloader.download")
def test_ohlc_resolver_weekend_handling(mock_download):
    """Test that if timestamp falls on a weekend, the previous Friday is fetched."""
    # Mock YFinance returning data only up to Friday (2026-07-10)
    dates = pd.date_range("2026-07-08", periods=3, tz=None) # Wed, Thu, Fri
    mock_df = pd.DataFrame({
        "open": [10, 11, 12],
        "high": [15, 16, 17],
        "low": [5, 6, 7],
        "close": [12, 13, 14],
        "volume": [100, 200, 300],
    }, index=dates)
    
    mock_download.return_value = mock_df
    
    # Requesting Sunday (2026-07-12)
    meta = ChartMetadata(
        symbol=_f("AAPL"),
        timeframe=_f("1d"),
        timestamp=_f("2026-07-12T12:00:00Z")
    )
    
    ohlc = ohlc_resolver.resolve(meta)
    
    assert ohlc is not None
    assert ohlc.close == 14.0 # Picks Friday's data
    assert ohlc.timestamp.startswith("2026-07-10")

def test_ohlc_resolver_missing_ticker():
    """Test OHLC resolver aborts without a symbol."""
    meta = ChartMetadata(timeframe=_f("1d"))
    ohlc = ohlc_resolver.resolve(meta)
    assert ohlc is None

@patch("ml_engine.data.download.yfinance_downloader.YFinanceDownloader.download")
def test_ohlc_resolver_empty_provider_response(mock_download):
    """Test provider returning empty dataframe."""
    mock_download.return_value = pd.DataFrame()
    
    meta = ChartMetadata(symbol=_f("INVALID"))
    ohlc = ohlc_resolver.resolve(meta)
    
    assert ohlc is None

@patch("ml_engine.data.download.yfinance_downloader.YFinanceDownloader.download")
def test_ohlc_resolver_provider_failure(mock_download):
    """Test provider throwing an exception."""
    mock_download.side_effect = RuntimeError("YFinance failed")
    
    meta = ChartMetadata(symbol=_f("AAPL"))
    ohlc = ohlc_resolver.resolve(meta)
    
    assert ohlc is None
