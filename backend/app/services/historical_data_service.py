from sqlalchemy.orm import Session
import yfinance as yf
import pandas as pd

from app.models import HistoricalPrice, Stock


class HistoricalDataService:

    def sync_stock(
        self,
        db: Session,
        symbol: str,
        period: str = "5y",
    ):

        stock = (
            db.query(Stock)
            .filter(Stock.symbol == symbol)
            .first()
        )

        if stock is None:
            raise ValueError(f"{symbol} not found.")

        df = yf.download(
            symbol + ".NS",
            period=period,
            interval="1d",
            auto_adjust=True,
            progress=False,
        )

        if df.empty:
            raise ValueError("No market data received.")

        # Production-safe for latest yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        for _, row in df.iterrows():

            exists = (
                db.query(HistoricalPrice)
                .filter(
                    HistoricalPrice.stock_id == stock.id,
                    HistoricalPrice.date == row["Date"].date(),
                )
                .first()
            )

            if exists:
                continue

            db.add(
                HistoricalPrice(
                    stock_id=stock.id,
                    date=row["Date"].date(),
                    open_price=float(row["Open"]),
                    high_price=float(row["High"]),
                    low_price=float(row["Low"]),
                    close_price=float(row["Close"]),
                    volume=float(row["Volume"]),
                )
            )

        db.commit()


historical_data_service = HistoricalDataService()