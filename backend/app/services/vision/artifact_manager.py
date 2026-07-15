import os
import json
import logging
from pathlib import Path

from app.schemas import VisionSession, VisionInferenceTrace

logger = logging.getLogger(__name__)

class VisionArtifactManager:
    """
    Manages persistence of massive JSON traces and artifacts for Vision Predictions.
    Deduplicates storage using the image_hash.
    """
    def __init__(self):
        project_root = Path(__file__).resolve().parents[4]
        self.artifacts_dir = project_root / "backend" / "vision_artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_artifact_path(self, image_hash: str) -> Path:
        return self.artifacts_dir / f"{image_hash}.json"
        
    def save_artifacts(
        self,
        image_hash: str,
        vision_session: VisionSession,
        inference_trace: VisionInferenceTrace
    ):
        """
        Saves the vision session and inference trace as a combined JSON artifact.
        Overwrites safely if idempotent request happens.
        """
        path = self._get_artifact_path(image_hash)
        
        payload = {
            "vision_session": vision_session.model_dump(),
            "inference_trace": inference_trace.model_dump(),
            "image_hash": image_hash
        }
        
        try:
            with open(path, "w") as f:
                json.dump(payload, f, indent=2)
            logger.info(f"Successfully saved Vision Artifacts to {path}")
        except Exception as e:
            logger.error(f"Failed to write artifact for {image_hash}: {e}")
            raise
            
    def get_artifacts(self, image_hash: str) -> dict | None:
        """
        Retrieves the persisted artifacts for an image hash if they exist.
        """
        path = self._get_artifact_path(image_hash)
        
        if not path.exists():
            return None
            
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read artifact for {image_hash}: {e}")
            return None

vision_artifact_manager = VisionArtifactManager()
