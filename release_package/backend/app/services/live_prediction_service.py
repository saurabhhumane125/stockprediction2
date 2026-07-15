from sqlalchemy.orm import Session

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

        market_data = live_data_service.fetch(
            stock,
        )

        sequence = market_data[
            "sequence"
        ]

        latest_features = market_data[
            "latest_features"
        ]

        latest_candle = market_data[
            "latest_candle"
        ]

        prediction = prediction_service.predict(
            stock=stock,
            feature_rows=sequence,
        )

        if sync_news:

            news_service.sync_news(
                db=db,
                symbol=stock,
            )

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

        if latest_news:

            sentiment = {

                "sentiment": latest_news.sentiment,

                "score": latest_news.sentiment_score,

            }

            result = fusion_service.fuse(
                prediction,
                sentiment,
            )

        else:

            result = {

                "prediction": prediction["prediction"],

                "confidence": prediction["confidence"],

                "sentiment": None,

                "sentiment_score": None,

                "technical_signal": "GRU model prediction only.",

                "news_signal": "No recent news available.",

                "final_reason": "Prediction generated without news sentiment.",

            }
        
        result["latest_features"] = latest_features

        result["latest_candle"] = latest_candle

        result["explanation"] = (
            explanation_service.explain(
                latest_features
            )
        )

        result["market_regime"] = (
            market_regime_service.analyze(
                latest_features
            )
        )

        result["stock"] = stock.upper()

        result["class_id"] = prediction["class_id"]

        result["probability_buy"] = prediction["probability_buy"]

        result["probability_sell"] = prediction["probability_sell"]

        prediction_history_service.save_prediction(

            db=db,

            symbol=stock.upper(),

            prediction=result["prediction"],

            confidence=result["confidence"],

            probability_buy=result["probability_buy"],

            probability_sell=result["probability_sell"],

        )

        return result


live_prediction_service = LivePredictionService()