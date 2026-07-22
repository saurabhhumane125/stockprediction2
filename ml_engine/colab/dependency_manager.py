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
    def _is_installed_and_compatible(pkg: str) -> bool:
        """Naive version check; production robust checks would use pkg_resources."""
        import sys
        try:
            pkg_name = pkg.split(">=")[0].split("==")[0]
            if sys.version_info >= (3, 8):
                from importlib.metadata import version
                version(pkg_name)
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def check_and_install():
        """Checks for missing dependencies and installs them."""
        logger.info("[DependencyManager] Checking dependencies...")
        
        # Load pinned deps from lockfile if available
        import os
        deps = DependencyManager.PINNED_DEPS
        if os.path.exists("requirements-training.txt"):
            with open("requirements-training.txt", "r") as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        missing = [pkg for pkg in deps if not DependencyManager._is_installed_and_compatible(pkg)]
        
        if not missing:
            logger.info("[DependencyManager] All dependencies are already satisfied.")
            return

        try:
            logger.info(f"[DependencyManager] Installing missing dependencies: {missing}")
            cmd = [sys.executable, "-m", "pip", "install", "-q"] + missing
            subprocess.check_call(cmd)
            logger.info("[DependencyManager] Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"[DependencyManager] Failed to install dependencies: {e}")
            raise
