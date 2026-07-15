import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from app.schemas import VisionSession, VisionFeatureSet, ChartMetadata, ExtractedField, ValidationResult
from app.services.vision.inference_service import inference_service

@pytest.fixture
def mock_session():
    return VisionSession(
        request_id="trace_test_123",
        upload_metadata={},
        ocr_metadata=ChartMetadata(symbol=ExtractedField(value="RELIANCE", confidence=1.0, source_engine="test")),
        validation_result=ValidationResult(is_valid=True),
        processing_time_ms=15.0
    )

@pytest.fixture
def mock_feature_set():
    features = np.random.rand(49, 20).tolist() # SEQUENCE_LENGTH + 1
    return VisionFeatureSet(
        session_id="trace_test_123",
        features=features,
        feature_names=[f"f{i}" for i in range(20)],
        feature_hash="mock_hash_sha256",
        provenance=[],
        is_valid=True,
        warnings=[]
    )

@patch("app.services.vision.inference_service.ml_adapter")
def test_inference_service_success(mock_ml_adapter, mock_session, mock_feature_set):
    mock_ml_adapter.is_available = True
    
    mock_engine = MagicMock()
    mock_engine.predict.return_value = [
        {
            "Predicted Class": 1,
            "Raw Probability": 0.85,
            "Calibrated Probability": 0.82,
            "Confidence": 0.82,
            "Model Version": "v1.0.0-legacy",
            "Inference Timestamp": "2026-07-14T12:00:00Z",
            "Execution Duration": 0.05,
            "Manifest Hash": "mock_keras_hash"
        }
    ]
    mock_ml_adapter.inference_engine = mock_engine
    
    response = inference_service.predict(mock_session, mock_feature_set)
    
    # Assert engine was called correctly
    mock_engine.predict.assert_called_once()
    args, _ = mock_engine.predict.call_args
    assert isinstance(args[0], np.ndarray)
    assert args[0].shape == (49, 20)
    
    # Assert Response
    assert response.prediction == "UP"
    assert response.confidence == 0.82
    assert response.probability_buy == pytest.approx(0.82)
    assert response.probability_sell == pytest.approx(0.18)
    assert response.stock == "RELIANCE"
    
    # Assert Trace
    assert response.trace.request_id == "trace_test_123"
    assert response.trace.vision_session_id == "trace_test_123"
    assert response.trace.feature_hash == "mock_hash_sha256"
    assert response.trace.model_version == "v1.0.0-legacy"
    assert response.trace.inference_latency_ms >= 0
    assert response.trace.calibration_version == "v1"

@patch("app.services.vision.inference_service.ml_adapter")
def test_inference_service_engine_unavailable(mock_ml_adapter, mock_session, mock_feature_set):
    mock_ml_adapter.is_available = False
    mock_ml_adapter.inference_engine = None
    
    with pytest.raises(RuntimeError, match="ProductionInferenceEngine is not available"):
        inference_service.predict(mock_session, mock_feature_set)

@patch("app.services.vision.inference_service.ml_adapter")
def test_inference_service_invalid_features(mock_ml_adapter, mock_session, mock_feature_set):
    mock_ml_adapter.is_available = True
    mock_ml_adapter.inference_engine = MagicMock()
    
    mock_feature_set.is_valid = False
    mock_feature_set.warnings = ["NaN detected"]
    
    with pytest.raises(ValueError, match="Cannot run inference on invalid feature set"):
        inference_service.predict(mock_session, mock_feature_set)

@patch("app.services.vision.inference_service.ml_adapter")
def test_inference_service_engine_failure(mock_ml_adapter, mock_session, mock_feature_set):
    mock_ml_adapter.is_available = True
    
    mock_engine = MagicMock()
    mock_engine.predict.side_effect = Exception("Model weights corrupt")
    mock_ml_adapter.inference_engine = mock_engine
    
    with pytest.raises(ValueError, match="Vision inference failed: Model weights corrupt"):
        inference_service.predict(mock_session, mock_feature_set)
