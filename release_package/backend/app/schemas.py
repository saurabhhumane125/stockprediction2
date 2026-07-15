from datetime import date, datetime
from typing import List, Optional, TypeVar, Generic
from enum import Enum

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


T = TypeVar('T')

class ExtractedField(BaseModel, Generic[T]):
    value: Optional[T] = None
    confidence: float
    bounding_box: Optional[List[int]] = None
    source_engine: str

class ChartMetadata(BaseModel):
    symbol: Optional[ExtractedField[str]] = None
    exchange: Optional[ExtractedField[str]] = None
    timeframe: Optional[ExtractedField[str]] = None
    current_price: Optional[ExtractedField[float]] = None
    timestamp: Optional[ExtractedField[str]] = None
    platform: Optional[ExtractedField[str]] = None

class NormalizedOHLC(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: str

class OCRResult(BaseModel):
    success: bool
    confidence: float
    metadata: ChartMetadata
    raw_text: str
    error: Optional[str] = None

class ValidationResult(BaseModel):
    is_valid: bool
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

class VisionSession(BaseModel):
    request_id: str
    upload_metadata: dict
    ocr_metadata: ChartMetadata
    normalized_metadata: Optional[ChartMetadata] = None
    resolved_ohlc: Optional[NormalizedOHLC] = None
    provider_used: Optional[str] = None
    validation_result: ValidationResult
    processing_time_ms: float
    trace_id: Optional[str] = None

    class Config:
        frozen = True

class FeatureProvenance(BaseModel):
    feature_name: str
    origin: str
    calculation_version: str
    lookback_window: int
    provider: str
    generation_timestamp: str
    validation_status: str

class VisionFeatureSet(BaseModel):
    session_id: str
    features: List[List[float]]
    feature_names: List[str]
    feature_hash: str
    provenance: List[FeatureProvenance]
    is_valid: bool
    warnings: List[str]

class VisionInferenceTrace(BaseModel):
    request_id: str
    vision_session_id: str
    feature_hash: str
    model_version: str
    registry_version: str
    calibration_version: str
    prediction_timestamp: str
    inference_latency_ms: float

class VisionPredictionResponse(BaseModel):
    trace: VisionInferenceTrace
    prediction: str
    confidence: float
    probability_buy: Optional[float] = None
    probability_sell: Optional[float] = None
    class_id: Optional[int] = None
    stock: str

class VisionComponentHealth(BaseModel):
    status: str
    details: Optional[str] = None
    
class VisionHealthResponse(BaseModel):
    overall_status: str
    components: dict[str, VisionComponentHealth]

class VisionMetricsResponse(BaseModel):
    success_count: int
    failure_count: int
    avg_ocr_latency_ms: float
    avg_feature_generation_latency_ms: float
    avg_inference_latency_ms: float
    avg_total_request_latency_ms: float
    
class VisionLifecycleState(str, Enum):
    UPLOADED = "UPLOADED"
    OCR_RUNNING = "OCR_RUNNING"
    OCR_COMPLETED = "OCR_COMPLETED"
    FEATURE_GENERATION = "FEATURE_GENERATION"
    COMPATIBILITY_VALIDATION = "COMPATIBILITY_VALIDATION"
    INFERENCE_RUNNING = "INFERENCE_RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class VisionPredictionRequest(BaseModel):
    filename: str
    trace_id: Optional[str] = None

class PredictionJobState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"

class PredictionJob(BaseModel):
    job_id: str
    request: VisionPredictionRequest
    state: PredictionJobState
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None