from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.evaluation_service import (
    evaluation_service,
)
from app.core.exceptions import raise_http

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/accuracy/{symbol}")
def accuracy(
    symbol: str,
    db: Session = Depends(get_db),
):

    try:

        result = evaluation_service.evaluate(
            db,
            symbol,
        )

        if result is None:

            raise HTTPException(
                status_code=404,
                detail="Stock not found.",
            )

        return result

    except Exception as e:

        raise_http(e)