from sqlalchemy.orm import Session

from app.models import User
from app.core.security import password_service


class UserService:

    def get_by_email(
        self,
        db: Session,
        email: str,
    ):

        return (
            db.query(User)
            .filter(
                User.email == email.lower()
            )
            .first()
        )

    def create_user(
        self,
        db: Session,
        full_name: str,
        email: str,
        password: str,
    ):

        existing_user = self.get_by_email(
            db,
            email,
        )

        if existing_user:

            raise ValueError(
                "Email already registered."
            )

        user = User(

            full_name=full_name.strip(),

            email=email.lower().strip(),

            password_hash=password_service.hash_password(
                password
            ),

            is_active=1,
        )

        db.add(user)

        db.commit()

        db.refresh(user)

        return user

    def authenticate(
        self,
        db: Session,
        email: str,
        password: str,
    ):

        user = self.get_by_email(
            db,
            email,
        )

        if user is None:

            return None

        if not password_service.verify_password(
            password,
            user.password_hash,
        ):

            return None

        return user


user_service = UserService()