from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.core.logger import logger

from app.core.model_loader import artifacts
from app.jobs.market_jobs import update_market_data
from app.jobs.scheduler import scheduler
#from app.routes.historical_prices import router as historical_prices_router
from app.routes.live_prediction import router as live_prediction_router
from app.routes.prediction import router as prediction_router
#from app.routes.stocks import router as stocks_router
from app.routes.stocks import router as stocks_router
from app.routes.dashboard import router as dashboard_router
from app.routes.analytics import router as analytics_router

from app.routes.history import router as history_router
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    StockPredictionException,
)

from app.routes.backtesting import router as backtesting_router
from app.routes.auth import router as auth_router
from app.routes.upload import router as upload_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    artifacts.load_artifacts()

    scheduler.add_job(
        update_market_data,
        trigger="interval",
        hours=1,
        id="market_sync",
        replace_existing=True,
    )

    scheduler.start()

    logger.info("=" * 60)
    logger.info("ML artifacts loaded successfully.")
    logger.info(
        f"Model : {artifacts.metadata['model_name']}"
    )
    logger.info(
        f"Features : {len(artifacts.features)}"
    )
    logger.info(
        f"Sequence : {artifacts.sequence_length}"
    )
    logger.info(
        "Background Scheduler Started"
    )
    logger.info("=" * 60)

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Stock Price Trend Prediction API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_router)
app.include_router(live_prediction_router)
app.include_router(stocks_router)
#app.include_router(historical_prices_router)
app.include_router(dashboard_router)
app.include_router(
    analytics_router
)
app.include_router(backtesting_router)
app.include_router(auth_router)
app.include_router(history_router)
app.include_router(upload_router)

@app.exception_handler(
    StockPredictionException
)
async def stock_prediction_exception_handler(
    request: Request,
    exc: StockPredictionException,
):

    logger.error(
        f"{request.method} {request.url.path} -> {exc.message}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):

    logger.exception(
        f"Unhandled exception during "
        f"{request.method} {request.url.path}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
        },
    )

@app.get("/")
def root():

    return {
        "message": "API Running",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
    }