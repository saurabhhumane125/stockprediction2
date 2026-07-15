import pytest
import asyncio
from unittest.mock import patch, MagicMock

from app.schemas import VisionPredictionRequest, VisionPredictionResponse, PredictionJobState, VisionInferenceTrace
from app.services.vision.job_manager import vision_job_manager
from app.services.vision.metrics_service import vision_metrics_service
from app.services.vision.health_service import vision_health_service
from app.config import settings

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    return user

@pytest.fixture
def test_request():
    return VisionPredictionRequest(
        filename="test_img.png",
        trace_id="trace_1"
    )

def test_metrics_service():
    # Initial state
    metrics = vision_metrics_service.get_metrics()
    
    # Record some success
    vision_metrics_service.record_success(10.0, 20.0, 30.0, 100.0)
    vision_metrics_service.record_success(20.0, 40.0, 60.0, 200.0)
    
    # Record a failure
    vision_metrics_service.record_failure()
    
    metrics = vision_metrics_service.get_metrics()
    
    # Metrics should be aggregated across the test session (2 previous runs maybe?)
    # Just asserting that they are positive numbers and failure_count is >= 1
    assert metrics.success_count >= 2
    assert metrics.failure_count >= 1
    assert metrics.avg_ocr_latency_ms > 0
    assert metrics.avg_total_request_latency_ms > 0

def test_health_service(mock_db):
    # Mocking out ML adapter since tests might not load it
    with patch('app.services.vision.health_service.ml_adapter.is_available', True):
        health = vision_health_service.check_health(mock_db)
        # Assuming permissions are ok during tests
        # We just want to ensure it builds the dictionary structure
        assert "ocr" in health.components
        assert "inference" in health.components
        assert "registry" in health.components
        assert "persistence" in health.components
        assert "artifact_storage" in health.components
        assert "upload_storage" in health.components
        
@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_job_manager_success(test_request, mock_db, mock_user, tmp_path):
    # Create dummy image to pass dimension check
    img_path = tmp_path / "test_img.png"
    from PIL import Image
    img = Image.new('RGB', (100, 100))
    img.save(img_path)
    
    async def dummy_work_fn(req, db, user):
        return VisionPredictionResponse(
            trace=VisionInferenceTrace(
                request_id="test",
                vision_session_id="test",
                feature_hash="hash",
                model_version="v1",
                registry_version="v1",
                calibration_version="v1",
                prediction_timestamp="2026",
                inference_latency_ms=10.0
            ),
            prediction="UP",
            confidence=0.9,
            stock="TEST"
        )
        
    response = await vision_job_manager.execute_job(
        request=test_request,
        db=mock_db,
        current_user=mock_user,
        image_path=str(img_path),
        work_fn=dummy_work_fn
    )
    
    assert response.prediction == "UP"

@pytest.mark.anyio
async def test_job_manager_oversized_image(test_request, mock_db, mock_user, tmp_path):
    img_path = tmp_path / "oversize.png"
    from PIL import Image
    # Create image exceeding config limit (assuming max is 4096)
    img = Image.new('RGB', (5000, 5000))
    img.save(img_path)
    
    async def dummy_work_fn(req, db, user):
        pass
        
    with pytest.raises(ValueError) as exc:
        await vision_job_manager.execute_job(
            request=test_request,
            db=mock_db,
            current_user=mock_user,
            image_path=str(img_path),
            work_fn=dummy_work_fn
        )
        
    assert "exceed maximum allowed" in str(exc.value)

@pytest.mark.anyio
async def test_job_manager_timeout(test_request, mock_db, mock_user, tmp_path):
    img_path = tmp_path / "test_img.png"
    from PIL import Image
    img = Image.new('RGB', (100, 100))
    img.save(img_path)
    
    # Overwrite timeout for test
    original_timeout = settings.VISION_PROCESSING_TIMEOUT_SEC
    settings.VISION_PROCESSING_TIMEOUT_SEC = 1
    
    async def slow_work_fn(req, db, user):
        await asyncio.sleep(2.0)
        return None
        
    try:
        with pytest.raises(ValueError) as exc:
            await vision_job_manager.execute_job(
                request=test_request,
                db=mock_db,
                current_user=mock_user,
                image_path=str(img_path),
                work_fn=slow_work_fn
            )
        assert "exceeded timeout" in str(exc.value)
    finally:
        settings.VISION_PROCESSING_TIMEOUT_SEC = original_timeout
