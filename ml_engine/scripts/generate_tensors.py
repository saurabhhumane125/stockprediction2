"""
ml_engine/scripts/generate_tensors.py
─────────────────────────────────────────────────────────────────────────────
CLI for generating production Tensor Datasets.
─────────────────────────────────────────────────────────────────────────────
"""
import argparse
import logging
import sys

from ml_engine.data.tensors.builder import TensorBuilder
from ml_engine.config.training_config import training_config

def main():
    parser = argparse.ArgumentParser(description="Generate PyTorch Tensor Datasets")
    
    parser.add_argument("--dataset", type=str, required=True, help="Dataset version e.g. CORE/v1.0")
    parser.add_argument("--output", type=str, default="ml_engine/data/tensors", help="Output directory")
    
    # Overrides
    parser.add_argument("--sequence-length", type=int, help="Override seq_len in config")
    
    # Execution modes
    parser.add_argument("--force", action="store_true", help="Overwrite existing tensors")
    parser.add_argument("--resume", action="store_true", help="Skip if metadata.json exists")
    parser.add_argument("--dry-run", action="store_true", help="Run logic without saving")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    logger = logging.getLogger("TensorCLI")
    
    if args.sequence_length:
        training_config.SEQUENCE_LENGTH = args.sequence_length
        logger.info(f"[CLI] Overriding SEQUENCE_LENGTH to {args.sequence_length}")
        
    try:
        if args.dry_run:
            logger.info("[CLI] Dry-run enabled. The builder handles it internally via the force/resume patterns, but we will execute the build in a temporary way.")
            # We just bypass the actual build save if we want a true dry run, but the prompt says 
            # "Dry-run: Run logic without saving". We can monkeypatch TensorSerializer.
            from ml_engine.data.tensors.serializer import TensorSerializer
            TensorSerializer.save = lambda *a, **k: logger.info("[CLI] Dry-run: Skipping tensor save.")
            
        TensorBuilder.build_all(args.dataset, output_base=args.output, force=args.force, resume=args.resume)
        logger.info("[CLI] Tensor generation completed successfully.")
    except Exception as e:
        logger.error(f"[CLI] Tensor generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
