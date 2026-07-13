import os
import hashlib
import shutil
from fastapi import UploadFile, HTTPException, status
from pathlib import Path
import logging

from app.services.malware_scanner import malware_scanner

logger = logging.getLogger(__name__)

class UploadService:
    """
    Handles secure file ingestion, validation, deduplication, and storage.
    """
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
    
    def __init__(self):
        project_root = Path(__file__).resolve().parents[3]
        self.upload_dir = project_root / "backend" / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
    async def process_upload(self, file: UploadFile) -> dict:
        """
        Processes a single upload securely.
        Returns a dict matching the UploadResponse schema.
        """
        
        if not file.content_type or file.content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {self.ALLOWED_MIME_TYPES}"
            )
            
        content = await file.read()
        size_bytes = len(content)
        
        if size_bytes > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {self.MAX_FILE_SIZE / 1024 / 1024}MB."
            )
            
        # Deduplication via Hashing
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Use hash as the filename to prevent malicious execution/directory traversal
        # and ensure exact deduplication
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "bin"
        safe_filename = f"{file_hash}.{ext}"
        file_path = self.upload_dir / safe_filename
        file_path = self.upload_dir / safe_filename
        
        # Save temporally if not exists
        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(content)
                
            # Malware Scan
            if not malware_scanner.scan(str(file_path)):
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="File rejected by malware scanner."
                )
        else:
            logger.info(f"Duplicate file uploaded: {file_hash}")
            
        return {
            "filename": safe_filename,
            "hash": file_hash,
            "size_bytes": size_bytes,
            "mime_type": file.content_type,
            "status": "success",
            "message": "File securely uploaded and validated."
        }

upload_service = UploadService()
