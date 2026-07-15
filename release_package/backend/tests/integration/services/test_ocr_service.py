import os
import pytest
from app.services.ocr.ocr_service import OCRService

@pytest.fixture
def test_image_dir(tmp_path):
    """Creates temporary fake image files with specific names for the MockEngine."""
    d = tmp_path / "test_images"
    d.mkdir()
    
    files = [
        "valid_chart.png",
        "missing_ticker.png",
        "missing_timeframe.png",
        "corrupted.png",
        "ocr_failure.png",
        "unsupported_platform.png",
        "low_confidence.png",
    ]
    
    for fname in files:
        f = d / fname
        f.write_text("fake_image_data")
        
    return str(d)

@pytest.fixture
def ocr_svc():
    # Force mock engine for tests
    os.environ["OCR_ENGINE"] = "mock"
    return OCRService()

def test_valid_chart(ocr_svc, test_image_dir):
    img_path = os.path.join(test_image_dir, "valid_chart.png")
    result = ocr_svc.process_image(img_path)
    
    assert result.success is True
    assert result.confidence == 0.95
    assert result.metadata.symbol.value == "RELIANCE"
    assert result.metadata.exchange.value == "NSE"
    assert result.metadata.timeframe.value == "15m"
    assert result.metadata.symbol.confidence == 0.9

def test_missing_ticker(ocr_svc, test_image_dir):
    img_path = os.path.join(test_image_dir, "missing_ticker.png")
    result = ocr_svc.process_image(img_path)
    
    assert result.success is True
    assert result.metadata.symbol is None
    assert result.metadata.timeframe.value == "1D"

def test_missing_timeframe(ocr_svc, test_image_dir):
    img_path = os.path.join(test_image_dir, "missing_timeframe.png")
    result = ocr_svc.process_image(img_path)
    
    assert result.success is True
    assert result.metadata.symbol.value == "TSLA"
    assert result.metadata.timeframe is None

def test_corrupted_image(ocr_svc, test_image_dir):
    img_path = os.path.join(test_image_dir, "corrupted.png")
    result = ocr_svc.process_image(img_path)
    
    assert result.success is False
    assert result.confidence == 0.0
    assert "Failed to decode" in result.error

def test_ocr_failure(ocr_svc, test_image_dir):
    img_path = os.path.join(test_image_dir, "ocr_failure.png")
    result = ocr_svc.process_image(img_path)
    
    assert result.success is False
    assert result.error == "Engine completely failed to read text"

def test_unsupported_platform(ocr_svc, test_image_dir):
    img_path = os.path.join(test_image_dir, "unsupported_platform.png")
    result = ocr_svc.process_image(img_path)
    
    assert result.success is True
    assert result.metadata.platform.value == "UNKNOWN_APP"

def test_low_confidence(ocr_svc, test_image_dir):
    img_path = os.path.join(test_image_dir, "low_confidence.png")
    result = ocr_svc.process_image(img_path)
    
    assert result.success is True
    assert result.confidence < 0.5
    assert "Low confidence" in result.error
