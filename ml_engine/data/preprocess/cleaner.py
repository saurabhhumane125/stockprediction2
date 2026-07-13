import logging
import time
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ProductionCleaner:
    """
    Standardized preprocessing pipeline ensuring tabular data is clean,
    sorted, deduplicated, and robust to outliers/missing values.
    Never silently modifies data; every correction is logged.
    """

    def __init__(self, outlier_std_devs: float = 5.0):
        self.outlier_std_devs = outlier_std_devs

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute the full cleaning pipeline.
        
        Args:
            df (pd.DataFrame): Raw downloaded dataframe.
            
        Returns:
            pd.DataFrame: Cleaned dataframe.
        """
        if df.empty:
            logger.warning("Empty dataframe passed to Cleaner.")
            return df

        start_time = time.time()
        initial_rows = len(df)
        df_clean = df.copy()

        df_clean = self._normalize_index(df_clean)
        df_clean = self._remove_duplicates(df_clean)
        df_clean = self._sort_chronologically(df_clean)
        df_clean = self._normalize_types(df_clean)
        df_clean = self._handle_missing_values(df_clean)
        df_clean = self._detect_and_handle_outliers(df_clean)

        final_rows = len(df_clean)
        duration = time.time() - start_time
        logger.info(f"Cleaner finished in {duration:.4f}s. Input rows: {initial_rows}, Output rows: {final_rows}")
        
        return df_clean

    def _normalize_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure the index is a timezone-naive UTC datetime."""
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, utc=True)
            
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
            logger.info("Normalized index timezone to UTC-naive.")
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_count = len(df)
        df = df[~df.index.duplicated(keep="last")]
        removed = initial_count - len(df)
        if removed > 0:
            logger.warning(f"Removed {removed} duplicate rows by keeping the last observation.")
        return df

    def _sort_chronologically(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.index.is_monotonic_increasing:
            df = df.sort_index()
            logger.info("Sorted dataset chronologically.")
        return df

    def _normalize_types(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = ["open", "high", "low", "close", "volume", "dividends", "stock_splits"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        missing_count = df.isna().sum().sum()
        if missing_count > 0:
            # Forward fill prices, fill volume/actions with 0
            price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
            if price_cols:
                df[price_cols] = df[price_cols].ffill()
            
            if "volume" in df.columns:
                df["volume"] = df["volume"].fillna(0)
            if "dividends" in df.columns:
                df["dividends"] = df["dividends"].fillna(0.0)
            if "stock_splits" in df.columns:
                df["stock_splits"] = df["stock_splits"].fillna(0.0)
                
            # If the very first rows are still NaN (no previous data to ffill), drop them
            still_missing = df.isna().sum().sum()
            if still_missing > 0:
                initial = len(df)
                df = df.dropna()
                logger.warning(f"Dropped {initial - len(df)} leading rows due to unfillable NaNs.")
                
            logger.info(f"Handled {missing_count} missing values.")
        return df

    def _detect_and_handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        # Example naive outlier detection on returns
        if "close" in df.columns:
            returns = df["close"].pct_change().dropna()
            mean, std = returns.mean(), returns.std()
            outliers = np.abs((returns - mean) / std) > self.outlier_std_devs
            outlier_count = outliers.sum()
            if outlier_count > 0:
                logger.warning(f"Detected {outlier_count} potential extreme outliers (>{self.outlier_std_devs} std dev) in price returns.")
                # We log but do NOT silently modify/clip prices to preserve market crash reality, 
                # but this logic can be extended if configured.
        return df
