from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
)

from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth import auth_service
from app.core.exceptions import raise_http
from app.database import get_db

from app.core.dependencies import (
    get_current_user,
)

from app.schemas import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
)

from app.services.user_service import (
    user_service,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):

    try:

        return user_service.create_user(
            db=db,
            full_name=request.full_name,
            email=request.email,
            password=request.password,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:

        raise_http(e)


@router.post("/login")
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    try:

        user = user_service.authenticate(
            db=db,
            email=request.email,
            password=request.password,
        )

        if user is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password.",
            )

        token = auth_service.create_access_token(
            user
        )

        response.set_cookie(
            value=token,
            **auth_service.cookie_settings(),
        )

        return {

            "message": "Login successful.",

            "user": {

                "id": user.id,

                "full_name": user.full_name,

                "email": user.email,

            },

        }

    except HTTPException:
        raise

    except Exception as e:

        raise_http(e)


@router.post("/logout")
def logout(
    response: Response,
):

    response.delete_cookie(

        key=settings.COOKIE_NAME,

        path="/",

    )

    return {

        "message": "Logout successful."

    }


@router.get("/me")
def me(

    current_user=Depends(
        get_current_user
    )

):

    return {

        "id": current_user.id,

        "full_name": current_user.full_name,

        "email": current_user.email,

        "is_active": current_user.is_active,

    }