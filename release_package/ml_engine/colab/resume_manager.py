"""
ml_engine/colab/resume_manager.py
─────────────────────────────────────────────────────────────────────────────
Handles recovering state from an interrupted Colab session.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
import os
import glob

logger = logging.getLogger(__name__)


class ResumeManager:
    """Finds the most recent checkpoint to resume from."""

    @staticmethod
    def find_latest_run(dataset_version: str, model_type: str) -> str:
        """
        Locates the most recent artifact directory for a given dataset and model.
        Returns the directory path or None.
        """
        base_dir = "artifacts/candidates"
        if not os.path.exists(base_dir):
            return None

        # Look for folders matching "{model_type}_run_*"
        # Actually our version format from runner is model_type_run_id
        # The artifact dir is artifacts/candidates/{dataset_version}_{run_name}
        
        # We need a robust way. Let's just find the latest modified folder in artifacts/candidates
        # that contains a 'checkpoints' folder.
        
        candidates = []
        for root, dirs, files in os.walk(base_dir):
            if "checkpoints" in dirs:
                # verify latest_checkpoint.pt exists
                if os.path.exists(os.path.join(root, "checkpoints", "latest_checkpoint.pt")):
                    candidates.append(root)

        if not candidates:
            logger.info("[ResumeManager] No resumable checkpoints found.")
            return None

        # Sort by modification time
        candidates.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest = candidates[0]
        
        logger.info(f"[ResumeManager] Found resumable checkpoint in: {latest}")
        return latest
