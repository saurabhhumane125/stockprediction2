from app.core.logger import logger
from app.database import SessionLocal
from app.core.model_loader import artifacts
from app.services.evaluation_job_service import (
    evaluation_job_service,
)
from app.services.historical_data_service import (
    historical_data_service,
)

from app.services.live_prediction_service import (
    live_prediction_service,
)

from app.services.news_service import (
    news_service,
)

STOCKS = (
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "LT",
    "ITC",
    "HINDUNILVR",
    "BHARTIARTL",
)


def update_market_data():

    db = SessionLocal()

    if artifacts.model is None:

        artifacts.load_artifacts()

    try:

        logger.info(
            "Market synchronization started."
        )

        print("=" * 60)
        print("Market Scheduler Started")

        for stock in STOCKS:

            print(f"Syncing {stock}")

            historical_data_service.sync_stock(
                db=db,
                symbol=stock,
            )

            news_service.sync_news(
                db=db,
                symbol=stock,
            )
            live_prediction_service.predict(
                db=db,
                stock=stock,
                sync_news=False,
            )

        print(
            "Evaluating pending predictions..."
        )

        evaluation_job_service.evaluate_pending_predictions()

        print(
            "Prediction evaluation completed."
        )

        print("Market Scheduler Finished")
        print("=" * 60)

        logger.info(
            "Market synchronization completed."
        )

    except Exception as e:

        logger.exception(e)

        db.rollback()

        raise

    finally:

        db.close()