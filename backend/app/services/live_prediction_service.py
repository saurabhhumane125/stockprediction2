from sqlalchemy.orm import Session

from app.core.logger import logger

from app.services.market_regime_service import (
    market_regime_service,
)


from app.services.explanation_service import (
    explanation_service,
)
from app.models import (
    News,
    Stock,
)
from app.services.fusion_service import (
    fusion_service,
)
from app.services.live_data_service import (
    live_data_service,
)
from app.services.news_service import (
    news_service,
)
from app.services.prediction_history_service import (
    prediction_history_service,
)
from app.services.prediction_service import (
    prediction_service,
)


class LivePredictionService:

    def predict(
        self,
        db: Session,
        stock: str,
        sync_news: bool = True,
    ):

        market_data_payload = live_data_service.fetch(
            stock,
        )

        raw_df = market_data_payload[
            "raw_df"
        ]

        market_data = market_data_payload[
            "market_data"
        ]

        latest_candle = market_data_payload[
            "latest_candle"
        ]

        prediction = prediction_service.predict(
            stock=stock,
            raw_df=raw_df,
            market_data=market_data,
        )

        # Extract latest_features from prediction payload for downstream services
        latest_features = prediction.get("latest_features")
        if not latest_features:
            raise RuntimeError("Live prediction failed to produce latest_features.")

        if sync_news:
            try:
                news_service.sync_news(
                    db=db,
                    symbol=stock,
                )
            except Exception as e:
                logger.exception("Failed to sync news for %s", stock)

        latest_news = (

            db.query(News)

            .join(Stock)

            .filter(
                Stock.symbol == stock.upper()
            )

            .order_by(
                News.published_at.desc()
            )

            .first()

        )

        result = None
        if latest_news:
            sentiment = {
                "sentiment": latest_news.sentiment,
                "score": latest_news.sentiment_score,
            }
            try:
                result = fusion_service.fuse(
                    prediction,
                    sentiment,
                )
            except Exception as e:
                logger.exception("Failed to fuse sentiment for %s", stock)

        if result is None:
            result = {
                "prediction": prediction["prediction"],
                "confidence": prediction["confidence"],
                "sentiment": None,
                "sentiment_score": None,
                "technical_signal": "GRU model prediction only.",
                "news_signal": "No recent news available." if not latest_news else "Sentiment fusion failed.",
                "final_reason": "Prediction generated without news sentiment.",
            }
        
        result["latest_features"] = latest_features

        result["latest_candle"] = latest_candle

        try:
            result["explanation"] = explanation_service.explain(
                latest_features
            )
        except Exception as e:
            logger.exception("Failed to generate explanation for %s", stock)
            result["explanation"] = None

        try:
            result["market_regime"] = market_regime_service.analyze(
                latest_features
            )
        except Exception as e:
            logger.exception("Failed to analyze market regime for %s", stock)
            result["market_regime"] = None

        result["stock"] = stock.upper()

        result["class_id"] = prediction["class_id"]

        result["probability_buy"] = prediction["probability_buy"]

        result["probability_sell"] = prediction["probability_sell"]

        try:
            prediction_history_service.save_prediction(
                db=db,
                symbol=stock.upper(),
                prediction=result["prediction"],
                confidence=result["confidence"],
                probability_buy=result["probability_buy"],
                probability_sell=result["probability_sell"],
            )
        except Exception as e:
            logger.exception("Failed to save prediction history for %s", stock)

        return result


live_prediction_service = LivePredictionService()