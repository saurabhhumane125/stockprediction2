from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DashboardResponse
from app.services.dashboard_service import dashboard_service


from app.core.dependencies import (
    get_current_user,
)

from app.models import User

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/{symbol}",
    response_model=DashboardResponse,
)
def dashboard(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    data = dashboard_service.get_dashboard(
        db,
        symbol,
    )

    if data is None:

        raise HTTPException(
            status_code=404,
            detail="Stock not found.",
        )

    return data