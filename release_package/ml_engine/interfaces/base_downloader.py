from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict


class BaseDownloader(ABC):
    """
    Abstract interface for acquiring historical market data.
    Ensures provider-agnostic implementation for downloading financial time-series data.
    Allows seamlessly swapping providers (Yahoo Finance, NSE, Polygon, or Vision AI).
    """

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify if the underlying data provider is available and accessible.
        
        Returns:
            bool: True if the provider is healthy, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def download(self, ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        """
        Download adjusted price and volume data for a specific ticker.
        
        Args:
            ticker (str): The unique identifier for the asset.
            start_date (str): The start date for the data range (YYYY-MM-DD).
            end_date (str): The end date for the data range (YYYY-MM-DD).
            interval (str): The timeframe interval (e.g., '1m', '1h', '1d', '1wk').
            
        Returns:
            pd.DataFrame: Tabular data containing time-series records.
            
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def download_batch(self, tickers: List[str], start_date: str, end_date: str, interval: str) -> Dict[str, pd.DataFrame]:
        """
        Download adjusted price and volume data for multiple tickers concurrently.
        
        Args:
            tickers (List[str]): A list of unique identifiers for the assets.
            start_date (str): The start date for the data range (YYYY-MM-DD).
            end_date (str): The end date for the data range (YYYY-MM-DD).
            interval (str): The timeframe interval (e.g., '1m', '1h', '1d', '1wk').
            
        Returns:
            Dict[str, pd.DataFrame]: A mapping of tickers to their respective tabular data.
            
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
