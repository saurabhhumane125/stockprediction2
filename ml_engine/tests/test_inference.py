import os
import json
import tempfile
import numpy as np
import pytest
import joblib

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

from ml_engine.inference.engine import ProductionInferenceEngine
from ml_engine.inference.exceptions import InferenceInputError, RegistryResolutionError
from ml_engine.registry.manager import RegistryManager
from ml_engine.config.registry_config import registry_config
from ml_engine.config.training_config import training_config
from ml_engine.config.inference_config import inference_config

from sklearn.linear_model import LogisticRegression


@pytest.fixture
def mock_inference_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "registry")
        manager = RegistryManager(registry_base_path=registry_path)
        
        source_dir = os.path.join(tmpdir, "source")
        os.makedirs(source_dir)
        
        # 1. Create Mock Keras Model
        input_layer = tf.keras.layers.InputLayer(input_shape=(training_config.SEQUENCE_LENGTH, 20))
        flatten = tf.keras.layers.Flatten()
        output_layer = tf.keras.layers.Dense(1, activation='sigmoid')
        
        model = tf.keras.Sequential([input_layer, flatten, output_layer])
        model_path = os.path.join(source_dir, "best_model.keras")
        model.save(model_path)
        
        # 2. Create Mock Calibrator
        platt = LogisticRegression()
        # Train on dummy data so it can predict
        platt.fit(np.random.rand(100, 1), np.random.randint(0, 2, 100))
        calibrator_path = os.path.join(source_dir, "calibrator.pkl")
        joblib.dump(platt, calibrator_path)
        
        # 2b. Create Mock Scaler
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaler.fit(np.random.rand(100, 20))
        scaler_path = os.path.join(source_dir, "feature_scaler.pkl")
        joblib.dump(scaler, scaler_path)

        # 3. Create dummy reports
        eval_report_path = os.path.join(source_dir, "evaluation_report.json")
        calib_report_path = os.path.join(source_dir, "calibration_report.json")
        with open(eval_report_path, "w") as f:
            json.dump({"dummy": "eval"}, f)
        with open(calib_report_path, "w") as f:
            json.dump({"dummy": "calib"}, f)
            
        source_artifacts = {
            "best_model.keras": model_path,
            "calibrator.pkl": calibrator_path,
            "feature_scaler.pkl": scaler_path,
            "evaluation_report.json": eval_report_path,
            "calibration_report.json": calib_report_path
        }
        
        # Register and Promote to Production
        manager.register_candidate("v1", source_artifacts, metadata={"model_file": "best_model.keras", "framework": "tensorflow"})
        manager.promote_model("v1", registry_config.STATE_CANDIDATE, registry_config.STATE_PRODUCTION)
        
        yield manager


def test_production_inference_successful_predict(mock_inference_env):
    manager = mock_inference_env
    engine = ProductionInferenceEngine(registry_manager=manager)
    
    # Needs to be at least SEQUENCE_LENGTH rows
    seq_len = training_config.SEQUENCE_LENGTH
    num_features = 20
    
    mock_input = np.random.rand(seq_len + 5, num_features).astype(np.float32)
    
    results = engine.predict(mock_input)
    
    assert len(results) == 6  # (seq_len + 5) - seq_len + 1 = 6
    assert "predicted_class" in results[0]
    assert "probability" in results[0]
    assert results[0]["Model Version"] == "v1"


def test_inference_invalid_shapes(mock_inference_env):
    manager = mock_inference_env
    engine = ProductionInferenceEngine(registry_manager=manager)
    
    # 1. Invalid features
    invalid_features = np.random.rand(10, 20 + 1).astype(np.float32)
    with pytest.raises(InferenceInputError, match="Expected"):
        engine.predict(invalid_features)
        
    # 2. Too short sequence
    short_seq = np.random.rand(training_config.SEQUENCE_LENGTH - 1, 20).astype(np.float32)
    with pytest.raises(InferenceInputError, match="Insufficient data"):
        engine.predict(short_seq)
        
    # 3. Not numpy
    with pytest.raises(InferenceInputError):
        engine.predict([[1,2],[3,4]])


def test_unresolved_registry(mock_inference_env):
    # Wipe the registry's active pointer
    manager = mock_inference_env
    os.remove(manager.active_pointer_path)
    
    with pytest.raises(RegistryResolutionError):
        ProductionInferenceEngine(registry_manager=manager)
