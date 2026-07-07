from fastapi import (
    Cookie,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth import auth_service
from app.database import get_db
from app.models import User


def get_current_user(

    access_token: str | None = Cookie(
        default=None,
        alias=settings.COOKIE_NAME,
    ),

    db: Session = Depends(get_db),

):

    if access_token is None:

        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    payload = auth_service.verify_token(
        access_token
    )

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )

    user = (
        db.query(User)
        .filter(
            User.id == int(payload["sub"])
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    if user.is_active != 1:

        raise HTTPException(
            status_code=403,
            detail="Inactive account.",
        )

    return user