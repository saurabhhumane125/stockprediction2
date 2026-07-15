from datetime import (
    datetime,
    timedelta,
    timezone,
)

from jose import JWTError, jwt

from app.config import settings
from app.models import User


class AuthService:

    def create_access_token(
        self,
        user: User,
    ) -> str:

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    def verify_token(
        self,
        token: str,
    ):

        try:

            return jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[
                    settings.ALGORITHM
                ],
            )

        except JWTError:

            return None

    def cookie_settings(self):

        return {

            "key": settings.COOKIE_NAME,

            "httponly": True,

            "secure": settings.COOKIE_SECURE,

            "samesite": settings.COOKIE_SAMESITE,

            "max_age": (
                settings.ACCESS_TOKEN_EXPIRE_MINUTES
                * 60
            ),

            "path": "/",

        }


auth_service = AuthService()