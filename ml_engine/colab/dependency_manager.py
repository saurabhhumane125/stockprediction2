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

    @staticmethod
    def get_canonical_deps() -> list[str]:
        import os
        if os.path.exists("requirements-training.txt"):
            with open("requirements-training.txt", "r") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        raise FileNotFoundError("requirements-training.txt not found. Cannot determine dependencies.")

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
        
        # Load pinned deps from lockfile
        deps = DependencyManager.get_canonical_deps()
        
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
