from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class SentimentType(str, enum.Enum):

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    symbol = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    company_name = Column(
        String(255),
        nullable=False,
    )

    sector = Column(
        String(100),
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    prices = relationship(
        "HistoricalPrice",
        back_populates="stock",
        cascade="all, delete-orphan",
    )

    predictions = relationship(
        "PredictionHistory",
        back_populates="stock",
        cascade="all, delete-orphan",
    )

    news = relationship(
        "News",
        back_populates="stock",
        cascade="all, delete-orphan",
    )


class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    stock_id = Column(
        Integer,
        ForeignKey("stocks.id"),
        nullable=False,
        index=True,
    )

    date = Column(
        Date,
        nullable=False,
        index=True,
    )

    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    stock = relationship(
        "Stock",
        back_populates="prices",
    )


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    stock_id = Column(
        Integer,
        ForeignKey("stocks.id"),
        nullable=False,
        index=True,
    )

    prediction = Column(
        String(10),
        nullable=False,
    )

    confidence = Column(
        Float,
        nullable=False,
    )

    probability_buy = Column(
        Float,
        nullable=False,
    )

    probability_sell = Column(
        Float,
        nullable=False,
    )

    prediction_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    evaluation_date = Column(
        Date,
        nullable=True,
    )

    status = Column(
        String(20),
        nullable=False,
        default="PENDING",
    )

    entry_price = Column(
        Float,
        nullable=True,
    )

    evaluated_price = Column(
        Float,
        nullable=True,
    )

    actual_prediction = Column(
        String(10),
        nullable=True,
    )

    is_correct = Column(
        Integer,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    stock = relationship(
        "Stock",
        back_populates="predictions",
    )


class News(Base):
    __tablename__ = "news"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    stock_id = Column(
        Integer,
        ForeignKey("stocks.id"),
        nullable=False,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    source = Column(
        String,
        nullable=False,
    )

    url = Column(
        Text,
        unique=True,
        nullable=False,
    )

    published_at = Column(
        DateTime,
        nullable=False,
    )

    sentiment = Column(
        Enum(SentimentType),
        nullable=True,
    )

    sentiment_score = Column(
        Float,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    stock = relationship(
        "Stock",
        back_populates="news",
    )