"""
ml_engine/colab/manifest_manager.py
─────────────────────────────────────────────────────────────────────────────
Generates and validates the execution manifest for environment reproducibility.
─────────────────────────────────────────────────────────────────────────────
"""
import hashlib
import json
import logging
import platform
import sys
import os
from typing import Dict, Any

from ml_engine.config.training_config import training_config
from ml_engine.config.model_config import model_config

logger = logging.getLogger(__name__)


class ManifestManager:
    """Handles execution manifest generation and environment verification."""

    MANIFEST_FILE = "execution_manifest.json"

    @staticmethod
    def _get_package_version(pkg_name: str) -> str:
        """Safely gets the version of an installed package."""
        try:
            if sys.version_info >= (3, 8):
                from importlib.metadata import version
                return version(pkg_name)
            else:
                import pkg_resources
                return pkg_resources.get_distribution(pkg_name).version
        except Exception:
            return "NOT_INSTALLED"

    @staticmethod
    def _compute_config_hash() -> str:
        """Computes a combined hash of training and model configs."""
        cfg_str = json.dumps(training_config.to_dict(), sort_keys=True)
        model_str = json.dumps(model_config.to_dict(), sort_keys=True)
        combined = cfg_str + model_str
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def generate_manifest(dataset_version: str) -> Dict[str, Any]:
        """Generates the environment execution manifest."""
        logger.info("[ManifestManager] Generating execution manifest...")

        cuda_version = "NOT_INSTALLED"
        torch_version = ManifestManager._get_package_version("torch")
        
        if torch_version != "NOT_INSTALLED":
            try:
                import torch
                if torch.cuda.is_available():
                    cuda_version = torch.version.cuda
            except ImportError:
                pass

        manifest = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "torch_version": torch_version,
            "cuda_version": cuda_version,
            "numpy_version": ManifestManager._get_package_version("numpy"),
            "pandas_version": ManifestManager._get_package_version("pandas"),
            "scikit_learn_version": ManifestManager._get_package_version("scikit-learn"),
            "optuna_version": ManifestManager._get_package_version("optuna"),
            "config_hash": ManifestManager._compute_config_hash(),
            "dataset_version": dataset_version,
            # For this milestone, we'll leave registry_version empty until a candidate is chosen
            "registry_version": "LATEST"
        }

        with open(ManifestManager.MANIFEST_FILE, "w") as f:
            json.dump(manifest, f, indent=4)
        
        logger.info(f"[ManifestManager] Manifest generated at {ManifestManager.MANIFEST_FILE}.")
        return manifest

    @staticmethod
    def verify(dataset_version: str) -> bool:
        """
        Verifies the current environment against the execution manifest.
        Fails fast if crucial components mismatch.
        """
        logger.info("[ManifestManager] Verifying environment against manifest...")
        
        if not os.path.exists(ManifestManager.MANIFEST_FILE):
            logger.error("[ManifestManager] Execution manifest not found! Generate one first.")
            return False

        with open(ManifestManager.MANIFEST_FILE, "r") as f:
            manifest = json.load(f)

        checks_passed = True

        # Check Python
        current_python = platform.python_version()
        # We only check major.minor match (e.g., 3.11.x)
        if current_python.rsplit('.', 1)[0] != manifest["python_version"].rsplit('.', 1)[0]:
            logger.warning(
                f"[ManifestManager] Python version mismatch. Expected ~{manifest['python_version']}, got {current_python}."
            )
            # Not a strict failure, but a warning
            
        # Check Config Hash
        current_hash = ManifestManager._compute_config_hash()
        if current_hash != manifest["config_hash"]:
            logger.error(
                f"[ManifestManager] Config hash mismatch! Expected {manifest['config_hash']}, got {current_hash}."
            )
            checks_passed = False

        # Check Dataset
        if dataset_version != manifest["dataset_version"]:
            logger.error(
                f"[ManifestManager] Dataset version mismatch! Expected {manifest['dataset_version']}, got {dataset_version}."
            )
            checks_passed = False

        # Check Torch
        current_torch = ManifestManager._get_package_version("torch")
        if current_torch != manifest["torch_version"]:
            logger.warning(
                f"[ManifestManager] Torch version mismatch. Expected {manifest['torch_version']}, got {current_torch}."
            )

        if checks_passed:
            logger.info("[ManifestManager] Environment successfully verified against manifest.")
        else:
            logger.error("[ManifestManager] Environment verification FAILED.")

        return checks_passed
