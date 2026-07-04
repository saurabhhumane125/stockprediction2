from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.backtesting_service import (
    backtesting_service,
)
from app.core.exceptions import raise_http

router = APIRouter(
    prefix="/backtesting",
    tags=["Backtesting"],
)


@router.get("/{symbol}")
def backtesting(
    symbol: str,
    db: Session = Depends(get_db),
):

    try:

        result = backtesting_service.summary(
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