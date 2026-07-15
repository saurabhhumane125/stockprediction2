import os
from app.services.ocr.mock_engine import MockEngine
from app.services.ocr.tesseract_engine import TesseractEngine
from app.schemas import OCRResult, ChartMetadata

class OCRService:
    """
    Orchestrates OCR extraction by routing to the configured engine.
    """
    
    def __init__(self):
        # Allow environment configuration of the OCR engine, defaulting to mock for now
        # so that testing and basic validation works without needing Tesseract installed.
        engine_type = os.getenv("OCR_ENGINE", "mock").lower()
        
        if engine_type == "tesseract":
            self.engine = TesseractEngine()
        else:
            self.engine = MockEngine()
            
    def process_image(self, image_path: str) -> OCRResult:
        """
        Processes an uploaded image to extract Chart Metadata.
        """
        if not os.path.exists(image_path):
            return OCRResult(
                success=False,
                confidence=0.0,
                metadata=ChartMetadata(),
                raw_text="",
                error="File does not exist"
            )
            
        return self.engine.extract(image_path)

ocr_service = OCRService()
