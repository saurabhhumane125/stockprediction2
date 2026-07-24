import os
import json
import tempfile
import numpy as np
import pytest

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

from ml_engine.calibration.calibrator import CalibrationManager, CalibratedModelWrapper
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


def test_calibration_manager_execution(mock_calibration_env):
    storage, tmpdir, model_path, artifact_dir, data_path = mock_calibration_env
    
    # Load data and model
    X_val, y_val = storage.load_arrays(f"{data_path}/val.npz")
    model = tf.keras.models.load_model(model_path)
    
    y_prob = model.predict(X_val, verbose=0)
    
    # Run calibration
    calibrator = CalibrationManager(method="isotonic")
    calibrator.fit(y_prob, y_val)
    
    assert calibrator._fitted is True
    
    y_prob_calibrated = calibrator.transform(y_prob)
    assert y_prob_calibrated.shape == (30,)
    assert np.all(y_prob_calibrated >= 0.0) and np.all(y_prob_calibrated <= 1.0)
    
    # Test save/load
    calib_path = os.path.join(tmpdir, "calibrator.pkl")
    calibrator.save(calib_path)
    assert os.path.exists(calib_path)
    
    loaded_calibrator = CalibrationManager.load(calib_path)
    assert loaded_calibrator._fitted is True
    assert loaded_calibrator.method_name == "isotonic"


def test_calibration_manager_not_fitted():
    calibrator = CalibrationManager(method="isotonic")
    with pytest.raises(RuntimeError, match="CalibrationManager must be fitted before transform."):
        calibrator.transform(np.array([0.5, 0.6]))

