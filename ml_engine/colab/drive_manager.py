"""
ml_engine/colab/drive_manager.py
─────────────────────────────────────────────────────────────────────────────
Handles mounting Google Drive dynamically without hardcoded paths.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
import sys

logger = logging.getLogger(__name__)


class DriveManager:
    """Manages Google Drive mounting in Colab."""

    @staticmethod
    def mount(mount_point: str = "/content/drive"):
        """Mounts Google Drive if in Colab."""
        if "google.colab" not in sys.modules:
            logger.info("[DriveManager] Not in Colab. Skipping Drive mount.")
            return

        try:
            from google.colab import drive # type: ignore
            
            from ml_engine.config.colab_config import ColabConfig
            project_root = ColabConfig.get_project_root()
            # Drive requires mounting at the root level (/content/drive) usually.
            # We mount standard drive then ensure project_root exists.
            mount_base = "/content/drive"
            if not os.path.exists(mount_base):
                logger.info(f"[DriveManager] Mounting Drive at {mount_base}...")
                drive.mount(mount_base)
            else:
                logger.info(f"[DriveManager] Drive already mounted at {mount_base}.")
                
            if not os.path.exists(project_root):
                logger.warning(f"[DriveManager] Configured project_root {project_root} does not exist on this Drive.")
        except Exception as e:
            logger.error(f"[DriveManager] Failed to mount Drive: {e}")
            raise
