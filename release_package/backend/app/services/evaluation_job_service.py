from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    HistoricalPrice,
    PredictionHistory,
)


class EvaluationJobService:

    def evaluate_pending_predictions(self):

        db: Session = SessionLocal()

        try:

            pending_predictions = (

                db.query(PredictionHistory)

                .filter(
                    PredictionHistory.status == "PENDING"
                )

                .all()

            )

            for prediction in pending_predictions:

                next_day = (

                    db.query(HistoricalPrice)

                    .filter(
                        HistoricalPrice.stock_id == prediction.stock_id,
                        HistoricalPrice.date > prediction.prediction_date,
                    )

                    .order_by(
                        HistoricalPrice.date.asc()
                    )

                    .first()

                )

                #
                # Market not opened yet.
                # Leave prediction pending.
                #

                if next_day is None:
                    continue

                prediction.evaluation_date = (
                    next_day.date
                )

                prediction.evaluated_price = (
                    next_day.close_price
                )

                if (
                    next_day.close_price
                    >= prediction.entry_price
                ):

                    prediction.actual_prediction = "BUY"

                else:

                    prediction.actual_prediction = "SELL"

                prediction.is_correct = int(

                    prediction.prediction
                    == prediction.actual_prediction

                )

                prediction.status = "COMPLETED"

            db.commit()

        except Exception:

            db.rollback()
            raise

        finally:

            db.close()


evaluation_job_service = EvaluationJobService()