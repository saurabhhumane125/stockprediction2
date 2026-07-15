"""
ml_engine/colab/dependency_manager.py
─────────────────────────────────────────────────────────────────────────────
Manages and verifies dependencies in the Colab environment.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


class DependencyManager:
    """Manages Python packages for Colab."""

    PINNED_DEPS = [
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.2.0",
        "optuna>=3.0.0"
    ]

    @staticmethod
    def check_and_install():
        """Checks for missing dependencies and installs them."""
        logger.info("[DependencyManager] Checking dependencies...")
        
        try:
            # In a real scenario, this would use pkg_resources to check before installing,
            # but blindly pip installing pinned versions in Colab is common and safe.
            cmd = [sys.executable, "-m", "pip", "install", "-q"] + DependencyManager.PINNED_DEPS
            subprocess.check_call(cmd)
            logger.info("[DependencyManager] Dependencies are satisfied.")
        except subprocess.CalledProcessError as e:
            logger.error(f"[DependencyManager] Failed to install dependencies: {e}")
            raise
