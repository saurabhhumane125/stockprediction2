import argparse
import logging
import os
import sys
import tempfile
import json
import zipfile
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.append(project_root)

from ml_engine.registry.manager import RegistryManager
from ml_engine.config.registry_config import registry_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("DeployCLI")

def validate_bundle(extracted_dir: str, registry_manager: RegistryManager) -> dict:
    """
    Validates the deployment bundle strictly against the registry contract.
    Returns the manifest dictionary if valid.
    """
    logger.info("Validating deployment bundle transport integrity...")
    manifest_path = os.path.join(extracted_dir, "manifest.json")
    
    # 1. Manifest must exist
    if not os.path.exists(manifest_path):
        raise FileNotFoundError("Deployment bundle is missing 'manifest.json'.")
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    version = manifest.get("model_version")
    if not version:
        raise ValueError("manifest.json is missing 'model_version'.")
        
    artifacts = manifest.get("artifacts", {})
    if not artifacts:
        raise ValueError("manifest.json has no 'artifacts' listed.")

    # 2. Strict Contract Enforcement
    # We dynamically check the REQUIRED_ARTIFACTS defined by the RegistryConfig.
    # The 'model_file' is dynamically resolved from the manifest metadata.
    source_artifacts = {}
    for req in registry_config.REQUIRED_ARTIFACTS:
        actual_req = manifest.get("model_file") if req == "model_file" else req
        if not actual_req:
            raise ValueError("manifest.json is missing 'model_file' declaration.")
        
        file_path = os.path.join(extracted_dir, actual_req)
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Contract Violation: Required artifact '{actual_req}' is missing from the bundle."
            )

    # 3. Dynamic Artifact Validation & Transport Integrity Check
    # Justification: RegistryManager verifies integrity of installed models via _verify_integrity(),
    # but does NOT verify the ZIP payload over the network. This early SHA-256 validation guarantees 
    # the downloaded files exactly match the Colab export before any registry manipulation begins.
    for artifact_name, expected_hash in artifacts.items():
        file_path = os.path.join(extracted_dir, artifact_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Artifact referenced in manifest is missing: {artifact_name}")
            
        actual_hash = registry_manager._compute_hash(file_path)
        if actual_hash != expected_hash:
            raise ValueError(f"SHA-256 hash mismatch for {artifact_name}. Bundle was corrupted during transport.")
        
        source_artifacts[artifact_name] = file_path

    # Removed Duplicate Responsibilities:
    # We do NOT manually check for version conflicts or manipulate registry directories here.
    # RegistryManager.register_candidate() strictly owns conflict resolution and path management.

    logger.info(f"Transport validation successful. Bundle '{version}' is clean and uncorrupted.")
    return manifest, source_artifacts

def main():
    parser = argparse.ArgumentParser(description="Local Deployment Import Pipeline")
    parser.add_argument("--bundle", type=str, required=True, help="Path to the local deployment zip bundle")
    parser.add_argument("--dry-run", action="store_true", help="Perform all validations without making registry changes")
    parser.add_argument("--promote", type=str, choices=["staging", "production"], help="Automatically promote the model after ingestion")
    
    args = parser.parse_args()
    
    registry_path = os.path.join(project_root, "ml_data", "registry")
    registry_manager = RegistryManager(registry_base_path=registry_path)
    
    if not os.path.exists(args.bundle):
        logger.error(f"Bundle not found: {args.bundle}")
        sys.exit(1)
        
    if not zipfile.is_zipfile(args.bundle):
        logger.error(f"Provided file is not a valid zip archive: {args.bundle}")
        sys.exit(1)

    logger.info(f"Starting deployment for bundle: {args.bundle}")
    logger.info(f"Dry Run: {args.dry_run}")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Extracting bundle to temporary directory: {temp_dir}")
            with zipfile.ZipFile(args.bundle, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
            extracted_items = os.listdir(temp_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                base_extract = os.path.join(temp_dir, extracted_items[0])
            else:
                base_extract = temp_dir
                
            manifest, source_artifacts = validate_bundle(base_extract, registry_manager)
            version = manifest["model_version"]
            
            if args.dry_run:
                logger.info(f"[DRY-RUN] Would register candidate: {version}")
                if args.promote:
                    logger.info(f"[DRY-RUN] Would promote {version} to {args.promote}")
                logger.info("Dry-run completed successfully.")
                sys.exit(0)
                
            # Import Step
            logger.info(f"Importing version '{version}' into Candidate registry...")
                
            registry_manager.register_candidate(
                version=version,
                source_artifacts=source_artifacts,
                metadata=manifest,
                authenticity=manifest.get("authenticity", "REAL")
            )
            
            logger.info(f"Candidate '{version}' successfully registered.")
            
            # Promotion Step
            if args.promote in ["staging", "production"]:
                logger.info(f"Promoting '{version}' to staging...")
                registry_manager.promote_model(version, registry_config.STATE_CANDIDATE, registry_config.STATE_STAGING)
                
                if args.promote == "production":
                    logger.info(f"Promoting '{version}' to production...")
                    registry_manager.promote_model(version, registry_config.STATE_STAGING, registry_config.STATE_PRODUCTION)
                    logger.info("Production promotion complete. IMPORTANT: Restart the backend server for the model to take effect.")
                    
            logger.info("Deployment pipeline completed successfully.")
            
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
