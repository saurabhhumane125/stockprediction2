from typing import Optional
from app.schemas import ChartMetadata, ValidationResult, ExtractedField

class MetadataValidator:
    """
    Validates ChartMetadata for completeness and confidence thresholds before OHLC resolution.
    """
    
    def __init__(self, critical_confidence_threshold: float = 0.5):
        self.critical_threshold = critical_confidence_threshold
        
    def validate(self, metadata: ChartMetadata) -> ValidationResult:
        is_valid = True
        warnings = []
        errors = []
        
        # 1. Symbol is absolutely critical
        if not metadata.symbol or not metadata.symbol.value:
            errors.append("Critical field 'symbol' is missing.")
            is_valid = False
        elif metadata.symbol.confidence < self.critical_threshold:
            errors.append(f"Symbol confidence ({metadata.symbol.confidence}) is below threshold ({self.critical_threshold}).")
            is_valid = False
            
        # 2. Timeframe is critical
        if not metadata.timeframe or not metadata.timeframe.value:
            errors.append("Critical field 'timeframe' is missing.")
            is_valid = False
        elif metadata.timeframe.confidence < self.critical_threshold:
            errors.append(f"Timeframe confidence ({metadata.timeframe.confidence}) is below threshold ({self.critical_threshold}).")
            is_valid = False
            
        # 3. Non-critical fields get warnings
        def check_warning(field: Optional[ExtractedField], name: str):
            if not field or not field.value:
                warnings.append(f"Optional field '{name}' is missing.")
            elif field.confidence < self.critical_threshold:
                warnings.append(f"Optional field '{name}' confidence ({field.confidence}) is low.")
                
        check_warning(metadata.exchange, "exchange")
        check_warning(metadata.current_price, "current_price")
        check_warning(metadata.timestamp, "timestamp")
        check_warning(metadata.platform, "platform")
        
        return ValidationResult(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors
        )

metadata_validator = MetadataValidator()
