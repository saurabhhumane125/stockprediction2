from fastapi import APIRouter

from app.core.exceptions import raise_http
from app.core.logger import logger

from app.database import SessionLocal
from app.services.live_prediction_service import (
    live_prediction_service,
)

router = APIRouter(
    prefix="/predict",
    tags=["Live Prediction"],
)


@router.post("/live/{stock}")
def predict_live(stock: str):

    db = SessionLocal()

    logger.info(
        f"Live prediction requested for {stock.upper()}"
    )

    try:

        result = live_prediction_service.predict(
            db=db,
            stock=stock,
        )

        logger.info(
            f"Prediction completed for {stock.upper()}"
        )

        return result

    except Exception as e:

        raise_http(e)

    finally:

        db.close()