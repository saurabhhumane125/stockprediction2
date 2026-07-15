"""
ml_engine/data/etl/incremental_updater.py
─────────────────────────────────────────────────────────────────────────────
Orchestrates incremental dataset downloads and storage.
─────────────────────────────────────────────────────────────────────────────
"""
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import pandas as pd

from ml_engine.data.download.parallel_downloader import ParallelDownloadEngine
from ml_engine.data.storage.parquet_partitioner import PartitionedParquetStorage
from ml_engine.data.etl.metadata_manager import MetadataManager
from ml_engine.data.universe.manager import UniverseManager

logger = logging.getLogger(__name__)


class IncrementalETLManager:
    """
    Manages the incremental data pipeline.
    """
    
    def __init__(self, root_dir: str):
        self.storage = PartitionedParquetStorage(root_dir)
        self.metadata = MetadataManager(root_dir)
        self.downloader = ParallelDownloadEngine(max_workers=5, max_retries=3)

    def run_update(
        self,
        universe: str,
        dataset_version: str,
        global_start_date: str,
        global_end_date: str
    ) -> Dict[str, str]:
        """
        Run an idempotent, incremental update for the specified universe.
        """
        logger.info(f"[IncrementalETL] Starting update for universe '{universe}' (version: {dataset_version})")
        
        tickers = UniverseManager.get_universe(universe)
        
        # 1. Determine Delta Periods per Ticker
        download_tasks = self._plan_downloads(tickers, universe, dataset_version, global_start_date, global_end_date)
        
        # 2. Execute Downloads (grouping by date ranges to batch efficiently)
        # For simplicity in incremental logic, we can group tickers that need the same date range,
        # or just fetch per ticker using the parallel downloader.
        # To reuse ParallelDownloadEngine directly, we group tickers by (start, end).
        
        groups = {}
        for t, (start, end) in download_tasks.items():
            key = (start, end)
            if key not in groups:
                groups[key] = []
            groups[key].append(t)
            
        logger.info(f"[IncrementalETL] Planned {len(download_tasks)} downloads across {len(groups)} distinct date windows.")
        
        for (start, end), group_tickers in groups.items():
            results = self.downloader.download_parallel(group_tickers, start, end)
            
            # 3. Store Results
            for t, df in results.items():
                if not df.empty:
                    self.storage.write_partition(
                        df=df,
                        universe=universe,
                        dataset_version=dataset_version,
                        ticker=t,
                        mode="append"
                    )
        
        # 4. Verification and Metadata
        checksum = self.storage.generate_checksum(universe, dataset_version)
        config_hash = self._generate_config_hash(tickers, global_start_date, global_end_date)
        
        meta_path = self.metadata.write_metadata(
            universe=universe,
            dataset_version=dataset_version,
            tickers=tickers,
            config_hash=config_hash,
            data_checksum=checksum
        )
        
        logger.info(f"[IncrementalETL] Update complete. Checksum: {checksum}")
        return {"metadata_path": meta_path, "checksum": checksum}

    def _plan_downloads(
        self,
        tickers: List[str],
        universe: str,
        dataset_version: str,
        global_start_date: str,
        global_end_date: str
    ) -> Dict[str, tuple]:
        """
        Calculates the required start and end date for each ticker based on existing data.
        Returns Dict[ticker, (start_date, end_date)].
        """
        tasks = {}
        
        global_end_dt = pd.to_datetime(global_end_date).tz_localize(None)
        
        for t in tickers:
            latest_date = self.storage.get_latest_date(universe, dataset_version, t)
            
            if latest_date is None:
                # Full download required
                tasks[t] = (global_start_date, global_end_date)
            else:
                # Incremental download required
                # Start from the day after the latest available data
                next_day = latest_date + timedelta(days=1)
                if next_day <= global_end_dt:
                    tasks[t] = (next_day.strftime("%Y-%m-%d"), global_end_date)
                else:
                    logger.debug(f"[IncrementalETL] Ticker {t} is already up-to-date (latest: {latest_date.strftime('%Y-%m-%d')}).")
                    
        return tasks

    def _generate_config_hash(self, tickers: List[str], start: str, end: str) -> str:
        s = "".join(sorted(tickers)) + start + end
        return hashlib.sha256(s.encode('utf-8')).hexdigest()
