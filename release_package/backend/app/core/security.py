from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class PasswordService:

    def hash_password(
        self,
        password: str,
    ) -> str:

        return pwd_context.hash(password)

    def verify_password(
        self,
        plain_password: str,
        password_hash: str,
    ) -> bool:

        return pwd_context.verify(
            plain_password,
            password_hash,
        )


password_service = PasswordService()