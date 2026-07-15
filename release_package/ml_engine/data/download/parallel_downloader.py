"""
ml_engine/data/download/parallel_downloader.py
─────────────────────────────────────────────────────────────────────────────
Parallel download engine orchestrating the YFinanceDownloader.
─────────────────────────────────────────────────────────────────────────────
"""
import concurrent.futures
import logging
import random
import time
from typing import Dict, List, Optional, Tuple
import pandas as pd

from ml_engine.data.download.yfinance_downloader import YFinanceDownloader

logger = logging.getLogger(__name__)


class ParallelDownloadEngine:
    """
    Downloads historical data for multiple tickers in parallel using a thread pool.
    Implements jittered exponential backoff and connection pooling wrappers.
    """
    def __init__(self, max_workers: int = 5, timeout: int = 15, max_retries: int = 3):
        self.max_workers = max_workers
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Instantiate base downloader
        self.base_downloader = YFinanceDownloader(
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=1.0
        )

    def download_parallel(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Download multiple tickers concurrently.
        
        Args:
            tickers: List of ticker symbols.
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            interval: Data interval
            
        Returns:
            Dict mapping ticker to its DataFrame. Failed downloads have empty DataFrames.
        """
        logger.info(f"[ParallelDownloader] Starting batch download for {len(tickers)} tickers "
                    f"using {self.max_workers} workers.")
        
        results: Dict[str, pd.DataFrame] = {}
        
        def _fetch(ticker: str) -> Tuple[str, pd.DataFrame]:
            # Jitter to avoid thunder-herd on the API
            time.sleep(random.uniform(0.1, 1.5))
            
            for attempt in range(1, self.max_retries + 1):
                try:
                    df = self.base_downloader.download(ticker, start_date, end_date, interval)
                    return ticker, df
                except Exception as e:
                    if attempt == self.max_retries:
                        logger.error(f"[ParallelDownloader] Failed {ticker} after {self.max_retries} attempts: {e}")
                        return ticker, pd.DataFrame()
                    
                    backoff = (2 ** attempt) + random.uniform(0.1, 1.0)
                    logger.warning(f"[ParallelDownloader] Attempt {attempt} failed for {ticker}. "
                                   f"Retrying in {backoff:.1f}s")
                    time.sleep(backoff)
            
            return ticker, pd.DataFrame()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ticker = {executor.submit(_fetch, t): t for t in tickers}
            
            for future in concurrent.futures.as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    t, df = future.result()
                    results[t] = df
                    if not df.empty:
                        logger.debug(f"[ParallelDownloader] {ticker}: {len(df)} rows downloaded.")
                    else:
                        logger.warning(f"[ParallelDownloader] {ticker}: Returned empty DataFrame.")
                except Exception as e:
                    logger.error(f"[ParallelDownloader] Unhandled exception for {ticker}: {e}")
                    results[ticker] = pd.DataFrame()

        successful = sum(1 for df in results.values() if not df.empty)
        logger.info(f"[ParallelDownloader] Completed batch download. {successful}/{len(tickers)} successful.")
        
        return results
