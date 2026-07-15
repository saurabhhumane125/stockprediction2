"""
ml_engine/tests/test_manifest.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for the ManifestManager and its execution locking capabilities.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import json
import pytest
from unittest.mock import patch, mock_open

from ml_engine.colab.manifest_manager import ManifestManager


def test_compute_config_hash():
    # Should not throw and should be deterministic
    h1 = ManifestManager._compute_config_hash()
    h2 = ManifestManager._compute_config_hash()
    assert h1 == h2
    assert len(h1) == 64  # sha256


@patch("ml_engine.colab.manifest_manager.ManifestManager._get_package_version")
def test_generate_manifest(mock_pkg):
    mock_pkg.return_value = "1.0.0"
    
    with patch("builtins.open", mock_open()) as mocked_file:
        manifest = ManifestManager.generate_manifest("CORE/v1.0")
        
        assert "python_version" in manifest
        assert manifest["dataset_version"] == "CORE/v1.0"
        assert manifest["numpy_version"] == "1.0.0"
        assert manifest["config_hash"] == ManifestManager._compute_config_hash()
        
        # Verify JSON was written
        mocked_file.assert_called_with("execution_manifest.json", "w")


@patch("os.path.exists", return_value=True)
def test_verify_manifest_success(mock_exists):
    valid_manifest = {
        "python_version": platform.python_version() if "platform" in globals() else "3.11.9",
        "platform": "Windows",
        "torch_version": "1.0.0",
        "cuda_version": "NOT_INSTALLED",
        "numpy_version": "1.0.0",
        "pandas_version": "1.0.0",
        "scikit_learn_version": "1.0.0",
        "optuna_version": "1.0.0",
        "config_hash": ManifestManager._compute_config_hash(),
        "dataset_version": "CORE/v2.0",
        "registry_version": "LATEST"
    }
    
    import platform
    valid_manifest["python_version"] = platform.python_version()
    
    with patch("builtins.open", mock_open(read_data=json.dumps(valid_manifest))):
        assert ManifestManager.verify("CORE/v2.0") is True


@patch("os.path.exists", return_value=True)
def test_verify_manifest_failure(mock_exists):
    invalid_manifest = {
        "python_version": "3.11.9",
        "platform": "Windows",
        "torch_version": "1.0.0",
        "cuda_version": "NOT_INSTALLED",
        "numpy_version": "1.0.0",
        "pandas_version": "1.0.0",
        "scikit_learn_version": "1.0.0",
        "optuna_version": "1.0.0",
        "config_hash": "bad_hash_1234",
        "dataset_version": "CORE/v1.0",
        "registry_version": "LATEST"
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(invalid_manifest))):
        assert ManifestManager.verify("CORE/v2.0") is False  # Dataset mismatch and Hash mismatch
