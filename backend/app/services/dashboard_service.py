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