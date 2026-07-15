from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd
from ml_engine.data.download.yfinance_downloader import YFinanceDownloader

class BaseMarketProvider(ABC):
    """Abstract interface for all Market Providers."""
    
    @abstractmethod
    def download(self, symbol: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        pass

class YFinanceProvider(BaseMarketProvider):
    """Adapter for YFinanceDownloader."""
    def __init__(self):
        self.downloader = YFinanceDownloader(timeout=10, max_retries=3)
        
    def download(self, symbol: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        return self.downloader.download(symbol, start_date, end_date, interval)

class MarketProviderRegistry:
    """Registry that holds active Market Providers."""
    
    def __init__(self):
        self._providers: Dict[str, BaseMarketProvider] = {}
        
    def register(self, name: str, provider: BaseMarketProvider) -> None:
        if name in self._providers:
            raise ValueError(f"Provider {name} is already registered.")
        self._providers[name] = provider
        
    def get_provider(self, name: str) -> BaseMarketProvider:
        if name not in self._providers:
            raise ValueError(f"Provider {name} not found in registry.")
        return self._providers[name]
        
    def get_default_provider_name(self) -> str:
        # Default to yfinance for now
        return "yfinance"

# Global singleton
provider_registry = MarketProviderRegistry()
provider_registry.register("yfinance", YFinanceProvider())
