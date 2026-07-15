from fastapi import APIRouter, File, UploadFile, Depends
from app.services.upload_service import upload_service
from app.schemas import UploadResponse

router = APIRouter(
    prefix="/api/v1/vision",
    tags=["vision"],
)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Securely uploads an image file for future Vision AI processing.
    """
    return await upload_service.process_upload(file)
