from fastapi import APIRouter
from app.schemas import VisionMetricsResponse
from app.services.vision.metrics_service import vision_metrics_service

router = APIRouter(
    prefix="/api/v1/vision",
    tags=["vision_ops"]
)

@router.get("/metrics", response_model=VisionMetricsResponse)
async def get_metrics():
    """
    Returns production operational metrics for the Vision AI pipeline.
    """
    return vision_metrics_service.get_metrics()
