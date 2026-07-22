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
    
    parser.add_argument("--extract", action="store_true", help="Extract execution package from Drive")
    parser.add_argument("--check-deps", action="store_true", help="Check and install missing Colab dependencies")
    parser.add_argument("--sync-exports", action="store_true", help="Sync artifacts back to Drive")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    logger = logging.getLogger("ColabCLI")
    
    try:
        from ml_engine.colab.manifest_manager import ManifestManager
        from ml_engine.colab.orchestrator import PackageOrchestrator
        from ml_engine.colab.dependency_manager import DependencyManager
        from ml_engine.colab.artifact_sync import ArtifactSynchronizer
        
        if args.lock_env:
            logger.info("Environment locking is handled statically via requirements-training.txt at the repository root.")
            
        if args.generate_manifest:
            ManifestManager.generate_manifest(args.generate_manifest)
            
        if args.verify_env:
            # We need the dataset version to verify, assume it was provided in generate-manifest or validate
            dv = args.validate or args.generate_manifest or "UNKNOWN"
            ManifestManager.verify(dv)
            
        if args.mount:
            from ml_engine.colab.drive_manager import DriveManager
            DriveManager.mount()
            
        if args.extract:
            PackageOrchestrator.extract_safely()
            
        if args.check_deps:
            DependencyManager.check_and_install()
            
        if args.sync_exports:
            ArtifactSynchronizer.sync_to_drive()
            
        if args.validate:
            ColabBootstrap.setup(args.validate)
            
        if args.package:
            if not args.dry_run:
                PackageBuilder.build()
            else:
                logger.info("[ColabCLI] Dry-run: Skipping zip building.")
                
        if not any([args.validate, args.package, args.mount, args.extract, args.check_deps, args.sync_exports, args.generate_manifest, args.verify_env, args.lock_env]):
            logger.info("No action requested. Check --help.")
            
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
