import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class FeatureGenerator:
    """
    Production Feature Engineering Pipeline.
    This serves as the single source of truth for all ML input features across 
    Training, Inference, Evaluation, and Vision AI.
    Calculations are strictly isolated into modular functions.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "RSI_PERIOD": 14,
            "MACD_FAST": 12,
            "MACD_SLOW": 26,
            "MACD_SIGNAL": 9,
            "EMA_SHORT": 20,
            "EMA_LONG": 50,
            "BB_PERIOD": 20,
            "BB_STD_DEV": 2.0,
            "ATR_PERIOD": 14,
            "ADX_PERIOD": 14,
            "ROC_PERIOD": 10,
            "MOMENTUM_PERIOD": 10,
            "VOLATILITY_PERIOD": 20,
        }
        self.metadata: List[Dict[str, Any]] = []

    def _register_metadata(self, name: str, desc: str, dtype: str, expected_range: str = "Any"):
        self.metadata.append({
            "feature_name": name,
            "description": desc,
            "data_type": dtype,
            "nullable": False,
            "expected_range": expected_range
        })

    def generate_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrator that applies all approved indicators in order.
        """
        logger.info("Starting feature generation pipeline.")
        start_time = time.time()
        
        df = df.copy()
        
        # Sequentially apply individual indicator functions
        df = self.add_daily_return(df)
        df = self.add_ema(df, self.config["EMA_SHORT"], "ema_short")
        df = self.add_ema(df, self.config["EMA_LONG"], "ema_long")
        df = self.add_rsi(df, self.config["RSI_PERIOD"])
        df = self.add_macd(df, self.config["MACD_FAST"], self.config["MACD_SLOW"], self.config["MACD_SIGNAL"])
        df = self.add_bollinger_bands(df, self.config["BB_PERIOD"], self.config["BB_STD_DEV"])
        df = self.add_atr(df, self.config["ATR_PERIOD"])
        df = self.add_adx(df, self.config["ADX_PERIOD"])
        df = self.add_roc(df, self.config["ROC_PERIOD"])
        df = self.add_momentum(df, self.config["MOMENTUM_PERIOD"])
        df = self.add_volatility(df, self.config["VOLATILITY_PERIOD"])
        df = self.add_volume_change(df)
        
        # Drop rows where features could not be calculated (NaNs due to lookback periods)
        initial_rows = len(df)
        df = df.dropna()
        dropped = initial_rows - len(df)
        if dropped > 0:
            logger.info(f"Dropped {dropped} rows due to feature generation lookback window NaNs.")
            
        duration = time.time() - start_time
        logger.info(f"Feature generation completed in {duration:.4f}s.")
        return df
        
    def add_daily_return(self, df: pd.DataFrame) -> pd.DataFrame:
        t0 = time.time()
        df["daily_return"] = df["close"].pct_change()
        self._register_metadata("daily_return", "Percentage change from previous close", "float64")
        logger.debug(f"add_daily_return took {time.time()-t0:.4f}s")
        return df

    def add_ema(self, df: pd.DataFrame, period: int, col_name: str) -> pd.DataFrame:
        t0 = time.time()
        df[col_name] = df["close"].ewm(span=period, adjust=False).mean()
        self._register_metadata(col_name, f"Exponential Moving Average (period={period})", "float64", "Positive")
        logger.debug(f"add_ema ({col_name}) took {time.time()-t0:.4f}s")
        return df

    def add_rsi(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        t0 = time.time()
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        # Handle edge case where loss is 0
        df["rsi"] = df["rsi"].fillna(100) 
        self._register_metadata("rsi", f"Relative Strength Index (period={period})", "float64", "[0, 100]")
        logger.debug(f"add_rsi took {time.time()-t0:.4f}s")
        return df

    def add_macd(self, df: pd.DataFrame, fast: int, slow: int, signal: int) -> pd.DataFrame:
        t0 = time.time()
        ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
        ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
        df["macd_line"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd_line"].ewm(span=signal, adjust=False).mean()
        df["macd_histogram"] = df["macd_line"] - df["macd_signal"]
        
        self._register_metadata("macd_line", "MACD Line", "float64")
        self._register_metadata("macd_signal", "MACD Signal Line", "float64")
        self._register_metadata("macd_histogram", "MACD Histogram", "float64")
        logger.debug(f"add_macd took {time.time()-t0:.4f}s")
        return df

    def add_bollinger_bands(self, df: pd.DataFrame, period: int, std_dev: float) -> pd.DataFrame:
        t0 = time.time()
        sma = df["close"].rolling(window=period).mean()
        std = df["close"].rolling(window=period).std()
        df["bb_upper"] = sma + (std * std_dev)
        df["bb_lower"] = sma - (std * std_dev)
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / sma
        
        self._register_metadata("bb_upper", "Bollinger Band Upper", "float64")
        self._register_metadata("bb_lower", "Bollinger Band Lower", "float64")
        self._register_metadata("bb_width", "Bollinger Band Width (Normalized)", "float64", "Positive")
        logger.debug(f"add_bollinger_bands took {time.time()-t0:.4f}s")
        return df

    def add_atr(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        t0 = time.time()
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift())
        low_close = np.abs(df["low"] - df["close"].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df["atr"] = true_range.rolling(window=period).mean()
        
        self._register_metadata("atr", f"Average True Range (period={period})", "float64", "Positive")
        logger.debug(f"add_atr took {time.time()-t0:.4f}s")
        return df

    def add_adx(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        t0 = time.time()
        # simplified ADX implementation for production robustness 
        # (A true Wilder's ADX uses Wilder's Smoothing, using standard rolling mean here for simplicity unless specified)
        up_move = df["high"] - df["high"].shift(1)
        down_move = df["low"].shift(1) - df["low"]
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        
        tr_series = df["high"] - df["low"] # Approximation for ATR denominator
        atr = tr_series.rolling(period).mean()
        
        plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(period).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(period).mean() / atr)
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df["adx"] = dx.rolling(period).mean()
        
        self._register_metadata("adx", f"Average Directional Index (period={period})", "float64", "[0, 100]")
        logger.debug(f"add_adx took {time.time()-t0:.4f}s")
        return df

    def add_roc(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        t0 = time.time()
        df["roc"] = df["close"].pct_change(periods=period) * 100
        self._register_metadata("roc", f"Rate of Change (period={period})", "float64")
        logger.debug(f"add_roc took {time.time()-t0:.4f}s")
        return df

    def add_momentum(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        t0 = time.time()
        df["momentum"] = df["close"] - df["close"].shift(period)
        self._register_metadata("momentum", f"Absolute Momentum (period={period})", "float64")
        logger.debug(f"add_momentum took {time.time()-t0:.4f}s")
        return df

    def add_volatility(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        t0 = time.time()
        if "daily_return" not in df.columns:
            df["daily_return"] = df["close"].pct_change()
        df["volatility"] = df["daily_return"].rolling(window=period).std() * np.sqrt(252) # Annualized
        self._register_metadata("volatility", f"Annualized Historical Volatility (period={period})", "float64", "Positive")
        logger.debug(f"add_volatility took {time.time()-t0:.4f}s")
        return df

    def add_volume_change(self, df: pd.DataFrame) -> pd.DataFrame:
        t0 = time.time()
        df["volume_change"] = df["volume"].pct_change()
        # Handle infinite volume changes if volume was 0
        df["volume_change"] = df["volume_change"].replace([np.inf, -np.inf], 0.0)
        self._register_metadata("volume_change", "Daily Volume Percentage Change", "float64")
        logger.debug(f"add_volume_change took {time.time()-t0:.4f}s")
        return df
