from fastapi import (
    APIRouter,
    Depends,
)

from app.core.exceptions import raise_http
from app.core.logger import logger
from app.core.dependencies import (
    get_current_user,
)

from app.models import User
from app.schemas import PredictionResponse

from app.database import SessionLocal
from app.services.live_prediction_service import (
    live_prediction_service,
)

router = APIRouter(
    prefix="/predict",
    tags=["Live Prediction"],
)


@router.post(
    "/live/{stock}",
    response_model=PredictionResponse,
)
def predict_live(

    stock: str,

    current_user: User = Depends(
        get_current_user
    ),

):

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