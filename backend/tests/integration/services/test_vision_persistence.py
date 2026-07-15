import pytest
import os
import json
from unittest.mock import patch, MagicMock

from app.schemas import VisionSession, VisionInferenceTrace, VisionPredictionResponse, ChartMetadata, ValidationResult, NormalizedOHLC
from app.services.vision.persistence_service import vision_persistence_service
from app.services.vision.artifact_manager import vision_artifact_manager
from app.models import VisionPredictionHistory, User
from app.database import SessionLocal

@pytest.fixture
def mock_db():
    db = MagicMock()
    # Mocking a valid user
    mock_user = User(id=1, email="test@test.com")
    return db

@pytest.fixture
def test_trace():
    return VisionInferenceTrace(
        request_id="test_req",
        vision_session_id="test_session",
        feature_hash="fhash123",
        model_version="v1",
        registry_version="v1",
        calibration_version="v1",
        prediction_timestamp="2026-07-14T00:00:00Z",
        inference_latency_ms=10.0
    )

@pytest.fixture
def test_vision_session():
    return VisionSession(
        request_id="test_req",
        upload_metadata={"filename": "test.png"},
        ocr_metadata=ChartMetadata(),
        validation_result=ValidationResult(is_valid=True),
        processing_time_ms=5.0
    )

@pytest.fixture
def test_prediction_response(test_trace):
    return VisionPredictionResponse(
        trace=test_trace,
        prediction="UP",
        confidence=0.9,
        stock="RELIANCE"
    )

def test_persist_prediction(mock_db, test_vision_session, test_prediction_response):
    # Setup artifact manager mock to avoid actual disk write
    with patch.object(vision_artifact_manager, 'save_artifacts') as mock_save:
        
        # Act
        history = vision_persistence_service.persist_prediction(
            db=mock_db,
            user_id=1,
            image_hash="imghash123",
            active_model_name="model_1",
            pipeline_version="v1",
            response=test_prediction_response,
            vision_session=test_vision_session
        )
        
        # Assert Artifacts Called
        mock_save.assert_called_once_with(
            image_hash="imghash123",
            vision_session=test_vision_session,
            inference_trace=test_prediction_response.trace
        )
        
        # Assert DB Called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Assert History Object
        assert history.user_id == 1
        assert history.image_hash == "imghash123"
        assert history.prediction == "UP"
        assert history.feature_hash == "fhash123"

def test_get_idempotent_prediction_not_found(mock_db):
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None
    
    result = vision_persistence_service.get_idempotent_prediction(
        db=mock_db,
        user_id=1,
        image_hash="hash123",
        pipeline_version="v1"
    )
    
    assert result is None

def test_get_idempotent_prediction_found(mock_db):
    mock_history = VisionPredictionHistory(
        user_id=1,
        image_hash="hash123",
        pipeline_version="v1",
        prediction="DOWN",
        confidence=0.8,
        feature_hash="fhash",
        model_version="mv1",
        registry_version="rv1",
        calibration_version="cv1"
    )
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = mock_history
    
    result = vision_persistence_service.get_idempotent_prediction(
        db=mock_db,
        user_id=1,
        image_hash="hash123",
        pipeline_version="v1"
    )
    
    assert result is not None
    assert result.prediction == "DOWN"
    assert result.confidence == 0.8
    assert result.trace.request_id == "IDEMPOTENT_HIT"
    assert result.trace.feature_hash == "fhash"
