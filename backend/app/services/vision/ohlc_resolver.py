import logging
from datetime import datetime, timedelta, timezone
import pandas as pd
from typing import Optional

# Reuse provider registry
from app.services.vision.provider_registry import provider_registry
from app.services.vision.date_resolver import vision_date_resolver

from app.schemas import ChartMetadata, NormalizedOHLC

logger = logging.getLogger(__name__)

class OHLCResolver:
    """
    Coordinates with Market Data providers to reconstruct the exact OHLC
    candle corresponding to the OCR metadata. Uses VisionDateResolver
    to guarantee valid market download windows.
    """
    
    def __init__(self):
        pass
        
    def resolve(self, metadata: ChartMetadata) -> Optional[NormalizedOHLC]:
        """
        Resolves NormalizedOHLC from ChartMetadata.
        """
        if not metadata.symbol or not metadata.symbol.value:
            logger.error("Cannot resolve OHLC: Missing symbol.")
            return None
            
        ticker = metadata.symbol.value
        
        # Default to 1d if timeframe missing
        interval = "1d"
        if metadata.timeframe and metadata.timeframe.value:
            interval = metadata.timeframe.value
            
        # Determine the target timestamp
        target_dt = datetime.now(timezone.utc)
        if metadata.timestamp and metadata.timestamp.value:
            try:
                target_dt = datetime.fromisoformat(metadata.timestamp.value.replace("Z", "+00:00"))
            except ValueError:
                logger.warning(f"Invalid timestamp format: {metadata.timestamp.value}. Using current time.")
                
        # Use VisionDateResolver as the single source of truth for market windows
        date_window = vision_date_resolver.resolve(target_dt, interval)
        for warning in date_window.warnings:
            logger.warning(f"DateResolver Warning: {warning}")
            
        # Also update the metadata timeframe if the resolver escalated it
        if metadata.timeframe and metadata.timeframe.value != date_window.interval:
            metadata.timeframe.value = date_window.interval
        
        try:
            provider_name = provider_registry.get_default_provider_name()
            provider = provider_registry.get_provider(provider_name)
            df = provider.download(
                ticker, 
                date_window.start_date, 
                date_window.end_date, 
                date_window.interval
            )
            
            if df.empty:
                logger.warning(f"Provider returned empty data for {ticker}.")
                return None
                
            # Filter to find the closest candle
            # df index is timezone naive UTC based on standardize_dataframe
            target_dt_naive = date_window.target_dt.replace(tzinfo=None)
            
            # Find exact match or closest previous candle
            past_data = df[df.index <= target_dt_naive]
            
            if past_data.empty:
                # If no past data, just take the first available
                closest_row = df.iloc[0]
                resolved_time = df.index[0]
            else:
                closest_row = past_data.iloc[-1]
                resolved_time = past_data.index[-1]
                
            ohlc = NormalizedOHLC(
                open=float(closest_row["open"]),
                high=float(closest_row["high"]),
                low=float(closest_row["low"]),
                close=float(closest_row["close"]),
                volume=float(closest_row["volume"]),
                timestamp=resolved_time.isoformat() + "Z"
            )
            
            return ohlc
            
        except Exception as e:
            logger.error(f"Provider failure during OHLC resolution: {e}")
            return None

ohlc_resolver = OHLCResolver()
