"""
ml_engine/scripts/train_models.py
─────────────────────────────────────────────────────────────────────────────
CLI for the Production Retraining Pipeline.
─────────────────────────────────────────────────────────────────────────────
"""
import argparse
import sys
import logging
from ml_engine.training.runner import ProductionTrainingRunner


def main():
    parser = argparse.ArgumentParser(description="Production Training Pipeline CLI")
    
    parser.add_argument("--dataset", type=str, required=True, help="Dataset version to use (e.g., CORE/v1.0)")
    parser.add_argument("--config", type=str, default="default", help="Configuration profile")
    parser.add_argument("--model", type=str, default="GRU", help="Model architecture (GRU, BiGRU, LSTM, Transformer)")
    parser.add_argument("--resume", action="store_true", help="Resume from latest checkpoint")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--device", type=str, default="cuda", help="cuda or cpu")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment Name for Tracker")
    parser.add_argument("--dry-run", action="store_true", help="Validate and orchestrate without training")
    parser.add_argument("--export-only", action="store_true", help="Simulate export only")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    logger = logging.getLogger("TrainCLI")
    
    logger.info("Initializing ProductionTrainingRunner...")
    
    runner = ProductionTrainingRunner(
        dataset_version=args.dataset,
        experiment_name=args.experiment,
        model_type=args.model,
        resume=args.resume,
        dry_run=args.dry_run,
        export_only=args.export_only,
        epochs=args.epochs,
        batch_size=getattr(args, "batch_size", 64),
        device=args.device
    )
    
    try:
        results = runner.run()
        logger.info(f"Training pipeline completed successfully. Version: {results.get('version')}")
    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
