from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.exceptions import raise_http
from app.core.logger import logger
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas import VisionPredictionRequest, VisionPredictionResponse
from app.database import get_db
from app.services.vision.prediction_controller import prediction_controller

router = APIRouter(
    prefix="/api/v1/vision",
    tags=["vision_prediction"]
)

@router.post("/predict", response_model=VisionPredictionResponse)
async def predict_vision(
    request: VisionPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executes the Vision AI prediction pipeline synchronously.
    Requires a valid image filename from a prior upload.
    """
    try:
        logger.info(f"Vision Prediction requested by User {current_user.id} for {request.filename}")
        
        response = await prediction_controller.predict(request, db, current_user)
        
        return response
        
    except ValueError as e:
        logger.warning(f"Validation Error in Vision Pipeline: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.warning(f"Upload not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Internal Vision Error: {str(e)}")
        raise_http(e)
