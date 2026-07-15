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
            if not os.path.exists(mount_point):
                logger.info(f"[DriveManager] Mounting Drive at {mount_point}...")
                drive.mount(mount_point)
            else:
                logger.info(f"[DriveManager] Drive already mounted at {mount_point}.")
        except Exception as e:
            logger.error(f"[DriveManager] Failed to mount Drive: {e}")
            raise
