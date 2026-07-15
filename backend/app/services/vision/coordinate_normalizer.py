from typing import List, Optional
from app.schemas import ChartMetadata, ExtractedField

class CoordinateNormalizer:
    """
    Normalizes arbitrary OCR engine bounding boxes into a canonical format:
    [x_min, y_min, x_max, y_max].
    """
    
    @staticmethod
    def normalize_box(box: Optional[List[int]], engine: str) -> Optional[List[int]]:
        if not box or len(box) != 4:
            return box
            
        # Example logic depending on engine format
        # If an engine provides [left, top, width, height], we convert it
        if engine.lower() == "tesseract_ltwh":
            left, top, width, height = box
            return [left, top, left + width, top + height]
            
        # Default assume it is already [x_min, y_min, x_max, y_max]
        return box
        
    def normalize(self, metadata: ChartMetadata) -> ChartMetadata:
        """Normalizes all bounding boxes in the metadata in-place."""
        def norm_field(f: Optional[ExtractedField]) -> Optional[ExtractedField]:
            if not f:
                return f
            f.bounding_box = self.normalize_box(f.bounding_box, f.source_engine)
            return f
            
        metadata.symbol = norm_field(metadata.symbol)
        metadata.exchange = norm_field(metadata.exchange)
        metadata.timeframe = norm_field(metadata.timeframe)
        metadata.current_price = norm_field(metadata.current_price)
        metadata.timestamp = norm_field(metadata.timestamp)
        metadata.platform = norm_field(metadata.platform)
        
        return metadata

coordinate_normalizer = CoordinateNormalizer()
