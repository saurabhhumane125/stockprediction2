import os
import json
import tempfile
import numpy as np
import pytest

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

from ml_engine.calibration.calibrator import ProductionCalibrator
from ml_engine.data.storage.numpy_storage import NumpyStorage


@pytest.fixture
def mock_calibration_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = NumpyStorage(base_path=tmpdir)
        base_path = "MOCK/v1"
        
        # Validation Data: 30 samples, 5 sequence length, 2 features
        X_val = np.random.rand(30, 5, 2).astype(np.float32)
        y_val = np.array([0, 1] * 15).astype(np.float32)
        
        # Testing Data: 20 samples, 5 sequence length, 2 features
        X_test = np.random.rand(20, 5, 2).astype(np.float32)
        y_test = np.array([0, 1] * 10).astype(np.float32)
        
        storage.save_arrays(f"{base_path}/val.npz", X=X_val, y=y_val)
        storage.save_arrays(f"{base_path}/test.npz", X=X_test, y=y_test)
        
        # Build a dummy model and save it
        input_layer = tf.keras.layers.InputLayer(input_shape=(5, 2))
        flatten = tf.keras.layers.Flatten()
        output_layer = tf.keras.layers.Dense(1, activation='sigmoid')
        
        model = tf.keras.Sequential([input_layer, flatten, output_layer])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        
        model_path = os.path.join(tmpdir, "mock_model.keras")
        model.save(model_path)
        
        artifact_dir = os.path.join(tmpdir, "artifacts")
        yield storage, tmpdir, model_path, artifact_dir, base_path


def test_production_calibrator_execution(mock_calibration_env):
    storage, tmpdir, model_path, artifact_dir, data_path = mock_calibration_env
    
    # Run calibration
    calibrator = ProductionCalibrator(tensor_storage=storage, artifact_dir=artifact_dir)
    report = calibrator.calibrate(model_path, data_path)
    
    # Assert JSON artifacts exist
    assert os.path.exists(os.path.join(artifact_dir, "calibration_report.json"))
    assert os.path.exists(os.path.join(artifact_dir, "calibration_metrics.json"))
    assert os.path.exists(os.path.join(artifact_dir, "calibration_report.md"))
    assert os.path.exists(os.path.join(artifact_dir, "calibrator.pkl"))
    
    # Assert Plots exist
    plots_dir = os.path.join(artifact_dir, "plots")
    assert os.path.exists(plots_dir)
    assert os.path.exists(os.path.join(plots_dir, "reliability_before.png"))
    assert os.path.exists(os.path.join(plots_dir, "reliability_after.png"))
    assert os.path.exists(os.path.join(plots_dir, "confidence_distribution.png"))
    
    # Assert report structure
    assert report is not None
    assert "Raw" in report["Metrics"]
    assert "Platt Scaling" in report["Metrics"]
    assert "Isotonic Regression" in report["Metrics"]
    assert "Best Method" in report
    
    # Check JSON metrics
    with open(os.path.join(artifact_dir, "calibration_metrics.json"), "r") as f:
        metrics = json.load(f)
        assert "brier_score" in metrics["Raw"]


def test_production_calibrator_insufficient_data(mock_calibration_env):
    storage, tmpdir, model_path, artifact_dir, data_path = mock_calibration_env
    
    # Create empty dataset
    storage.save_arrays("EMPTY/v1/val.npz", X=np.array([]), y=np.array([]))
    storage.save_arrays("EMPTY/v1/test.npz", X=np.array([]), y=np.array([]))
    
    calibrator = ProductionCalibrator(tensor_storage=storage, artifact_dir=artifact_dir)
    
    with pytest.raises(ValueError, match="Insufficient validation or testing data"):
        calibrator.calibrate(model_path, "EMPTY/v1")
