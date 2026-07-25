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

from app.services.stock_service import stock_service


def update_market_data():

    db = SessionLocal()

    if artifacts.model is None:

        artifacts.load_artifacts()

    try:

        logger.info("=" * 60)
        logger.info("Market synchronization started.")

        stocks = stock_service.get_all(db)

        processed = 0
        succeeded = 0
        failed = 0

        for stock in stocks:
            processed += 1
            logger.info(
                "Synchronizing %s",
                stock.symbol,
            )

            try:
                historical_data_service.sync_stock(
                    db=db,
                    symbol=stock.symbol,
                )

                news_service.sync_news(
                    db=db,
                    symbol=stock.symbol,
                )

                live_prediction_service.predict(
                    db=db,
                    stock=stock.symbol,
                    sync_news=False,
                )
                
                succeeded += 1

            except Exception as e:
                logger.exception("Failed to process stock %s", stock.symbol)
                failed += 1

        logger.info("-" * 50)
        logger.info("Market Sync Summary")
        logger.info("Processed : %d", processed)
        logger.info("Succeeded : %d", succeeded)
        logger.info("Failed    : %d", failed)
        logger.info("-" * 50)

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