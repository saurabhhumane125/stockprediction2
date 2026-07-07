from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.core.exceptions import raise_http

from app.services.prediction_history_service import (
    prediction_history_service,
)

router = APIRouter(
    prefix="/history",
    tags=["Prediction History"],
)


@router.get("/")
def get_history(
    db: Session = Depends(get_db),
):

    try:

        return prediction_history_service.get_history(
            db,
        )

    except Exception as e:

        raise_http(e)


@router.get("/{symbol}")
def get_stock_history(
    symbol: str,
    db: Session = Depends(get_db),
):

    try:

        return prediction_history_service.get_stock_history(
            db=db,
            symbol=symbol,
        )

    except Exception as e:

        raise_http(e)


@router.get("/latest/{symbol}")
def latest_prediction(
    symbol: str,
    db: Session = Depends(get_db),
):

    try:

        return prediction_history_service.get_latest_prediction(
            db=db,
            symbol=symbol,
        )

    except Exception as e:

        raise_http(e)