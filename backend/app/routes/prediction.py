from fastapi import APIRouter
from app.core.exceptions import raise_http

from app.core.logger import logger

from app.schemas import (
    PredictionRequest,
    PredictionResponse
)
from app.services.prediction_service import (
    prediction_service
)

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.post(
    "",
    response_model=PredictionResponse
)
def predict(request: PredictionRequest):

    try:

        logger.info(
            f"Offline prediction requested for {request.stock}"
        )

        return prediction_service.predict(
            stock=request.stock,
            feature_rows=request.features
        )

    except Exception as e:

        raise_http(e)
