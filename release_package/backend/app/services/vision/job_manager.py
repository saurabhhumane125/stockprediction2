import asyncio
import logging
from datetime import datetime, timezone
import uuid
from typing import Callable, Awaitable, Any

from PIL import Image
from sqlalchemy.orm import Session

from app.schemas import PredictionJob, PredictionJobState, VisionPredictionRequest, VisionPredictionResponse
from app.config import settings

logger = logging.getLogger(__name__)

class VisionJobManager:
    """
    Abstracts Vision Operations into Jobs. 
    Applies Operational Guards (timeouts, max dimensions).
    Currently executes synchronously via asyncio.wait_for, but is designed 
    to be easily swappable with a task queue (like Celery).
    """
    
    async def execute_job(
        self,
        request: VisionPredictionRequest,
        db: Session,
        current_user: Any,
        image_path: str,
        work_fn: Callable[[VisionPredictionRequest, Session, Any], Awaitable[VisionPredictionResponse]]
    ) -> VisionPredictionResponse:
        
        job_id = str(uuid.uuid4())
        
        job = PredictionJob(
            job_id=job_id,
            request=request,
            state=PredictionJobState.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        logger.info(f"Created Vision PredictionJob {job_id} for user {current_user.id}")
        
        try:
            # Operational Guard: Memory / Dimensions
            self._guard_image_size(image_path)
            
            job.state = PredictionJobState.RUNNING
            job.updated_at = datetime.now(timezone.utc)
            
            # Operational Guard: Timeout
            response = await asyncio.wait_for(
                work_fn(request, db, current_user),
                timeout=settings.VISION_PROCESSING_TIMEOUT_SEC
            )
            
            job.state = PredictionJobState.COMPLETED
            job.updated_at = datetime.now(timezone.utc)
            logger.info(f"Vision PredictionJob {job_id} COMPLETED successfully.")
            
            return response
            
        except asyncio.TimeoutError:
            job.state = PredictionJobState.TIMEOUT
            job.updated_at = datetime.now(timezone.utc)
            job.error_message = f"Processing exceeded timeout of {settings.VISION_PROCESSING_TIMEOUT_SEC}s"
            logger.error(f"Vision PredictionJob {job_id} TIMED OUT.")
            raise ValueError(job.error_message)
            
        except Exception as e:
            job.state = PredictionJobState.FAILED
            job.updated_at = datetime.now(timezone.utc)
            job.error_message = str(e)
            logger.error(f"Vision PredictionJob {job_id} FAILED: {str(e)}")
            raise ValueError(f"Vision Job Failed: {str(e)}")

    def _guard_image_size(self, image_path: str):
        """
        Validates that the image does not exceed configured dimensions to prevent OOM.
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                if width > settings.VISION_MAX_IMAGE_WIDTH or height > settings.VISION_MAX_IMAGE_HEIGHT:
                    raise ValueError(f"Image dimensions ({width}x{height}) exceed maximum allowed ({settings.VISION_MAX_IMAGE_WIDTH}x{settings.VISION_MAX_IMAGE_HEIGHT})")
        except FileNotFoundError:
            raise ValueError("File not found during size verification.")
        except Exception as e:
            # Let other PIL errors bubble up as ValueErrors
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid image file: {str(e)}")

vision_job_manager = VisionJobManager()
