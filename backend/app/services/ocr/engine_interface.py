from abc import ABC, abstractmethod
from app.schemas import OCRResult

class BaseOCREngine(ABC):
    """
    Abstract base class for all OCR engines.
    Ensures modularity and provider-agnosticism.
    """
    
    @abstractmethod
    def extract(self, image_path: str) -> OCRResult:
        """
        Extracts trading chart metadata from an image.
        
        Args:
            image_path (str): The absolute path to the local image file.
            
        Returns:
            OCRResult: A strictly structured DTO.
        """
        pass
