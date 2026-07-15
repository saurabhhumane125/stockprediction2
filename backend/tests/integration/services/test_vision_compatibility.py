import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from app.schemas import VisionFeatureSet
from app.services.vision.compatibility_validator import compatibility_validator

@pytest.fixture
def mock_feature_set():
    # 48 sequence length + 1 current day = 49 rows. 20 features.
    features = np.random.rand(49, 20).tolist()
    return VisionFeatureSet(
        session_id="comp_test_123",
        features=features,
        feature_names=[f"f{i}" for i in range(20)],
        feature_hash="hash",
        provenance=[],
        is_valid=True,
        warnings=[]
    )

@patch("app.services.vision.compatibility_validator.ml_adapter")
def test_compatibility_validator_success(mock_ml_adapter, mock_feature_set):
    mock_ml_adapter.is_available = True
    mock_engine = MagicMock()
    mock_engine.sequence_length = 48
    mock_engine.feature_count = 20
    mock_ml_adapter.inference_engine = mock_engine
    
    is_compatible, errors = compatibility_validator.validate(mock_feature_set)
    
    assert is_compatible is True
    assert len(errors) == 0

@patch("app.services.vision.compatibility_validator.ml_adapter")
def test_compatibility_validator_engine_unavailable(mock_ml_adapter, mock_feature_set):
    mock_ml_adapter.is_available = False
    mock_ml_adapter.inference_engine = None
    
    is_compatible, errors = compatibility_validator.validate(mock_feature_set)
    
    assert is_compatible is False
    assert "ProductionInferenceEngine is unavailable." in errors

@patch("app.services.vision.compatibility_validator.ml_adapter")
def test_compatibility_validator_invalid_feature_count(mock_ml_adapter, mock_feature_set):
    mock_ml_adapter.is_available = True
    mock_engine = MagicMock()
    mock_engine.sequence_length = 48
    mock_engine.feature_count = 21 # Expects 21, receives 20
    mock_ml_adapter.inference_engine = mock_engine
    
    is_compatible, errors = compatibility_validator.validate(mock_feature_set)
    
    assert is_compatible is False
    assert any("Feature count mismatch" in err for err in errors)
    assert any("Feature names mismatch" in err for err in errors)

@patch("app.services.vision.compatibility_validator.ml_adapter")
def test_compatibility_validator_insufficient_history(mock_ml_adapter, mock_feature_set):
    mock_ml_adapter.is_available = True
    mock_engine = MagicMock()
    mock_engine.sequence_length = 60 # Expects 60, receives 49
    mock_engine.feature_count = 20
    mock_ml_adapter.inference_engine = mock_engine
    
    is_compatible, errors = compatibility_validator.validate(mock_feature_set)
    
    assert is_compatible is False
    assert any("Insufficient history" in err for err in errors)
