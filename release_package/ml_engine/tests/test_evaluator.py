import os
import json
import tempfile
import numpy as np
import pytest

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

from ml_engine.evaluation.evaluator import ProductionEvaluator
from ml_engine.data.storage.numpy_storage import NumpyStorage
from ml_engine.config.training_config import training_config


@pytest.fixture
def mock_evaluation_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = NumpyStorage(base_path=tmpdir)
        base_path = "MOCK/v1"
        
        # 20 samples, 5 sequence length, 2 features
        X_test = np.random.rand(20, 5, 2).astype(np.float32)
        # Create a mix of 0s and 1s to test metrics correctly
        y_test = np.array([0, 1] * 10).astype(np.float32)
        
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


def test_production_evaluator_execution(mock_evaluation_env, monkeypatch):
    storage, tmpdir, model_path, artifact_dir, data_path = mock_evaluation_env
    
    # Run evaluation
    evaluator = ProductionEvaluator(tensor_storage=storage, artifact_dir=artifact_dir)
    report = evaluator.evaluate(model_path, data_path)
    
    # Assert JSON artifacts exist
    assert os.path.exists(os.path.join(artifact_dir, "evaluation.json"))
    assert os.path.exists(os.path.join(artifact_dir, "metrics.json"))
    assert os.path.exists(os.path.join(artifact_dir, "evaluation.md"))
    
    # Assert Plots exist
    plots_dir = os.path.join(artifact_dir, "plots")
    assert os.path.exists(plots_dir)
    assert os.path.exists(os.path.join(plots_dir, "confusion_matrix.png"))
    assert os.path.exists(os.path.join(plots_dir, "roc_curve.png"))
    assert os.path.exists(os.path.join(plots_dir, "pr_curve.png"))
    assert os.path.exists(os.path.join(plots_dir, "calibration_curve.png"))
    assert os.path.exists(os.path.join(plots_dir, "prediction_distribution.png"))
    
    # Assert report data
    assert report is not None
    assert "accuracy" in report["Metrics"]
    assert "roc_auc" in report["Metrics"]
    assert report["Prediction Distribution"]["Total Samples"] == 20
    
    with open(os.path.join(artifact_dir, "evaluation.md"), "r") as f:
        md = f.read()
        assert "Production Evaluation Report" in md
        assert "ROC Curve" in md


def test_production_evaluator_insufficient_data(mock_evaluation_env):
    storage, tmpdir, model_path, artifact_dir, data_path = mock_evaluation_env
    
    # Create empty dataset
    storage.save_arrays("EMPTY/v1/test.npz", X=np.array([]), y=np.array([]))
    
    evaluator = ProductionEvaluator(tensor_storage=storage, artifact_dir=artifact_dir)
    
    with pytest.raises(ValueError, match="Insufficient test data"):
        evaluator.evaluate(model_path, "EMPTY/v1")
