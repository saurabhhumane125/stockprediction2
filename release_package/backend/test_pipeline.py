import asyncio
import logging
import warnings
from datetime import datetime, timezone
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)

from app.schemas import ChartMetadata, ExtractedField, VisionSession, ValidationResult
from app.services.vision.ohlc_resolver import ohlc_resolver
from app.services.vision.feature_pipeline import feature_pipeline
from app.services.vision.prediction_controller import prediction_controller
from app.services.vision.date_resolver import vision_date_resolver

async def test_full_pipeline():
    print("\n--- STAGE: OCR MOCK ---")
    metadata = ChartMetadata(
        symbol=ExtractedField(value="RELIANCE.NS", confidence=0.99, source_engine="test"),
        timeframe=ExtractedField(value="1d", confidence=0.99, source_engine="test"),
        timestamp=ExtractedField(value="2024-01-12T10:00:00Z", confidence=0.99, source_engine="test")
    )
    
    print("\n--- STAGE: OHLC RESOLVER ---")
    ohlc = ohlc_resolver.resolve(metadata)
    print(f"OHLC Resolved: {ohlc}")
    
    if not ohlc:
        print("PIPELINE FAILED AT OHLC RESOLVER")
        return
        
    print("\n--- STAGE: FEATURE PIPELINE ---")
    session = VisionSession(
        request_id="test-123",
        upload_metadata={},
        ocr_metadata=metadata,
        resolved_ohlc=ohlc,
        validation_result=ValidationResult(is_valid=True),
        processing_time_ms=10.0,
    )
    
    features = feature_pipeline.process(session)
    print(f"Features valid: {features.is_valid}")
    if not features.is_valid:
        print(f"Warnings: {features.warnings}")
        print("PIPELINE FAILED AT FEATURE PIPELINE")
        return
        
    print(f"Features Shape: {len(features.features)} x {len(features.features[0])}")
        
    print("\n--- STAGE: PREDICTION CONTROLLER ---")
    result = prediction_controller.predict(features)
    print(f"Prediction Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
