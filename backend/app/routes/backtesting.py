from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.services.backtesting_service import (
    backtesting_service,
)

from app.core.dependencies import (
    get_current_user,
)

from app.schemas import (
    BacktestingResponse,
)

from app.models import User

from app.core.exceptions import raise_http

router = APIRouter(
    prefix="/backtesting",
    tags=["Backtesting"],
)


@router.get(
    "/{symbol}",
    response_model=BacktestingResponse,
)
def backtesting(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
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

    except HTTPException:
        raise

    except Exception as e:

        raise_http(e)