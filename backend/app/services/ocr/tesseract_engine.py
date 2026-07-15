import logging
from PIL import Image
import pytesseract

from app.services.ocr.engine_interface import BaseOCREngine
from app.schemas import OCRResult, ChartMetadata, ExtractedField

logger = logging.getLogger(__name__)

class TesseractEngine(BaseOCREngine):
    """
    Implementation of the BaseOCREngine using pytesseract.
    """
    
    def extract(self, image_path: str) -> OCRResult:
        try:
            # NOTE: For production Windows, pytesseract.pytesseract.tesseract_cmd must be configured if not in PATH.
            # We assume it is in PATH or this is running in a configured container.
            image = Image.open(image_path)
            
            # Simple extraction for now. A production version would crop and preprocess.
            # We also get data string to extract confidence.
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            raw_text = pytesseract.image_to_string(image)
            
            # Calculate average confidence of valid words
            confidences = [int(c) for c in data['conf'] if str(c) != '-1']
            avg_conf = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0
            
            if not raw_text.strip():
                return OCRResult(
                    success=False,
                    confidence=0.0,
                    metadata=ChartMetadata(),
                    raw_text="",
                    error="No text detected by Tesseract"
                )
                
            # A rudimentary regex/keyword parser would go here to fill ChartMetadata.
            # This is a foundation, so we leave advanced parsing for later.
            
            # Placeholder parsing logic:
            metadata = ChartMetadata()
            
            return OCRResult(
                success=True,
                confidence=avg_conf,
                metadata=metadata,
                raw_text=raw_text.strip(),
                error=None
            )
            
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return OCRResult(
                success=False,
                confidence=0.0,
                metadata=ChartMetadata(),
                raw_text="",
                error=str(e)
            )
