import logging
import time
import pandas as pd
import yfinance as yf
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class YFinanceDownloader:
    def __init__(self):
        self.session = Session()
        self.timeout = 10
        retry_strategy = Retry(total=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _standardize_dataframe(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        print(f"[Stage 2] Entering _standardize_dataframe")
        print(f"[Stage 2] Initial shape: {df.shape}")
        
        if df.empty:
            return pd.DataFrame()
            
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        print(f"[Stage 2] After tz_localize(None) shape: {df.shape}")
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        print(f"[Stage 2] After flatten MultiIndex shape: {df.shape}, columns: {df.columns.tolist()}")

        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
        print(f"[Stage 2] After rename/lower shape: {df.shape}, columns: {df.columns.tolist()}")
        
        expected_cols = ["open", "high", "low", "close", "volume", "dividends", "stock_splits"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0.0 if col in ["dividends", "stock_splits"] else pd.NA
        print(f"[Stage 2] After expected_cols mapping shape: {df.shape}")
            
        df["ticker"] = ticker
        
        df = df[expected_cols + ["ticker"]]
        print(f"[Stage 2] After subsetting expected_cols shape: {df.shape}")
        
        return df

    def download(self, ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        print(f"\n[Stage 1] Executing yf.Ticker('{ticker}').history(start='{start_date}', end='{end_date}', interval='{interval}')")
        yf_ticker = yf.Ticker(ticker)
        df = yf_ticker.history(
            start=start_date,
            end=end_date,
            interval=interval,
            actions=True,
            auto_adjust=True,
            timeout=self.timeout
        )
        print(f"[Stage 1] yf.history() returned shape: {df.shape}")
        print(f"[Stage 1] columns: {df.columns}")
        print(f"[Stage 1] head: \n{df.head(3)}")
        print(f"[Stage 1] tail: \n{df.tail(3)}")
        
        if df.empty:
            print("[Stage 1] DF is empty!")
            return pd.DataFrame()
            
        standardized_df = self._standardize_dataframe(df, ticker)
        print(f"[Stage 1] Final standardized shape: {standardized_df.shape}")
        return standardized_df

if __name__ == "__main__":
    d = YFinanceDownloader()
    df = d.download("RELIANCE.NS", "2023-08-11", "2024-01-12", "1d")
    print(f"\n[Trace Result] Final shape: {df.shape}")
