from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.exceptions import raise_http
from app.database import get_db
from app.services.analytics_service import analytics_service
from app.services.evaluation_service import evaluation_service

from app.core.dependencies import (
    get_current_user,
)

from app.models import User

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/accuracy/{symbol}")
def accuracy(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
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


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
):

    try:

        return analytics_service.get_overview(
            db,
        )

    except Exception as e:

        raise_http(e)


@router.get("/recent")
def recent_predictions(
    limit: int = 20,
    db: Session = Depends(get_db),
):

    try:

        return analytics_service.get_recent_predictions(
            db=db,
            limit=limit,
        )

    except Exception as e:

        raise_http(e)


@router.get("/distribution")
def distribution(
    db: Session = Depends(get_db),
):

    try:

        return analytics_service.get_prediction_distribution(
            db,
        )

    except Exception as e:

        raise_http(e)


@router.get("/confidence")
def confidence(
    db: Session = Depends(get_db),
):

    try:

        return analytics_service.get_confidence_statistics(
            db,
        )

    except Exception as e:

        raise_http(e)