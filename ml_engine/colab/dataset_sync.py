"""
ml_engine/colab/dataset_sync.py
─────────────────────────────────────────────────────────────────────────────
Synchronizes datasets from Google Drive to the local Colab disk.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import shutil
import logging
import time

from ml_engine.config.colab_config import ColabConfig

logger = logging.getLogger(__name__)


class DatasetSynchronizer:
    """Handles copying tensor datasets from Google Drive to the local runtime."""

    @staticmethod
    def sync(dataset_version: str) -> None:
        """
        Synchronizes the tensor dataset into the local execution path.
        """
        logger.info(f"=== Dataset Synchronization [{dataset_version}] ===")
        
        project_root = ColabConfig.get_project_root()
        datasets_location = ColabConfig.get("datasets_location", "datasets")
        
        # Source is Drive
        source_dir = os.path.join(project_root, datasets_location, dataset_version)
        # Destination is local
        dest_dir = os.path.join("ml_engine", "data", "tensors", dataset_version)
        
        if not os.path.exists(source_dir):
            logger.error(f"[DatasetSync] Source dataset missing at: {source_dir}")
            raise FileNotFoundError(f"Source dataset not found on Drive: {source_dir}")
            
        logger.info(f"[DatasetSync] Source: {source_dir}")
        logger.info(f"[DatasetSync] Destination: {dest_dir}")
        
        os.makedirs(dest_dir, exist_ok=True)
        
        copied_files = 0
        start_time = time.time()
        
        # Safe synchronization
        for root, _, files in os.walk(source_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source_dir)
                dst_path = os.path.join(dest_dir, rel_path)
                
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                
                # Check if file exists and size matches
                if os.path.exists(dst_path):
                    if os.path.getsize(src_path) == os.path.getsize(dst_path):
                        logger.debug(f"[DatasetSync] Skipping identical file: {rel_path}")
                        continue
                        
                shutil.copy2(src_path, dst_path)
                copied_files += 1
                logger.debug(f"[DatasetSync] Copied {rel_path}")
                
        elapsed = time.time() - start_time
        logger.info(f"[DatasetSync] Synced {copied_files} files in {elapsed:.2f} seconds.")
