import logging
from typing import Optional
from app.schemas import ChartMetadata

logger = logging.getLogger(__name__)

class MetadataResolver:
    """
    Normalizes extracted OCR metadata (ChartMetadata) into standard formats
    suitable for market data providers (e.g. yfinance).
    """
    
    # Simple mapping of exchanges to Yahoo Finance suffixes
    EXCHANGE_SUFFIX_MAP = {
        "NSE": ".NS",
        "BSE": ".BO",
        "NASDAQ": "",
        "NYSE": "",
    }
    
    # Mapping of common timeframe strings
    TIMEFRAME_MAP = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "1H": "1h",
        "4h": "4h",
        "4H": "4h",
        "1d": "1d",
        "1D": "1d",
        "1w": "1wk",
        "1W": "1wk",
    }
    
    def resolve(self, metadata: ChartMetadata) -> ChartMetadata:
        """
        Normalizes the fields within ChartMetadata.
        Returns a new instance to avoid mutating the original OCR result.
        """
        resolved = ChartMetadata()
        
        # 1. Normalize Exchange
        exchange_suffix = ""
        if metadata.exchange and metadata.exchange.value:
            raw_exchange = metadata.exchange.value.upper()
            if raw_exchange in self.EXCHANGE_SUFFIX_MAP:
                exchange_suffix = self.EXCHANGE_SUFFIX_MAP[raw_exchange]
                resolved.exchange = metadata.exchange
                resolved.exchange.value = raw_exchange
            else:
                logger.warning(f"Unknown exchange: {raw_exchange}")
                resolved.exchange = metadata.exchange
                
        # 2. Normalize Symbol
        if metadata.symbol and metadata.symbol.value:
            raw_symbol = metadata.symbol.value.upper()
            
            # Prevent double suffixing
            if exchange_suffix and not raw_symbol.endswith(exchange_suffix):
                resolved_symbol = f"{raw_symbol}{exchange_suffix}"
            else:
                resolved_symbol = raw_symbol
                
            resolved.symbol = metadata.symbol
            resolved.symbol.value = resolved_symbol
            
        # 3. Normalize Timeframe
        if metadata.timeframe and metadata.timeframe.value:
            raw_tf = metadata.timeframe.value
            resolved_tf = self.TIMEFRAME_MAP.get(raw_tf, raw_tf)
            resolved.timeframe = metadata.timeframe
            resolved.timeframe.value = resolved_tf
            
        # 4. Copy over other fields as-is
        resolved.current_price = metadata.current_price
        resolved.timestamp = metadata.timestamp
        resolved.platform = metadata.platform
        
        return resolved

metadata_resolver = MetadataResolver()
