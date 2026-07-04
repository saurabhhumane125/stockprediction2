from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    PredictionHistory,
    Stock,
)
from app.core.exceptions import raise_http

router = APIRouter(
    prefix="/history",
    tags=["Prediction History"],
)


@router.get("/")
def get_history(
    db: Session = Depends(get_db),
):

    try:

        rows = (
            db.query(
                PredictionHistory,
                Stock,
            )
            .join(
                Stock,
                PredictionHistory.stock_id == Stock.id,
            )
            .order_by(
                PredictionHistory.created_at.desc()
            )
            .all()
        )

        return [
            {
                "id": history.id,
                "symbol": stock.symbol,
                "prediction": history.prediction,
                "confidence": history.confidence,
                "probability_buy": history.probability_buy,
                "probability_sell": history.probability_sell,
                "created_at": history.created_at,
            }
            for history, stock in rows
        ]

    except Exception as e:

        raise_http(e)


@router.get("/{symbol}")
def get_stock_history(
    symbol: str,
    db: Session = Depends(get_db),
):

    try:

        rows = (
            db.query(PredictionHistory)
            .join(Stock)
            .filter(
                Stock.symbol == symbol.upper()
            )
            .order_by(
                PredictionHistory.created_at.desc()
            )
            .all()
        )

        return rows

    except Exception as e:

        raise_http(e)


@router.get("/latest/{symbol}")
def latest_prediction(
    symbol: str,
    db: Session = Depends(get_db),
):

    try:

        row = (
            db.query(PredictionHistory)
            .join(Stock)
            .filter(
                Stock.symbol == symbol.upper()
            )
            .order_by(
                PredictionHistory.created_at.desc()
            )
            .first()
        )

        return row

    except Exception as e:

        raise_http(e)