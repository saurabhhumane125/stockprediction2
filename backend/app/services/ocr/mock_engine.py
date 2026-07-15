from app.services.ocr.engine_interface import BaseOCREngine
from app.schemas import OCRResult, ChartMetadata, ExtractedField
from datetime import datetime, timedelta, timezone

def _f(val, conf=0.9):
    return ExtractedField(value=val, confidence=conf, source_engine="mock")

class MockEngine(BaseOCREngine):
    """
    Deterministic mock engine for robust integration testing.
    Responds to specific filename keywords to simulate edge cases.
    """
    
    def extract(self, image_path: str) -> OCRResult:
        path_lower = image_path.lower()
        
        if "corrupted" in path_lower:
            return OCRResult(
                success=False,
                confidence=0.0,
                metadata=ChartMetadata(),
                raw_text="",
                error="Failed to decode image data"
            )
            
        if "ocr_failure" in path_lower:
            return OCRResult(
                success=False,
                confidence=0.0,
                metadata=ChartMetadata(),
                raw_text="",
                error="Engine completely failed to read text"
            )
            
        if "unsupported_platform" in path_lower:
            return OCRResult(
                success=True,
                confidence=0.9,
                metadata=ChartMetadata(
                    symbol=_f("AAPL"),
                    exchange=_f("NASDAQ"),
                    platform=_f("UNKNOWN_APP")
                ),
                raw_text="AAPL 150.00",
                error=None
            )
            
        if "low_confidence" in path_lower:
            return OCRResult(
                success=True,
                confidence=0.3,
                metadata=ChartMetadata(
                    symbol=_f("???", 0.2),
                    current_price=_f(10.0, 0.3)
                ),
                raw_text="??? 10.0",
                error="Low confidence extraction"
            )
            
        if "missing_ticker" in path_lower:
            return OCRResult(
                success=True,
                confidence=0.8,
                metadata=ChartMetadata(
                    timeframe=_f("1D"),
                    current_price=_f(250.0),
                    platform=_f("TradingView")
                ),
                raw_text="1D 250.00 TradingView",
                error=None
            )
            
        if "missing_timeframe" in path_lower:
            return OCRResult(
                success=True,
                confidence=0.8,
                metadata=ChartMetadata(
                    symbol=_f("TSLA"),
                    exchange=_f("NASDAQ"),
                    current_price=_f(250.0),
                    platform=_f("TradingView")
                ),
                raw_text="TSLA NASDAQ 250.00 TradingView",
                error=None
            )
            
        # Use a hardcoded safe past timestamp and a 1d timeframe to guarantee
        # yfinance resolution without hitting the 60-day limit for 15m intraday data.
        safe_dt = "2024-01-10T10:00:00Z"
        
        # Default valid case
        return OCRResult(
            success=True,
            confidence=0.95,
            metadata=ChartMetadata(
                symbol=_f("RELIANCE.NS"),
                exchange=_f("NSE"),
                timeframe=_f("1d"),
                current_price=_f(2950.0),
                timestamp=_f(safe_dt),
                platform=_f("TradingView")
            ),
            raw_text=f"RELIANCE NSE 1d 2950.0 {safe_dt} TradingView",
            error=None
        )
