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

        logger.info("=" * 60)
        logger.info("Market synchronization started.")

        for stock in STOCKS:

            logger.info(
                "Synchronizing %s",
                stock,
            )

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

        logger.info(
            "Evaluating pending predictions."
        )

        evaluation_job_service.evaluate_pending_predictions()

        logger.info(
            "Prediction evaluation completed."
        )

        logger.info(
            "Market synchronization completed."
        )

        logger.info("=" * 60)

    except Exception as error:

        logger.exception(
            "Market synchronization failed."
        )

        db.rollback()

        raise

    finally:

        db.close()