from sqlalchemy.orm import Session

from app.models import (
    PredictionHistory,
    Stock,
)


class BacktestingService:

    def summary(
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

        total_predictions = len(
            predictions
        )

        evaluated = [
            p
            for p in predictions
            if p.is_correct is not None
        ]

        pending = (
            total_predictions
            - len(evaluated)
        )

        wins = sum(
            1
            for p in evaluated
            if p.is_correct
        )

        losses = (
            len(evaluated)
            - wins
        )

        accuracy = (
            (wins / len(evaluated)) * 100
            if evaluated
            else 0.0
        )

        average_confidence = (
            sum(
                p.confidence
                for p in predictions
            )
            / total_predictions
            if total_predictions
            else 0.0
        )

        win_rate = (
            (wins / len(evaluated)) * 100
            if evaluated
            else 0.0
        )

        loss_rate = (
            (losses / len(evaluated)) * 100
            if evaluated
            else 0.0
        )

        latest_prediction = None

        if predictions:

            latest_prediction = {

                "prediction": (
                    predictions[0].prediction
                ),

                "confidence": (
                    predictions[0].confidence
                ),

                "created_at": (
                    predictions[0].created_at
                ),

                "is_correct": (
                    predictions[0].is_correct
                ),
            }

        return {

            "stock": stock.symbol,

            "total_predictions": (
                total_predictions
            ),

            "evaluated_predictions": (
                len(evaluated)
            ),

            "pending_predictions": (
                pending
            ),

            "wins": wins,

            "losses": losses,

            "accuracy": round(
                accuracy,
                2,
            ),

            "win_rate": round(
                win_rate,
                2,
            ),

            "loss_rate": round(
                loss_rate,
                2,
            ),

            "average_confidence": round(
                average_confidence,
                4,
            ),

            "latest_prediction": (
                latest_prediction
            ),
        }


backtesting_service = BacktestingService()