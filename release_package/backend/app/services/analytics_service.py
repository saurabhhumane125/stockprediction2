from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import PredictionHistory


class AnalyticsService:
    """
    Production analytics service.

    This service contains ONLY business logic.

    It never raises HTTP exceptions.
    It never imports FastAPI.

    Every method returns plain Python dictionaries
    that can be reused by APIs, dashboards,
    recommendation engine and future services.
    """

    def get_overview(
        self,
        db: Session,
    ) -> dict:

        total_predictions = db.query(
            PredictionHistory
        ).count()

        pending_predictions = (
            db.query(PredictionHistory)
            .filter(
                PredictionHistory.status == "PENDING"
            )
            .count()
        )

        completed_predictions = (
            db.query(PredictionHistory)
            .filter(
                PredictionHistory.status == "COMPLETED"
            )
            .count()
        )

        correct_predictions = (
            db.query(PredictionHistory)
            .filter(
                PredictionHistory.is_correct == 1
            )
            .count()
        )

        incorrect_predictions = (
            db.query(PredictionHistory)
            .filter(
                PredictionHistory.is_correct == 0
            )
            .count()
        )

        accuracy = 0.0

        if completed_predictions > 0:

            accuracy = round(
                (
                    correct_predictions
                    / completed_predictions
                )
                * 100,
                2,
            )

        return {

            "total_predictions":
                total_predictions,

            "pending_predictions":
                pending_predictions,

            "completed_predictions":
                completed_predictions,

            "correct_predictions":
                correct_predictions,

            "incorrect_predictions":
                incorrect_predictions,

            "accuracy":
                accuracy,
        }

    def get_recent_predictions(
        self,
        db: Session,
        limit: int = 20,
    ) -> list:

        rows = (

            db.query(PredictionHistory)

            .order_by(
                PredictionHistory.created_at.desc()
            )

            .limit(limit)

            .all()

        )

        return [

            {

                "id": row.id,

                "stock_id": row.stock_id,

                "prediction": row.prediction,

                "status": row.status,

                "confidence": row.confidence,

                "prediction_date":
                    row.prediction_date,

                "created_at":
                    row.created_at,

            }

            for row in rows

        ]

    def get_prediction_distribution(
        self,
        db: Session,
    ) -> dict:

        buy_count = (

            db.query(PredictionHistory)

            .filter(
                PredictionHistory.prediction == "BUY"
            )

            .count()

        )

        sell_count = (

            db.query(PredictionHistory)

            .filter(
                PredictionHistory.prediction == "SELL"
            )

            .count()

        )

        return {

            "BUY": buy_count,

            "SELL": sell_count,

        }

    def get_confidence_statistics(
        self,
        db: Session,
    ) -> dict:

        result = (

            db.query(

                func.avg(
                    PredictionHistory.confidence
                ),

                func.min(
                    PredictionHistory.confidence
                ),

                func.max(
                    PredictionHistory.confidence
                ),

            )

            .first()

        )

        return {

            "average_confidence": round(
                float(result[0] or 0),
                4,
            ),

            "minimum_confidence": round(
                float(result[1] or 0),
                4,
            ),

            "maximum_confidence": round(
                float(result[2] or 0),
                4,
            ),

        }


analytics_service = AnalyticsService()