"""
ml_engine/colab/package_builder.py
─────────────────────────────────────────────────────────────────────────────
Builds the complete execution package for Colab.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
import zipfile
from ml_engine.config.colab_config import ColabConfig
from ml_engine.colab.manifest_manager import ManifestManager

logger = logging.getLogger(__name__)


class PackageBuilder:
    """Zips the ML engine into a standalone package."""

    @staticmethod
    def build(output_zip: str = "stockprediction_v2.zip"):
        """Creates a zip containing ml_engine and requirements."""
        logger.info("=== Building Colab Execution Package ===")
        try:
            if os.path.exists("ml_engine"):
                # Automatically generate execution manifest
                dataset_version = ColabConfig.get("dataset_id", "NIFTY50/v2.0")
                try:
                    ManifestManager.generate_manifest(dataset_version)
                except Exception as e:
                    logger.error(f"[PackageBuilder] Failed to generate manifest: {e}")
                    
                with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk("ml_engine"):
                        if "__pycache__" in dirs:
                            dirs.remove("__pycache__")
                        
                        # Exclude heavy dataset directories
                        root_unix = root.replace("\\", "/")
                        if root_unix.endswith("ml_engine/data/tensors"):
                            for heavy_dir in ["CORE", "NIFTY50"]:
                                if heavy_dir in dirs:
                                    dirs.remove(heavy_dir)
                                    
                        # Exclude runtime registry artifacts
                        if root_unix.endswith("ml_engine/model_registry"):
                            for state_dir in ["candidate", "staging", "archived", "rolled_back", "deprecated"]:
                                if state_dir in dirs:
                                    dirs.remove(state_dir)
                                    
                        for file in files:
                            if file.endswith(".pyc"):
                                continue
                            
                            # Exclude tracking.db
                            if root_unix.endswith("ml_engine/experiments") and file == "tracking.db":
                                continue
                                
                            file_path = os.path.join(root, file)
                            zf.write(file_path, file_path)
                    
                    if os.path.exists("requirements-training.txt"):
                        zf.write("requirements-training.txt", "requirements-training.txt")
                    else:
                        logger.warning("[PackageBuilder] requirements-training.txt not found!")
                        
                    if os.path.exists(ManifestManager.MANIFEST_FILE):
                        zf.write(ManifestManager.MANIFEST_FILE, ManifestManager.MANIFEST_FILE)
                    else:
                        logger.warning(f"[PackageBuilder] {ManifestManager.MANIFEST_FILE} not found!")
                        
                logger.info(f"[PackageBuilder] Package created at {output_zip}")
            else:
                logger.error("[PackageBuilder] 'ml_engine' directory not found.")
        except Exception as e:
            logger.error(f"[PackageBuilder] Packaging failed: {e}")
