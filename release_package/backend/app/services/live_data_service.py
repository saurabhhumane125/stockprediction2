import numpy as np
import pandas as pd
import yfinance as yf

from ta.momentum import RSIIndicator, ROCIndicator
from ta.trend import ADXIndicator, EMAIndicator, MACD
from ta.volatility import AverageTrueRange, BollingerBands


class LiveDataService:

    def fetch(self, symbol: str):

        df = yf.download(
            symbol + ".NS",
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )

        if len(df) < 60:
            raise ValueError(
                "Not enough market data."
            )

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.reset_index(inplace=True)

        df["RSI"] = RSIIndicator(df["Close"]).rsi()

        df["MACD"] = MACD(df["Close"]).macd()

        df["EMA20"] = EMAIndicator(
            df["Close"],
            window=20,
        ).ema_indicator()

        df["EMA50"] = EMAIndicator(
            df["Close"],
            window=50,
        ).ema_indicator()

        df["ATR"] = AverageTrueRange(
            df["High"],
            df["Low"],
            df["Close"],
        ).average_true_range()

        df["ADX"] = ADXIndicator(
            df["High"],
            df["Low"],
            df["Close"],
        ).adx()

        bb = BollingerBands(df["Close"])

        df["BB_UPPER"] = bb.bollinger_hband()
        df["BB_LOWER"] = bb.bollinger_lband()
        df["BB_WIDTH"] = (
            df["BB_UPPER"] -
            df["BB_LOWER"]
        )

        df["ROC"] = ROCIndicator(
            df["Close"]
        ).roc()

        df["MOMENTUM"] = (
            df["Close"] -
            df["Close"].shift(10)
        )

        df["DAILY_RETURN"] = (
            df["Close"].pct_change()
        )

        df["VOLATILITY"] = (
            df["DAILY_RETURN"]
            .rolling(10)
            .std()
        )

        df["VOLUME_CHANGE"] = (
            df["Volume"]
            .pct_change()
        )

        # Match notebook preprocessing
        df = (
            df.replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .dropna()
            .reset_index(drop=True)
        )

        if len(df) < 48:
            raise ValueError(
                "Not enough valid rows after preprocessing."
            )

        feature_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "RSI",
            "MACD",
            "EMA20",
            "EMA50",
            "ATR",
            "ADX",
            "BB_UPPER",
            "BB_LOWER",
            "BB_WIDTH",
            "ROC",
            "MOMENTUM",
            "DAILY_RETURN",
            "VOLATILITY",
            "VOLUME_CHANGE",
        ]

        latest = df.iloc[-1]

        sequence = (
            df[
                feature_columns
            ]
            .tail(48)
            .values
            .tolist()
        )

        latest_features = {

            column: (
                float(latest[column])
                if pd.notna(latest[column])
                else None
            )

            for column in feature_columns

        }

        latest_candle = {

            "date": str(
                latest["Date"].date()
            ),

            "open": float(
                latest["Open"]
            ),

            "high": float(
                latest["High"]
            ),

            "low": float(
                latest["Low"]
            ),

            "close": float(
                latest["Close"]
            ),

            "volume": float(
                latest["Volume"]
            ),

        }

        return {

            "sequence": sequence,

            "latest_features": latest_features,

            "latest_candle": latest_candle,

        }


live_data_service = LiveDataService()