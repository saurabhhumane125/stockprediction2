from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey

class Base(DeclarativeBase):
    pass

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False)
    company_name = Column(String, nullable=False)
    sector = Column(String)

class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True)

    stock_id = Column(Integer, ForeignKey("stocks.id"))

    date = Column(Date, nullable=False)

    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)

    volume = Column(Float)
