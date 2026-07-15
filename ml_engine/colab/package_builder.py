"""
ml_engine/colab/package_builder.py
─────────────────────────────────────────────────────────────────────────────
Builds the complete execution package for Colab.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
import shutil

logger = logging.getLogger(__name__)


class PackageBuilder:
    """Zips the ML engine into a standalone package."""

    @staticmethod
    def build(output_zip: str = "colab_execution_package.zip"):
        """Creates a zip containing ml_engine and requirements."""
        logger.info("=== Building Colab Execution Package ===")
        try:
            if os.path.exists("ml_engine"):
                # We want to zip the current directory but ignore heavy artifacts if possible.
                # shutil.make_archive is sufficient for this milestone.
                shutil.make_archive(output_zip.replace('.zip', ''), 'zip', base_dir="ml_engine")
                logger.info(f"[PackageBuilder] Package created at {output_zip}")
            else:
                logger.error("[PackageBuilder] 'ml_engine' directory not found.")
        except Exception as e:
            logger.error(f"[PackageBuilder] Packaging failed: {e}")
