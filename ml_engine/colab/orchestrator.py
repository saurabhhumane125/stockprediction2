"""
ml_engine/colab/orchestrator.py
─────────────────────────────────────────────────────────────────────────────
Handles extracting the execution package inside Colab.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import zipfile
import logging
import hashlib
from ml_engine.config.colab_config import ColabConfig

logger = logging.getLogger(__name__)


class PackageOrchestrator:
    """Manages the extraction and validation of the execution package."""

    @staticmethod
    def _calculate_md5(file_path: str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def extract_safely(extract_path: str = "/content"):
        """Extracts the package from Google Drive into the Colab runtime."""
        logger.info("=== Extracting Execution Package ===")
        
        project_root = ColabConfig.get_project_root()
        packages_location = ColabConfig.get("packages_location", "packages")
        package_filename = ColabConfig.get("package_filename", "stockprediction_v2.zip")
        
        package_path = os.path.join(project_root, packages_location, package_filename)
        
        if not os.path.exists(package_path):
            logger.error(f"[Orchestrator] Package not found at {package_path}")
            raise FileNotFoundError(f"Package missing: {package_path}")
            
        logger.info(f"[Orchestrator] Found package: {package_path}")
        
        # Optional checksum validation if checksum file exists
        checksum_path = package_path + ".md5"
        if os.path.exists(checksum_path):
            with open(checksum_path, "r") as f:
                expected_hash = f.read().strip()
            actual_hash = PackageOrchestrator._calculate_md5(package_path)
            if expected_hash != actual_hash:
                logger.error("[Orchestrator] Checksum validation failed!")
                raise ValueError("Package checksum mismatch")
            else:
                logger.info("[Orchestrator] Checksum validated successfully.")
                
        # Extract safely
        logger.info(f"[Orchestrator] Extracting to {extract_path}...")
        try:
            with zipfile.ZipFile(package_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            logger.info("[Orchestrator] Extraction complete.")
            
            # Verify structure
            if not os.path.exists(os.path.join(extract_path, "ml_engine")):
                logger.error("[Orchestrator] Invalid structure: missing ml_engine/ directory")
                raise RuntimeError("Invalid package structure")
            logger.info("[Orchestrator] Structure validated successfully.")
        except zipfile.BadZipFile:
            logger.error("[Orchestrator] Bad zip file format")
            raise RuntimeError("Corrupted zip package")
