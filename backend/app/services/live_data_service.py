import pandas as pd
import yfinance as yf

class LiveDataService:

    def fetch(self, symbol: str):

        df = yf.download(
            symbol + ".NS",
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
            actions=True,
        )

        if len(df) < 60:
            raise ValueError(
                "Not enough market data."
            )

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        
        # Ensure corporate actions exist (mimicking training pipeline normalization)
        if "Dividends" not in df.columns:
            df["Dividends"] = 0.0
        if "Stock Splits" not in df.columns:
            df["Stock Splits"] = 0.0
        
        # Download market benchmarks for ML Engine
        nifty = yf.download(
            "^NSEI",
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )
        if isinstance(nifty.columns, pd.MultiIndex):
            nifty.columns = nifty.columns.get_level_values(0)
        nifty.index = pd.to_datetime(nifty.index, utc=True).tz_localize(None)
            
        vix = yf.download(
            "^INDIAVIX",
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )
        if isinstance(vix.columns, pd.MultiIndex):
            vix.columns = vix.columns.get_level_values(0)
        vix.index = pd.to_datetime(vix.index, utc=True).tz_localize(None)
            
        market_data = {
            "^NSEI": nifty,
            "^INDIAVIX": vix
        }

        latest = df.iloc[-1]
        
        latest_date_str = str(latest.name.date()) if hasattr(latest.name, 'date') else str(latest.name)

        latest_candle = {
            "date": latest_date_str,
            "open": float(latest["Open"]),
            "high": float(latest["High"]),
            "low": float(latest["Low"]),
            "close": float(latest["Close"]),
            "volume": float(latest["Volume"]),
        }

        return {
            "raw_df": df,
            "market_data": market_data,
            "latest_candle": latest_candle,
        }

live_data_service = LiveDataService()