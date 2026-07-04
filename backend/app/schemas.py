from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):

    stock: str = Field(
        ...,
        examples=["RELIANCE"],
    )

    features: List[List[float]] = Field(
        ...,
        min_length=48,
        max_length=48,
    )


class PredictionResponse(BaseModel):

    prediction: str
    class_id: Optional[int] = None

    confidence: float

    probability_buy: Optional[float] = None
    probability_sell: Optional[float] = None

    stock: str

    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None

    technical_signal: Optional[str] = None
    news_signal: Optional[str] = None
    final_reason: Optional[str] = None


class StockResponse(BaseModel):

    id: int
    symbol: str
    company_name: str
    sector: Optional[str] = None

    class Config:
        from_attributes = True


class HistoricalPriceResponse(BaseModel):

    id: int
    stock_id: int

    date: date

    open_price: float
    high_price: float
    low_price: float
    close_price: float

    volume: float

    created_at: datetime

    class Config:
        from_attributes = True
    
class DashboardResponse(BaseModel):

    stock: StockResponse

    latest_price: HistoricalPriceResponse | None

    latest_prediction: PredictionResponse | None

    recommendation: dict | None

    class Config:
        from_attributes = True