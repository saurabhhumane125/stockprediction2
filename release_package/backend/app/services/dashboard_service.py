from sqlalchemy.orm import Session

from app.models import (
    HistoricalPrice,
    News,
    PredictionHistory,
    Stock,
)
from app.services.recommendation_service import (
    recommendation_service,
)


class DashboardService:

    def _get_latest_features(self, db, stock_id: int):
        import pandas as pd
        import numpy as np
        from ta.momentum import RSIIndicator, ROCIndicator
        from ta.trend import ADXIndicator, EMAIndicator, MACD
        from ta.volatility import AverageTrueRange, BollingerBands

        prices = db.query(HistoricalPrice).filter(HistoricalPrice.stock_id == stock_id).order_by(HistoricalPrice.date.desc()).limit(100).all()
        if len(prices) < 60:
            return None

        prices.reverse()

        data = [{
            "Date": p.date,
            "Open": p.open_price,
            "High": p.high_price,
            "Low": p.low_price,
            "Close": p.close_price,
            "Volume": p.volume,
        } for p in prices]
        
        df = pd.DataFrame(data)
        
        df["RSI"] = RSIIndicator(df["Close"]).rsi()
        df["MACD"] = MACD(df["Close"]).macd()
        df["EMA20"] = EMAIndicator(df["Close"], window=20).ema_indicator()
        df["EMA50"] = EMAIndicator(df["Close"], window=50).ema_indicator()
        df["ATR"] = AverageTrueRange(df["High"], df["Low"], df["Close"]).average_true_range()
        df["ADX"] = ADXIndicator(df["High"], df["Low"], df["Close"]).adx()
        bb = BollingerBands(df["Close"])
        df["BB_UPPER"] = bb.bollinger_hband()
        df["BB_LOWER"] = bb.bollinger_lband()
        df["BB_WIDTH"] = df["BB_UPPER"] - df["BB_LOWER"]
        df["ROC"] = ROCIndicator(df["Close"]).roc()
        df["MOMENTUM"] = df["Close"] - df["Close"].shift(10)
        df["DAILY_RETURN"] = df["Close"].pct_change()
        df["VOLATILITY"] = df["DAILY_RETURN"].rolling(10).std()
        df["VOLUME_CHANGE"] = df["Volume"].pct_change()
        
        df = df.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
        if len(df) == 0:
            return None
            
        latest = df.iloc[-1]
        feature_columns = [
            "Open", "High", "Low", "Close", "Volume",
            "RSI", "MACD", "EMA20", "EMA50", "ATR", "ADX",
            "BB_UPPER", "BB_LOWER", "BB_WIDTH",
            "ROC", "MOMENTUM", "DAILY_RETURN", "VOLATILITY", "VOLUME_CHANGE"
        ]
        
        return {
            col: float(latest[col]) if pd.notna(latest[col]) else None
            for col in feature_columns
        }

    def get_dashboard(
        self,
        db: Session,
        symbol: str,
    ):

        stock = (
            db.query(Stock)
            .filter(
                Stock.symbol == symbol.upper()
            )
            .first()
        )

        if stock is None:
            return None

        latest_price = (
            db.query(HistoricalPrice)
            .filter(
                HistoricalPrice.stock_id == stock.id
            )
            .order_by(
                HistoricalPrice.date.desc()
            )
            .first()
        )

        latest_prediction = (
            db.query(PredictionHistory)
            .filter(
                PredictionHistory.stock_id == stock.id
            )
            .order_by(
                PredictionHistory.created_at.desc()
            )
            .first()
        )

        latest_news = (
            db.query(News)
            .filter(
                News.stock_id == stock.id
            )
            .order_by(
                News.published_at.desc()
            )
            .first()
        )

        recommendation = None
        latest_prediction_response = None

        if latest_prediction:

            latest_features = self._get_latest_features(db, stock.id)
            latest_candle = {
                "date": latest_price.date.strftime("%Y-%m-%d") if latest_price.date else "",
                "open": latest_price.open_price,
                "high": latest_price.high_price,
                "low": latest_price.low_price,
                "close": latest_price.close_price,
                "volume": latest_price.volume,
            } if latest_price else None

            explanation = None
            market_regime = None

            if latest_features:
                from app.services.explanation_service import explanation_service
                from app.services.market_regime_service import market_regime_service
                
                explanation = explanation_service.explain(latest_features)
                market_regime = market_regime_service.analyze(latest_features)

            fusion_result = {

                "prediction": latest_prediction.prediction,

                "confidence": latest_prediction.confidence,

                "sentiment": (
                    latest_news.sentiment.value
                    if latest_news
                    and latest_news.sentiment
                    else "NEUTRAL"
                ),

                "sentiment_score": (
                    float(latest_news.sentiment_score)
                    if latest_news
                    and latest_news.sentiment_score is not None
                    else 0.0
                ),

                "technical_signal": (
                    f"GRU model predicts "
                    f"{latest_prediction.prediction}"
                ),

                "news_signal": (
                    "Latest news sentiment available."
                    if latest_news
                    else "No recent news available."
                ),

                "final_reason": (
                    "Dashboard recommendation generated "
                    "from latest prediction and news."
                ),

                "class_id": None,

                "probability_buy": (
                    latest_prediction.probability_buy
                ),

                "probability_sell": (
                    latest_prediction.probability_sell
                ),
            }

            recommendation = (
                recommendation_service.generate(
                    fusion_result
                )
            )

            latest_prediction_response = {

                "prediction": (
                    latest_prediction.prediction
                ),

                "class_id": None,

                "confidence": (
                    latest_prediction.confidence
                ),

                "probability_buy": (
                    latest_prediction.probability_buy
                ),

                "probability_sell": (
                    latest_prediction.probability_sell
                ),

                "stock": stock.symbol,

                "sentiment": (
                    fusion_result["sentiment"]
                ),

                "sentiment_score": (
                    fusion_result["sentiment_score"]
                ),

                "technical_signal": (
                    fusion_result["technical_signal"]
                ),

                "news_signal": (
                    fusion_result["news_signal"]
                ),

                "final_reason": (
                    fusion_result["final_reason"]
                ),
                
                "latest_features": latest_features,
                "latest_candle": latest_candle,
                "explanation": explanation,
                "market_regime": market_regime,
            }

        return {

            "stock": stock,

            "latest_price": latest_price,

            "latest_prediction": (
                latest_prediction_response
            ),

            "recommendation": recommendation,
        }


dashboard_service = DashboardService()