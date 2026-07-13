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

class LatestCandleResponse(BaseModel):

    date: str

    open: float
    high: float
    low: float
    close: float

    volume: float

class ExplanationResponse(BaseModel):

    trend: str

    trend_strength: str

    rsi: float

    rsi_state: str

    roc: float

    momentum: float

    volatility: float

    atr: float

    bollinger_width: float

    price_position: str

    volume_change: float

    volume_trend: str

    summary: list[str]


class MarketRegimeResponse(BaseModel):

    regime: str

    trend: str

    trend_strength: str

    volatility: str

    momentum: str


class LatestFeaturesResponse(BaseModel):

    Open: float
    High: float
    Low: float
    Close: float
    Volume: float

    RSI: float
    MACD: float

    EMA20: float
    EMA50: float

    ATR: float
    ADX: float

    BB_UPPER: float
    BB_LOWER: float
    BB_WIDTH: float

    ROC: float
    MOMENTUM: float

    DAILY_RETURN: float
    VOLATILITY: float
    VOLUME_CHANGE: float



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

    latest_features: LatestFeaturesResponse | None = None

    latest_candle: LatestCandleResponse | None = None

    explanation: ExplanationResponse | None = None

    market_regime: MarketRegimeResponse | None = None


class PredictionHistoryResponse(BaseModel):

    id: int

    symbol: str

    prediction: str

    confidence: float

    probability_buy: float | None

    probability_sell: float | None

    created_at: datetime


class PredictionHistoryListResponse(BaseModel):

    history: list[PredictionHistoryResponse]


class LatestBacktestPredictionResponse(BaseModel):

    prediction: str

    confidence: float

    created_at: datetime

    is_correct: bool | None


class BacktestingResponse(BaseModel):

    stock: str

    total_predictions: int

    evaluated_predictions: int

    pending_predictions: int

    wins: int

    losses: int

    accuracy: float

    win_rate: float

    loss_rate: float

    average_confidence: float

    latest_prediction: LatestBacktestPredictionResponse | None


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


class RecommendationResponse(BaseModel):

    action: str

    strength: str

    confidence: float

    prediction: str

    sentiment: str

    sentiment_score: float

    class_id: int | None

    probability_buy: float | None

    probability_sell: float | None

    technical_signal: str

    news_signal: str

    reason: str

    summary: str


    
class DashboardResponse(BaseModel):

    stock: StockResponse

    latest_price: HistoricalPriceResponse | None

    latest_prediction: PredictionResponse | None

    recommendation: RecommendationResponse | None

    class Config:
        from_attributes = True

# ============================================================
# Authentication Schemas
# ============================================================

class RegisterRequest(BaseModel):

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    email: str = Field(
        ...,
        max_length=255,
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):

    email: str = Field(
        ...,
        max_length=255,
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):

    id: int

    full_name: str

    email: str

    is_active: int

    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):

    access_token: str

    token_type: str

class UploadResponse(BaseModel):

    filename: str

    hash: str

    size_bytes: int

    mime_type: str

    status: str

    message: Optional[str] = None