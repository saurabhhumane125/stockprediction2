import os
import json
import shutil
import hashlib
import time
from typing import Dict, Any, List, Optional
import pandas as pd

from ml_engine.config.registry_config import registry_config
from ml_engine.registry.exceptions import (
    InvalidStateTransitionError,
    HashMismatchError,
    MissingArtifactError,
    VersionConflictError
)

class RegistryManager:
    """
    Production Model Registry Manager.
    Handles artifact ingestion, validation, cryptographic hashing, 
    and strict state transitions ensuring no unverified models hit production.
    """
    
    def __init__(self, registry_base_path: str):
        self.base_path = registry_base_path
        
        # Initialize registry folder structure
        for state in registry_config.VALID_STATES:
            os.makedirs(os.path.join(self.base_path, state), exist_ok=True)
            
        self.active_pointer_path = os.path.join(self.base_path, "active_production.json")

    def _compute_hash(self, file_path: str) -> str:
        """Computes SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    def _verify_integrity(self, version: str, state: str) -> bool:
        """Validates physical files against the cryptographic manifest."""
        bundle_path = os.path.join(self.base_path, state, version)
        manifest_path = os.path.join(bundle_path, "manifest.json")
        
        if not os.path.exists(manifest_path):
            raise MissingArtifactError(f"manifest.json missing in {bundle_path}")
            
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            
        # Verify each artifact
        for artifact_name, expected_hash in manifest["artifacts"].items():
            file_path = os.path.join(bundle_path, artifact_name)
            if not os.path.exists(file_path):
                raise MissingArtifactError(f"Required artifact {artifact_name} is physically missing.")
                
            actual_hash = self._compute_hash(file_path)
            if actual_hash != expected_hash:
                raise HashMismatchError(f"Hash mismatch for {artifact_name}. Expected: {expected_hash}, Actual: {actual_hash}")
                
        return True

    def register_candidate(self, version: str, source_artifacts: Dict[str, str], metadata: Dict[str, Any] = None, authenticity: str = "REAL") -> Dict[str, Any]:
        """
        Registers a new model version into the Candidate state.
        Calculates hashes and generates a manifest.
        """
        candidate_path = os.path.join(self.base_path, registry_config.STATE_CANDIDATE, version)
        
        if os.path.exists(candidate_path):
            raise VersionConflictError(f"Model version {version} already exists in candidate state.")
            
        if not metadata:
            metadata = {}
            
        # Verify required artifacts are present in source
        for req in registry_config.REQUIRED_ARTIFACTS:
            actual_req = metadata.get("model_file") if req == "model_file" else req
            if not actual_req:
                raise MissingArtifactError("metadata['model_file'] must be provided if 'model_file' is in REQUIRED_ARTIFACTS.")
                
            if actual_req not in source_artifacts:
                raise MissingArtifactError(f"Artifact {actual_req} must be provided for registration.")
            if not os.path.exists(source_artifacts[actual_req]):
                raise MissingArtifactError(f"Physical file for {actual_req} not found at {source_artifacts[actual_req]}")
                
        os.makedirs(candidate_path)
        
        if authenticity not in ["REAL", "LEGACY IMPORT", "SYNTHETIC PLACEHOLDER"]:
            raise ValueError(f"Invalid authenticity {authenticity}")
            
        # Copy and Hash
        manifest = metadata.copy()  # Embed full model contract
        manifest.update({
            "model_version": version,
            "authenticity": authenticity,
            "registration_timestamp": pd.Timestamp.utcnow().isoformat(),
            "artifacts": {}
        })
        
        for name, src_path in source_artifacts.items():
            dest_path = os.path.join(candidate_path, name)
            shutil.copy2(src_path, dest_path)
            manifest["artifacts"][name] = self._compute_hash(dest_path)
            
        # Save manifest
        manifest_path = os.path.join(candidate_path, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=4)
            
        return manifest

    def promote_model(self, version: str, current_state: str, target_state: str) -> None:
        """
        Promotes a model from one state to another (e.g., candidate -> staging -> production).
        """
        if current_state not in registry_config.VALID_STATES or target_state not in registry_config.VALID_STATES:
            raise InvalidStateTransitionError(f"Invalid states provided. {current_state} -> {target_state}")
            
        source_dir = os.path.join(self.base_path, current_state, version)
        dest_dir = os.path.join(self.base_path, target_state, version)
        
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Model version {version} not found in {current_state}.")
            
        if os.path.exists(dest_dir):
            raise VersionConflictError(f"Model version {version} already exists in {target_state}.")
            
        # Verify integrity before promotion
        self._verify_integrity(version, current_state)
        
        # Move bundle
        shutil.move(source_dir, dest_dir)
        
        # If moving to production, update active pointer and archive previous
        if target_state == registry_config.STATE_PRODUCTION:
            self._set_active_production(version)

    def _set_active_production(self, version: str) -> None:
        """Sets the currently active production model pointer."""
        prev_version = None
        if os.path.exists(self.active_pointer_path):
            with open(self.active_pointer_path, "r") as f:
                data = json.load(f)
                prev_version = data.get("active_version")
                
        # Update pointer
        with open(self.active_pointer_path, "w") as f:
            json.dump({
                "active_version": version,
                "previous_version": prev_version,
                "updated_at": pd.Timestamp.utcnow().isoformat()
            }, f, indent=4)
            
    def rollback_production(self) -> str:
        """
        Rolls back the current production model to the previous production version.
        Moves the failing model to 'rolled_back'.
        """
        if not os.path.exists(self.active_pointer_path):
            raise InvalidStateTransitionError("No active production model to rollback.")
            
        with open(self.active_pointer_path, "r") as f:
            data = json.load(f)
            
        current_version = data.get("active_version")
        prev_version = data.get("previous_version")
        
        if not current_version or not prev_version:
            raise InvalidStateTransitionError("No previous version recorded for rollback.")
            
        # Move current to rolled_back
        self.promote_model(current_version, registry_config.STATE_PRODUCTION, registry_config.STATE_ROLLED_BACK)
        
        # Re-activate previous (Assuming previous is still in production folder physically, 
        # but if we strictly move them out, we should move it back. 
        # Typically old production models stay in 'production' or 'archived'.
        # Let's assume they stay in production but the pointer shifts, OR we bring it back from archived.
        
        # Ensure prev_version is physically in production
        prev_prod_path = os.path.join(self.base_path, registry_config.STATE_PRODUCTION, prev_version)
        if not os.path.exists(prev_prod_path):
            # Try to recover from archived
            archived_path = os.path.join(self.base_path, registry_config.STATE_ARCHIVED, prev_version)
            if os.path.exists(archived_path):
                shutil.move(archived_path, prev_prod_path)
            else:
                raise MissingArtifactError(f"Previous version {prev_version} cannot be found to rollback.")
                
        # Update Pointer
        with open(self.active_pointer_path, "w") as f:
            json.dump({
                "active_version": prev_version,
                "previous_version": None, # We don't store double history here for simplicity
                "updated_at": pd.Timestamp.utcnow().isoformat(),
                "rollback_event": True
            }, f, indent=4)
            
        return prev_version

    def get_active_model(self) -> Dict[str, str]:
        """Returns the paths for the active production model artifacts."""
        if not os.path.exists(self.active_pointer_path):
            raise FileNotFoundError("No active production model is set.")
            
        with open(self.active_pointer_path, "r") as f:
            data = json.load(f)
            
        active_version = data.get("active_version")
        prod_dir = os.path.join(self.base_path, registry_config.STATE_PRODUCTION, active_version)
        
        # Double check integrity before serving to inference
        self._verify_integrity(active_version, registry_config.STATE_PRODUCTION)
        
        manifest_path = os.path.join(prod_dir, "manifest.json")
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            
        authenticity = manifest.get("authenticity", "UNKNOWN")
        if "PLACEHOLDER" in authenticity or "LEGACY" in authenticity:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"REGISTRY WARNING: Bootstrapping model version {active_version} with authenticity: {authenticity}. This is not a native production-trained artifact.")
            
        model_filename = manifest.get("model_file", "best_model.keras")

        return {
            "model_path": os.path.join(prod_dir, model_filename),
            "scaler_path": os.path.join(prod_dir, "feature_scaler.pkl"),
            "calibrator_path": os.path.join(prod_dir, "calibrator.pkl"),
            "version": active_version,
            "authenticity": authenticity,
            "manifest_data": manifest
        }
