from sqlalchemy.orm import Session

from app.models import (
    HistoricalPrice,
    PredictionHistory,
    Stock,
)


class EvaluationService:

    def evaluate(
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

        predictions = (
            db.query(PredictionHistory)
            .filter(
                PredictionHistory.stock_id == stock.id
            )
            .order_by(
                PredictionHistory.created_at.desc()
            )
            .all()
        )

        correct = 0
        total = 0

        for prediction in predictions:

            current_price = (
                db.query(HistoricalPrice)
                .filter(
                    HistoricalPrice.stock_id == stock.id,
                    HistoricalPrice.date >= prediction.created_at.date(),
                )
                .order_by(
                    HistoricalPrice.date.asc()
                )
                .first()
            )

            previous_price = (
                db.query(HistoricalPrice)
                .filter(
                    HistoricalPrice.stock_id == stock.id,
                    HistoricalPrice.date < prediction.created_at.date(),
                )
                .order_by(
                    HistoricalPrice.date.desc()
                )
                .first()
            )

            if (
                current_price is None
                or previous_price is None
            ):
                continue

            actual = (
                "BUY"
                if current_price.close_price
                > previous_price.close_price
                else "SELL"
            )

            total += 1

            if actual == prediction.prediction:
                correct += 1

        accuracy = 0.0

        if total > 0:
            accuracy = (
                correct / total
            ) * 100

        return {

            "stock": symbol.upper(),

            "total_predictions": total,

            "correct_predictions": correct,

            "accuracy": round(
                accuracy,
                2,
            ),
        }


evaluation_service = EvaluationService()