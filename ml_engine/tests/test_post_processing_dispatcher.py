import os
import shutil
import tempfile
import numpy as np
import pytest

from ml_engine.core.types import TaskType
from ml_engine.training.post_processing import PostProcessingDispatcher


@pytest.fixture
def temp_artifact_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath, ignore_errors=True)


def test_post_processing_dispatcher_binary(temp_artifact_dir):
    val_true = np.array([0, 1, 0, 1, 0, 1])
    val_preds = np.array([0, 1, 0, 1, 0, 1])
    val_probs = np.array([[0.8, 0.2], [0.1, 0.9], [0.7, 0.3], [0.2, 0.8], [0.9, 0.1], [0.3, 0.7]])
    val_logits = np.array([[-1.5, 1.5], [1.5, -1.5], [-1.0, 1.0], [1.0, -1.0], [-2.0, 2.0], [0.5, -0.5]])

    test_true = val_true
    test_preds = val_preds
    test_probs = val_probs
    test_logits = val_logits

    res = PostProcessingDispatcher.dispatch(
        task_type=TaskType.BINARY_CLASSIFICATION,
        val_true=val_true,
        val_preds=val_preds,
        val_probs=val_probs,
        val_logits=val_logits,
        test_true=test_true,
        test_preds=test_preds,
        test_probs=test_probs,
        test_logits=test_logits,
        artifact_dir=temp_artifact_dir
    )

    assert "metrics" in res
    assert "accuracy" in res["metrics"]
    assert "calibrator_path" in res
    assert os.path.exists(res["calibrator_path"])
    assert "plot_paths" in res["metrics"]


def test_post_processing_dispatcher_regression(temp_artifact_dir):
    val_true = np.array([0.01, 0.02, -0.01, 0.04, 0.02])
    val_preds = np.array([0.012, 0.019, -0.008, 0.038, 0.022])
    val_probs = val_preds.reshape(-1, 1)
    val_logits = val_preds.reshape(-1, 1)

    test_true = val_true
    test_preds = val_preds
    test_probs = val_probs
    test_logits = val_logits

    res = PostProcessingDispatcher.dispatch(
        task_type=TaskType.REGRESSION,
        val_true=val_true,
        val_preds=val_preds,
        val_probs=val_probs,
        val_logits=val_logits,
        test_true=test_true,
        test_preds=test_preds,
        test_probs=test_probs,
        test_logits=test_logits,
        artifact_dir=temp_artifact_dir
    )

    assert "metrics" in res
    assert "rmse" in res["metrics"]
    assert "mae" in res["metrics"]
    assert "r2" in res["metrics"]
    assert "mean_residual" in res["metrics"]
    assert "calibrator_path" in res
    assert os.path.exists(res["calibrator_path"])
    assert "pred_vs_actual" in res["metrics"]["plot_paths"]
    assert "residual_histogram" in res["metrics"]["plot_paths"]


def test_post_processing_dispatcher_multi_output(temp_artifact_dir):
    val_true = np.random.randn(10, 4)
    val_preds = val_true + 0.01
    val_probs = val_preds
    val_logits = val_preds

    res = PostProcessingDispatcher.dispatch(
        task_type=TaskType.MULTI_OUTPUT_REGRESSION,
        val_true=val_true,
        val_preds=val_preds,
        val_probs=val_probs,
        val_logits=val_logits,
        test_true=val_true,
        test_preds=val_preds,
        test_probs=val_probs,
        test_logits=val_logits,
        artifact_dir=temp_artifact_dir
    )

    assert "rmse" in res["metrics"]
    assert "mean_residual" in res["metrics"]
