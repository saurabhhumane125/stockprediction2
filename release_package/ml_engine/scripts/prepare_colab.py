"""
ml_engine/scripts/prepare_colab.py
─────────────────────────────────────────────────────────────────────────────
CLI for preparing the Google Colab Execution Package.
─────────────────────────────────────────────────────────────────────────────
"""
import argparse
import logging
import sys

from ml_engine.colab.bootstrap import ColabBootstrap
from ml_engine.colab.package_builder import PackageBuilder
from ml_engine.colab.drive_manager import DriveManager

def main():
    parser = argparse.ArgumentParser(description="Prepare Colab Execution")
    
    parser.add_argument("--validate", type=str, help="Validate dataset and env (pass dataset version)")
    parser.add_argument("--package", action="store_true", help="Build execution zip package")
    parser.add_argument("--mount", action="store_true", help="Mount Google Drive (only works in Colab)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without modifying anything")
    
    parser.add_argument("--lock-env", action="store_true", help="Generate or update requirements-training.txt lock file")
    parser.add_argument("--verify-env", action="store_true", help="Verify current environment against execution_manifest.json")
    parser.add_argument("--generate-manifest", type=str, help="Generate execution_manifest.json (pass dataset version)")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    logger = logging.getLogger("ColabCLI")
    
    try:
        from ml_engine.colab.manifest_manager import ManifestManager
        
        if args.lock_env:
            logger.info("Environment locking is handled statically via requirements-training.txt at the repository root.")
            
        if args.generate_manifest:
            ManifestManager.generate_manifest(args.generate_manifest)
            
        if args.verify_env:
            # We need the dataset version to verify, assume it was provided in generate-manifest or validate
            dv = args.validate or args.generate_manifest or "UNKNOWN"
            ManifestManager.verify(dv)
        if args.mount:
            DriveManager.mount()
            
        if args.validate:
            ColabBootstrap.setup(args.validate)
            
        if args.package:
            if not args.dry_run:
                PackageBuilder.build()
            else:
                logger.info("[ColabCLI] Dry-run: Skipping zip building.")
                
        if not any([args.validate, args.package, args.mount]):
            logger.info("No action requested. Use --validate, --package, or --mount.")
            
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
