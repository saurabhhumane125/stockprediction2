"""
ml_engine/tests/test_colab.py
─────────────────────────────────────────────────────────────────────────────
Unit tests for the Colab modules.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import sys
from unittest.mock import patch, MagicMock

from ml_engine.colab.environment import EnvironmentDetector
from ml_engine.colab.execution_validator import ExecutionValidator
from ml_engine.colab.drive_manager import DriveManager
from ml_engine.colab.resume_manager import ResumeManager
from ml_engine.colab.package_builder import PackageBuilder
from ml_engine.colab.artifact_sync import ArtifactSynchronizer


def test_environment_detector():
    report = EnvironmentDetector.get_report()
    assert "is_colab" in report
    assert "python_version" in report
    assert "ram_total_gb" in report


@patch("os.path.exists")
def test_execution_validator(mock_exists):
    # Mock all paths as existing
    mock_exists.return_value = True
    
    # Actually need to bypass the os.makedirs and write check 
    with patch("os.makedirs"), patch("builtins.open", MagicMock()), patch("os.remove"):
        result = ExecutionValidator.validate_pre_flight("CORE/v1.0")
        assert result is True


def test_drive_manager_in_colab():
    # Because we mocked sys.modules to contain google.colab, it should attempt to mount
    with patch("os.path.exists", return_value=False):
        # We need to mock google.colab.drive so it doesn't actually error out
        mock_colab = MagicMock()
        with patch.dict('sys.modules', {'google.colab': mock_colab}):
            DriveManager.mount()
            assert mock_colab.drive.mount.called


def test_drive_manager_not_in_colab():
    # Ensure google.colab is NOT in sys.modules
    original_modules = sys.modules.copy()
    if 'google.colab' in sys.modules:
        del sys.modules['google.colab']
        
    DriveManager.mount()
    # It should exit silently early
    
    sys.modules.update(original_modules)


@patch("os.walk")
@patch("os.path.exists")
@patch("os.path.getmtime")
def test_resume_manager(mock_mtime, mock_exists, mock_walk):
    # Mock artifacts/candidates existing
    mock_exists.side_effect = lambda path: True
    
    # Mock os.walk returning a dummy checkpoint structure
    mock_walk.return_value = [
        ("artifacts/candidates/CORE_run_1", ["checkpoints"], []),
    ]
    
    mock_mtime.return_value = 1000.0
    
    latest = ResumeManager.find_latest_run("CORE/v1.0", "GRU")
    assert latest == "artifacts/candidates/CORE_run_1"


@patch("shutil.make_archive")
def test_package_builder(mock_make_archive):
    with patch("os.path.exists", return_value=True):
        PackageBuilder.build("dummy.zip")
        mock_make_archive.assert_called_once()
        
@patch("shutil.make_archive")
@patch("shutil.copytree")
@patch("shutil.copy2")
def test_artifact_sync(mock_copy2, mock_copytree, mock_make_archive):
    with patch("os.makedirs"), patch("os.path.exists", return_value=True), patch("shutil.rmtree"):
        ArtifactSynchronizer.sync("artifacts/candidates/run1", "dummy.zip")
        mock_copytree.assert_called_once()
        mock_copy2.assert_called_once()
        mock_make_archive.assert_called_once()
