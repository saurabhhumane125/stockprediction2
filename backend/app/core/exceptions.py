from fastapi import HTTPException

from app.core.logger import logger


class StockPredictionException(Exception):

    def __init__(
        self,
        message: str,
        status_code: int = 400,
    ):
        self.message = message
        self.status_code = status_code


def raise_http(error: Exception):

    if isinstance(
        error,
        StockPredictionException,
    ):
        raise HTTPException(
            status_code=error.status_code,
            detail=error.message,
        )

    logger.exception(error)

    raise HTTPException(
        status_code=500,
        detail="Internal Server Error",
    )