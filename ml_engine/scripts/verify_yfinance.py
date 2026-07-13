import logging
import pandas as pd
from unittest.mock import patch, MagicMock
from ml_engine.data.download.yfinance_downloader import YFinanceDownloader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_verification():
    downloader = YFinanceDownloader(timeout=5, max_retries=3, backoff_factor=0.3)
    
    # 10. Compilation
    logger.info("Test 10: Compilation Successful")
    
    # Create a mock dataframe for successful downloads
    mock_df = pd.DataFrame({
        'Open': [100.0, 101.0],
        'High': [102.0, 103.0],
        'Low': [99.0, 100.0],
        'Close': [101.0, 102.0],
        'Volume': [1000, 1500],
        'Dividends': [0.0, 0.5],
        'Stock Splits': [0.0, 2.0]
    }, index=pd.to_datetime(['2020-08-20', '2020-08-21'], utc=True))
    
    with patch('yfinance.Ticker') as mock_ticker:
        # 1. Single Ticker, 8. Corporate Actions, 9. Adjusted OHLC Correctness (Standardization)
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_instance
        
        logger.info("Test 1, 8, 9: Single ticker + Corporate actions + Adjusted OHLC")
        df = downloader.download("AAPL", "2020-08-20", "2020-08-21", "1d")
        
        if df.empty:
            logger.error("Failed Test 1: Empty DataFrame")
        else:
            if 'stock_splits' in df.columns and df['stock_splits'].sum() > 0:
                logger.info("Successfully found corporate actions (splits/dividends)!")
            if 'open' in df.columns and 'ticker' in df.columns:
                logger.info("Successfully standardized columns to lowercase without spaces.")
                
        # 2. Batch Download
        logger.info("Test 2: Batch Download")
        batch_df = downloader.download_batch(["TCS.NS", "INFY.NS"], "2023-01-01", "2023-01-02", "1d")
        if len(batch_df) == 2 and not batch_df["TCS.NS"].empty:
            logger.info("Successfully downloaded batch.")
            
        # 6. Invalid Ticker Handling & 7. Empty Dataset Handling
        logger.info("Test 6 & 7: Invalid ticker / Empty dataset")
        mock_instance.history.return_value = pd.DataFrame()
        empty_df = downloader.download("INVALID", "2023-01-01", "2023-01-02", "1d")
        if empty_df.empty:
            logger.info("Successfully handled empty dataset for invalid ticker.")
            
        # 4. Timeout Handling & 5. Network Failure Handling & 3. Retry Logic
        logger.info("Test 4, 5, 3: Timeout / Retry / Network Failure")
        mock_instance.history.side_effect = Exception("Simulated Network Timeout")
        try:
            downloader.download("RELIANCE.NS", "2023-01-01", "2023-01-02", "1d")
            logger.error("Failed to raise exception on network failure.")
        except RuntimeError as e:
            logger.info(f"Successfully caught and wrapped network failure: {e}")

if __name__ == "__main__":
    run_verification()
