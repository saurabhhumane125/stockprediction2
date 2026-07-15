import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.models import User
from app.core.dependencies import get_current_user

# Mock Authentication
async def mock_get_current_user():
    user = User(id=1, email="test@example.com")
    return user

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

@pytest.fixture
def valid_payload():
    return {
        "filename": "test_image.png",
        "trace_id": "test-trace-123"
    }

from app.schemas import VisionPredictionResponse, VisionInferenceTrace

@patch("app.routes.vision_prediction.prediction_controller")
def test_vision_predict_success(mock_controller, valid_payload):
    mock_response = VisionPredictionResponse(
        prediction="UP",
        confidence=0.85,
        stock="RELIANCE",
        trace=VisionInferenceTrace(
            request_id="test",
            vision_session_id="test",
            feature_hash="hash",
            model_version="v1",
            registry_version="v1",
            calibration_version="v1",
            prediction_timestamp="now",
            inference_latency_ms=10.0
        )
    )
    mock_controller.predict = AsyncMock(return_value=mock_response)

    response = client.post("/api/v1/vision/predict", json=valid_payload)
    
    assert response.status_code == 200
    mock_controller.predict.assert_called_once()
    
@patch("app.routes.vision_prediction.prediction_controller")
def test_vision_predict_file_not_found(mock_controller, valid_payload):
    mock_controller.predict = AsyncMock(side_effect=FileNotFoundError("Uploaded file test_image.png not found."))
    
    response = client.post("/api/v1/vision/predict", json=valid_payload)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

@patch("app.routes.vision_prediction.prediction_controller")
def test_vision_predict_validation_error(mock_controller, valid_payload):
    mock_controller.predict = AsyncMock(side_effect=ValueError("Feature Generation Failed: ['NaN detected']"))
    
    response = client.post("/api/v1/vision/predict", json=valid_payload)
    
    assert response.status_code == 400
    assert "Feature Generation Failed" in response.json()["detail"]

@patch("app.routes.vision_prediction.prediction_controller")
def test_vision_predict_internal_error(mock_controller, valid_payload):
    mock_controller.predict = AsyncMock(side_effect=RuntimeError("Something terrible happened."))
    
    response = client.post("/api/v1/vision/predict", json=valid_payload)
    
    assert response.status_code == 500
    assert "Internal Server Error" in response.json()["detail"]
    
def test_vision_predict_unauthenticated():
    # Remove auth override
    app.dependency_overrides.pop(get_current_user, None)
    
    response = client.post("/api/v1/vision/predict", json={"filename": "test.png"})
    
    # Needs auth token, but we didn't provide one
    assert response.status_code == 401
    
    # Restore for other tests if needed
    app.dependency_overrides[get_current_user] = mock_get_current_user
