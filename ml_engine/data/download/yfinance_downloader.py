import logging
import time
import pandas as pd
import yfinance as yf
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Optional

from ml_engine.interfaces.base_downloader import BaseDownloader


logger = logging.getLogger(__name__)


class YFinanceDownloader(BaseDownloader):
    """
    Concrete implementation of BaseDownloader using Yahoo Finance (yfinance).
    Handles network retries, connection pooling, timeouts, and standardized extraction
    of adjusted OHLCV, splits, and dividends.
    """

    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 5,
        backoff_factor: float = 0.5,
    ):
        """
        Initialize the downloader with configurable networking policies.
        
        Args:
            timeout (int): Request timeout in seconds.
            max_retries (int): Maximum number of retry attempts for failed requests.
            backoff_factor (float): Multiplier for exponential backoff between retries.
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        # Configure connection reuse and exponential backoff
        self.session = Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def health_check(self) -> bool:
        """
        Verify if Yahoo Finance is accessible by fetching a lightweight ticker.
        """
        try:
            test_ticker = yf.Ticker("RELIANCE.NS", session=self.session)
            hist = test_ticker.history(period="1d", timeout=self.timeout)
            if not hist.empty:
                return True
            return False
        except Exception as e:
            logger.error(f"Health check failed for YFinanceDownloader: {e}")
            return False

    def _standardize_dataframe(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Internal method to enforce a standardized schema on the downloaded data.
        
        Args:
            df (pd.DataFrame): Raw yfinance dataframe.
            ticker (str): The ticker symbol.
            
        Returns:
            pd.DataFrame: Clean, standardized dataframe.
        """
        if df.empty:
            return pd.DataFrame()
            
        # yfinance returns tz-aware datetime index, usually localized to the exchange.
        # We convert it to UTC and strip timezone to prevent downstream merging issues.
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        
        # Ensure column names are standardized
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
        
        # We expect 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits'
        expected_cols = ["open", "high", "low", "close", "volume", "dividends", "stock_splits"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0.0 if col in ["dividends", "stock_splits"] else pd.NA
                
        # Drop any multi-level columns if they exist (happens in yf.download)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Add the ticker column for downstream grouping
        df["ticker"] = ticker
        
        # Keep only the requested standard columns
        df = df[expected_cols + ["ticker"]]
        
        return df

    def download(self, ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        """
        Download adjusted price and volume data for a specific ticker.
        """
        logger.info(f"Downloading {ticker} from {start_date} to {end_date} at {interval} interval.")
        
        try:
            yf_ticker = yf.Ticker(ticker, session=self.session)
            
            # yfinance history handles auto_adjust=True by default for OHLC
            # actions=True brings in dividends and splits
            df = yf_ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                actions=True,
                auto_adjust=True,
                timeout=self.timeout
            )
            
            if df.empty:
                logger.warning(f"Empty dataset returned for {ticker}.")
                return pd.DataFrame()
                
            standardized_df = self._standardize_dataframe(df, ticker)
            
            logger.debug(f"Successfully downloaded {len(standardized_df)} rows for {ticker}.")
            return standardized_df
            
        except Exception as e:
            logger.error(f"Failed to download {ticker}: {e}")
            raise RuntimeError(f"YFinance download failed for {ticker}") from e

    def download_batch(self, tickers: List[str], start_date: str, end_date: str, interval: str) -> Dict[str, pd.DataFrame]:
        """
        Download adjusted price and volume data for multiple tickers concurrently.
        """
        logger.info(f"Downloading batch of {len(tickers)} tickers from {start_date} to {end_date}.")
        
        results = {}
        for ticker in tickers:
            try:
                # To prevent hitting rate limits even with backoff, add a small sleep in batching
                time.sleep(0.5) 
                df = self.download(ticker, start_date, end_date, interval)
                results[ticker] = df
            except Exception as e:
                logger.error(f"Skipping {ticker} due to download error: {e}")
                results[ticker] = pd.DataFrame()
                
        return results
