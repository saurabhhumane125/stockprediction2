from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    APP_NAME: str = "Stock Price Trend Prediction API"

    APP_VERSION: str = "1.0.0"

    DEBUG: bool = False

    DATABASE_URL: str

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    MODEL_DIRECTORY: str = "models"

    NEWS_API_KEY: str = ""

    FRONTEND_URL: str = "http://localhost:3000"

    COOKIE_NAME: str = "access_token"

    COOKIE_SECURE: bool = False

    COOKIE_SAMESITE: str = "lax"

    # Vision Operational Limits
    VISION_MAX_IMAGE_WIDTH: int = 4096
    VISION_MAX_IMAGE_HEIGHT: int = 4096
    VISION_PROCESSING_TIMEOUT_SEC: int = 30
    VISION_MAX_MEMORY_MB: int = 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:

    return Settings()


settings = get_settings()