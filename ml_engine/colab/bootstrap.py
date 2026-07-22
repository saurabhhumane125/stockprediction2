"""
ml_engine/colab/bootstrap.py
─────────────────────────────────────────────────────────────────────────────
Coordinates initialization: environment, deps, mounts, and validation.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
from ml_engine.colab.environment import EnvironmentDetector
from ml_engine.colab.dependency_manager import DependencyManager
from ml_engine.colab.drive_manager import DriveManager
from ml_engine.colab.gpu_manager import GPUManager
from ml_engine.colab.execution_validator import ExecutionValidator

logger = logging.getLogger(__name__)


class ColabBootstrap:
    """Bootstraps the Colab environment for training."""

    @staticmethod
    def setup(dataset_version: str):
        """Runs the full initialization sequence."""
        logger.info("=== Bootstrapping Colab Environment ===")
        
        # 1. Environment Logging
        EnvironmentDetector.log_environment()
        
        # 2. Drive Mount
        DriveManager.mount()
        
        # 3. Dependencies
        DependencyManager.check_and_install()
        
        # 4. GPU Verification
        has_gpu = GPUManager.verify_gpu()
        if not has_gpu:
            logger.warning("[Bootstrap] No GPU detected. Execution will be slow.")
            
        from ml_engine.colab.manifest_manager import ManifestManager
        
        # 5. Manifest Verification
        manifest_valid = ManifestManager.verify(dataset_version)
        if not manifest_valid:
            logger.error("[Bootstrap] Environment manifest verification failed. Aborting.")
            raise RuntimeError("Colab environment manifest mismatch.")
            
        # 6. Dataset Synchronization
        from ml_engine.colab.dataset_sync import DatasetSynchronizer
        DatasetSynchronizer.sync(dataset_version)
            
        # 7. Validation
        valid = ExecutionValidator.validate_pre_flight(dataset_version)
        
        if valid:
            logger.info("[Bootstrap] System is READY for execution.")
        else:
            logger.error("[Bootstrap] System is NOT READY. Fix validation errors.")
            raise RuntimeError("Colab environment validation failed.")
