"""
ml_engine/scripts/generate_dataset.py
─────────────────────────────────────────────────────────────────────────────
Orchestrates the Production Dataset Generation pipeline.
Executes strict flow:
Universe -> Downloader -> Validation -> Cleaner -> Feature Gen -> Validation -> Storage -> Metadata -> Reports
─────────────────────────────────────────────────────────────────────────────
"""
import argparse
import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pandas as pd

from ml_engine.data.universe.manager import UniverseManager
from ml_engine.data.download.parallel_downloader import ParallelDownloadEngine
from ml_engine.data.validation.validators import ProductionDataValidator
from ml_engine.data.preprocess.cleaner import ProductionCleaner
from ml_engine.data.features.generator import FeatureGenerator
from ml_engine.data.storage.parquet_partitioner import PartitionedParquetStorage
from ml_engine.data.reports.data_quality import DataQualityReportBuilder


# Configure structured logging for the script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("DatasetGenerator")


def generate_manifest(
    output_dir: str,
    universe: str,
    dataset_version: str,
    stats: dict,
    checksum: str,
    tickers: list
) -> str:
    """Generates the manifest.json file."""
    manifest = {
        "dataset_version": dataset_version,
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "universe": universe,
        "ticker_list": tickers,
        "checksums": checksum,
        "dataset_statistics": stats
    }
    
    path = os.path.join(output_dir, universe, dataset_version, "manifest.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(manifest, f, indent=4)
        
    return path


def main():
    parser = argparse.ArgumentParser(description="Production Dataset Generator")
    parser.add_argument("--universe", type=str, required=True, help="Universe name (e.g., CORE)")
    parser.add_argument("--dataset-version", type=str, required=True, help="Version (e.g., v1.0)")
    parser.add_argument("--start-date", type=str, required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", type=str, required=True, help="YYYY-MM-DD")
    parser.add_argument("--workers", type=int, default=5, help="Parallel download workers")
    parser.add_argument("--force-full-refresh", action="store_true", help="Ignore existing data and download all")
    parser.add_argument("--output-directory", type=str, default="ml_engine/data/storage/datasets", help="Root storage directory")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to disk")
    
    args = parser.parse_args()
    
    global_start_time = time.time()
    
    # Initialize Components
    storage = PartitionedParquetStorage(args.output_directory)
    downloader = ParallelDownloadEngine(max_workers=args.workers)
    cleaner = ProductionCleaner()
    feat_gen = FeatureGenerator()
    validator = ProductionDataValidator(dataset_version=args.dataset_version)
    
    stats = {
        "total_rows_downloaded": 0,
        "total_rows_cleaned": 0,
        "total_rows_removed": 0,
        "total_rows_final": 0,
        "features_generated": 0,
        "missing_values_imputed": 0,
        "execution_time_seconds": 0,
        "rows_per_ticker": {},
        "failed_tickers": []
    }

    # 1. Universe
    logger.info("=== STAGE 1: Universe Resolution ===")
    tickers = UniverseManager.get_universe(args.universe)
    logger.info(f"Resolved {len(tickers)} tickers.")
    
    # Determine date ranges per ticker
    download_tasks = {}
    end_dt = pd.to_datetime(args.end_date).tz_localize(None)
    
    for t in tickers:
        if args.force_full_refresh:
            download_tasks[t] = (args.start_date, args.end_date)
        else:
            latest = storage.get_latest_date(args.universe, args.dataset_version, t)
            if latest is None:
                download_tasks[t] = (args.start_date, args.end_date)
            else:
                next_day = latest + timedelta(days=1)
                if next_day <= end_dt:
                    download_tasks[t] = (next_day.strftime("%Y-%m-%d"), args.end_date)
                else:
                    logger.info(f"[{t}] Up to date. Skipping download.")
                    # Keep track of existing rows if not downloading
                    existing_df = storage.read_partition(args.universe, args.dataset_version, t)
                    stats["rows_per_ticker"][t] = len(existing_df)
                    stats["total_rows_final"] += len(existing_df)
                    
    if not download_tasks:
        logger.info("All tickers are up to date. Exiting.")
        sys.exit(0)

    # Group by date ranges to utilize ParallelDownloadEngine optimally
    date_groups = {}
    for t, dates in download_tasks.items():
        if dates not in date_groups:
            date_groups[dates] = []
        date_groups[dates].append(t)

    # 2. Downloader
    logger.info("=== STAGE 2: Downloader ===")
    raw_data_dict = {}
    
    t0_dl = time.time()
    for (s_date, e_date), grp_tickers in date_groups.items():
        results = downloader.download_parallel(grp_tickers, s_date, e_date)
        raw_data_dict.update(results)
        
    stats["download_throughput_s"] = time.time() - t0_dl
    
    # Process each ticker sequentially through pipeline to ensure Fail-Fast
    logger.info("=== STAGE 3-7: Pipeline Execution ===")
    
    t0_pipe = time.time()
    for ticker, raw_df in raw_data_dict.items():
        if raw_df.empty:
            logger.warning(f"[{ticker}] No data downloaded.")
            stats["failed_tickers"].append(ticker)
            continue
            
        stats["total_rows_downloaded"] += len(raw_df)
        
        # 3. Validation (raw_ohlc)
        is_valid, report_raw = validator.validate(raw_df, "raw_ohlc")
        if not is_valid:
            logger.error(f"[{ticker}] Raw OHLC Validation FAILED.")
            stats["failed_tickers"].append(ticker)
            sys.exit(1) # Fail-fast requirement
            
        # 4. Cleaner
        pre_clean_len = len(raw_df)
        clean_df = cleaner.clean(raw_df)
        post_clean_len = len(clean_df)
        stats["total_rows_cleaned"] += post_clean_len
        stats["total_rows_removed"] += (pre_clean_len - post_clean_len)
        
        if clean_df.empty:
            logger.warning(f"[{ticker}] Cleaner removed all rows.")
            stats["failed_tickers"].append(ticker)
            continue
            
        # 5. Feature Generation
        feat_df = feat_gen.generate_all_features(clean_df)
        
        # 6. Feature Validation
        is_valid_feat, report_feat = validator.validate(feat_df, "engineered_features")
        if not is_valid_feat:
            logger.error(f"[{ticker}] Engineered Features Validation FAILED.")
            stats["failed_tickers"].append(ticker)
            sys.exit(1) # Fail-fast requirement
            
        stats["features_generated"] = len(feat_df.columns)
        stats["rows_per_ticker"][ticker] = len(feat_df)
        stats["total_rows_final"] += len(feat_df)
        
        # 7. Partitioned Storage
        if not args.dry_run:
            storage.write_partition(
                df=feat_df,
                universe=args.universe,
                dataset_version=args.dataset_version,
                ticker=ticker,
                mode="append" if not args.force_full_refresh else "overwrite"
            )
            logger.info(f"[{ticker}] Partition saved. Rows: {len(feat_df)}")
            
    stats["pipeline_throughput_s"] = time.time() - t0_pipe
    
    # If Dry Run, exit early
    if args.dry_run:
        logger.info("Dry run complete. Exiting.")
        sys.exit(0)
        
    # 8. Metadata / Manifest
    logger.info("=== STAGE 8: Metadata & Manifest ===")
    checksum = storage.generate_checksum(args.universe, args.dataset_version)
    
    stats["execution_time_seconds"] = time.time() - global_start_time
    
    manifest_path = generate_manifest(
        output_dir=args.output_directory,
        universe=args.universe,
        dataset_version=args.dataset_version,
        stats=stats,
        checksum=checksum,
        tickers=tickers
    )
    logger.info(f"Manifest written to: {manifest_path}")

    # 9. Quality Reports
    logger.info("=== STAGE 9: Quality Reports ===")
    report_builder = DataQualityReportBuilder(storage, os.path.join(args.output_directory, "reports"))
    report_builder.build_report(args.universe, args.dataset_version, tickers)
    
    logger.info("=== Dataset Generation Complete ===")
    for k, v in stats.items():
        if not isinstance(v, (dict, list)):
            logger.info(f"  {k}: {v}")

if __name__ == "__main__":
    main()
