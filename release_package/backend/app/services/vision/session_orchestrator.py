import time
import uuid
from typing import Optional
import logging

from app.schemas import VisionSession, ChartMetadata, OCRResult
from app.services.vision.coordinate_normalizer import coordinate_normalizer
from app.services.vision.validator import metadata_validator
from app.services.vision.metadata_resolver import metadata_resolver
from app.services.vision.ohlc_resolver import ohlc_resolver
from app.services.vision.provider_registry import provider_registry

logger = logging.getLogger(__name__)

class VisionSessionOrchestrator:
    """
    Orchestrates the entire vision validation and resolution pipeline.
    Produces a single, immutable VisionSession object.
    """
    
    def create_session(
        self, 
        ocr_result: OCRResult, 
        upload_metadata: dict,
        trace_id: Optional[str] = None
    ) -> VisionSession:
        start_time = time.perf_counter()
        
        # 1. Normalize Coordinates
        normalized_coords_meta = coordinate_normalizer.normalize(ocr_result.metadata)
        
        # 2. Validate extracted data
        validation_result = metadata_validator.validate(normalized_coords_meta)
        
        resolved_ohlc = None
        normalized_meta = None
        provider_name = None
        
        if not validation_result.is_valid:
            logger.warning(f"Vision validation failed: {validation_result.errors}")
        else:
            # 3. Resolve Metadata (Normalization for providers)
            normalized_meta = metadata_resolver.resolve(normalized_coords_meta)
            
            # 4. Resolve OHLC via Market Provider
            try:
                resolved_ohlc = ohlc_resolver.resolve(normalized_meta)
                if resolved_ohlc:
                    provider_name = provider_registry.get_default_provider_name()
                else:
                    validation_result.errors.append("OHLC Resolution returned empty data.")
                    validation_result.is_valid = False
            except Exception as e:
                logger.error(f"Failed to resolve OHLC: {e}")
                validation_result.errors.append(f"OHLC Provider Error: {str(e)}")
                validation_result.is_valid = False
                
        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000
        
        session = VisionSession(
            request_id=str(uuid.uuid4()),
            upload_metadata=upload_metadata,
            ocr_metadata=ocr_result.metadata,
            normalized_metadata=normalized_meta,
            resolved_ohlc=resolved_ohlc,
            provider_used=provider_name,
            validation_result=validation_result,
            processing_time_ms=processing_time_ms,
            trace_id=trace_id
        )
        
        return session

session_orchestrator = VisionSessionOrchestrator()
