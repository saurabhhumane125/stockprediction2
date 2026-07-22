"""
ml_engine/colab/artifact_sync.py
─────────────────────────────────────────────────────────────────────────────
Synchronizes artifacts for download post-training.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
import shutil

logger = logging.getLogger(__name__)


class ArtifactSynchronizer:
    """Packages training outputs into a single downloadable zip."""

    @staticmethod
    def sync_to_drive():
        """
        Syncs generated artifacts from the Colab VM back to Google Drive.
        Uses paths from colab.yaml via ColabConfig.
        """
        logger.info("[ArtifactSync] Syncing artifacts back to Google Drive...")
        
        from ml_engine.config.colab_config import ColabConfig
        project_root = ColabConfig.get_project_root()
        
        # Pull paths from config
        registry_drive_path = os.path.join(project_root, ColabConfig.get("registry_location", "ml_engine/model_registry"))
        logs_drive_path = os.path.join(project_root, ColabConfig.get("logs_location", "artifacts/logs"))
        exports_drive_path = os.path.join(project_root, ColabConfig.get("exports_location", "artifacts/exports"))
        artifacts_drive_path = os.path.join(project_root, ColabConfig.get("artifacts_location", "artifacts/candidates"))
        
        # Sync Registry (models and metadata)
        ArtifactSynchronizer._copy_tree_safe("ml_engine/model_registry", registry_drive_path)
        
        # Sync tensor metadata if it exists (for reproducibility)
        ArtifactSynchronizer._copy_tree_safe("ml_engine/data/tensors", os.path.join(project_root, "ml_engine/data/tensors"))
        
        # Sync execution logs
        ArtifactSynchronizer._copy_tree_safe("artifacts", artifacts_drive_path)

    @staticmethod
    def _copy_tree_safe(src: str, dst: str):
        if not os.path.exists(src):
            return
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            logger.info(f"[ArtifactSync] Synced {src} to {dst}")
        except Exception as e:
            logger.error(f"[ArtifactSync] Failed to sync {src} to {dst}: {e}")

    @staticmethod
    def sync(run_dir: str, output_zip: str = "artifacts/colab_sync.zip"):
        """
        Zips up the candidate directory, tracker DB, and registry.
        """
        logger.info(f"=== Artifact Sync ===")
        sync_dir = "artifacts/sync_tmp"
        
        try:
            os.makedirs(sync_dir, exist_ok=True)
            
            # 1. Copy Run Dir
            if os.path.exists(run_dir):
                shutil.copytree(run_dir, os.path.join(sync_dir, os.path.basename(run_dir)))
                logger.info(f"[ArtifactSync] Copied {run_dir}")
                
            # 2. Copy Tracker DB
            db_path = "ml_engine/experiments/tracking.db"
            if os.path.exists(db_path):
                # Ensure target directory exists for db
                os.makedirs(os.path.join(sync_dir, "experiments"), exist_ok=True)
                shutil.copy2(db_path, os.path.join(sync_dir, "experiments", "tracking.db"))
                logger.info("[ArtifactSync] Copied tracking.db")
                
            # 3. Zip it all
            shutil.make_archive(output_zip.replace('.zip', ''), 'zip', sync_dir)
            logger.info(f"[ArtifactSync] Successfully created {output_zip}")
            
        except Exception as e:
            logger.error(f"[ArtifactSync] Sync failed: {e}")
        finally:
            if os.path.exists(sync_dir):
                shutil.rmtree(sync_dir)
