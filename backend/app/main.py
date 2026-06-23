from app.database import engine
from app.models import Base
from fastapi import FastAPI

app = FastAPI(
    title="Stock Price Trend Prediction API",
    version="1.0.0"
)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
