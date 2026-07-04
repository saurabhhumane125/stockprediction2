from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.exceptions import raise_http
from app.database import get_db
from app.schemas import StockResponse
from app.services.stock_service import stock_service

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"],
)


@router.get(
    "/",
    response_model=list[StockResponse],
)
def get_all_stocks(
    db: Session = Depends(get_db),
):

    return stock_service.get_all(db)


@router.get(
    "/{symbol}",
    response_model=StockResponse,
)
def get_stock(
    symbol: str,
    db: Session = Depends(get_db),
):

    stock = stock_service.get_by_symbol(
        db,
        symbol,
    )

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail="Stock not found.",
        )

    return stock