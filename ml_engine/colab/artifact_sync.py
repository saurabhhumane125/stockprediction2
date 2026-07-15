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
