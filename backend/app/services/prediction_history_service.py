from sqlalchemy.orm import Session

from app.models import (
    HistoricalPrice,
    PredictionHistory,
    Stock,
)


class PredictionHistoryService:

    def save_prediction(
        self,
        db: Session,
        symbol: str,
        prediction: str,
        confidence: float,
        probability_buy: float,
        probability_sell: float,
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

        if latest_price is None:
            return None

        existing_prediction = (

            db.query(PredictionHistory)

            .filter(
                PredictionHistory.stock_id == stock.id,
                PredictionHistory.prediction_date == latest_price.date,
            )

            .first()

        )

        if existing_prediction:

            return existing_prediction

        history = PredictionHistory(

            stock_id=stock.id,

            prediction=prediction,

            confidence=confidence,

            probability_buy=probability_buy,

            probability_sell=probability_sell,

            prediction_date=latest_price.date,

            evaluation_date=None,

            status="PENDING",

            entry_price=latest_price.close_price,

            evaluated_price=None,

            actual_prediction=None,

            is_correct=None,
        )

        db.add(history)

        db.commit()

        db.refresh(history)

        return history


prediction_history_service = PredictionHistoryService()