"""
ml_engine/data/storage/parquet_partitioner.py
─────────────────────────────────────────────────────────────────────────────
Manages Parquet file storage, partitioning, and checksums.
─────────────────────────────────────────────────────────────────────────────
"""
import hashlib
import logging
import os
from typing import Dict, List, Optional
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)


class PartitionedParquetStorage:
    """
    Handles partitioned Parquet storage for the expanded datasets.
    Layout: root_dir/<universe>/<dataset_version>/ticker=<ticker>/data.parquet
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        os.makedirs(self.root_dir, exist_ok=True)

    def write_partition(
        self,
        df: pd.DataFrame,
        universe: str,
        dataset_version: str,
        ticker: str,
        mode: str = "overwrite"
    ) -> str:
        """
        Write a single ticker's dataframe into its partition.
        
        Args:
            mode: "overwrite" or "append"
        """
        if df.empty:
            logger.debug(f"[ParquetStorage] Empty DataFrame for {ticker}, skipping write.")
            return ""
            
        partition_dir = os.path.join(self.root_dir, universe, dataset_version, f"ticker={ticker}")
        os.makedirs(partition_dir, exist_ok=True)
        file_path = os.path.join(partition_dir, "data.parquet")
        
        if mode == "append" and os.path.exists(file_path):
            existing_df = pd.read_parquet(file_path)
            # Combine and deduplicate by index (datetime)
            combined = pd.concat([existing_df, df])
            combined = combined[~combined.index.duplicated(keep='last')]
            combined.sort_index(inplace=True)
            df_to_write = combined
        else:
            df_to_write = df
            
        table = pa.Table.from_pandas(df_to_write)
        pq.write_table(table, file_path, compression='snappy')
        
        return file_path

    def read_partition(self, universe: str, dataset_version: str, ticker: str) -> pd.DataFrame:
        """
        Read a single ticker's data. Returns empty DataFrame if missing.
        """
        file_path = os.path.join(self.root_dir, universe, dataset_version, f"ticker={ticker}", "data.parquet")
        if not os.path.exists(file_path):
            return pd.DataFrame()
            
        return pd.read_parquet(file_path)
        
    def read_universe(self, universe: str, dataset_version: str) -> pd.DataFrame:
        """
        Read all partitions for a universe into a single DataFrame.
        """
        base_dir = os.path.join(self.root_dir, universe, dataset_version)
        if not os.path.exists(base_dir):
            return pd.DataFrame()
            
        dataset = pq.ParquetDataset(base_dir)
        return dataset.read().to_pandas()

    def get_latest_date(self, universe: str, dataset_version: str, ticker: str) -> Optional[pd.Timestamp]:
        """
        Find the latest timestamp in the existing partition for a ticker.
        """
        df = self.read_partition(universe, dataset_version, ticker)
        if df.empty:
            return None
        return df.index.max()

    def generate_checksum(self, universe: str, dataset_version: str) -> str:
        """
        Generate a SHA-256 checksum for the entire dataset directory to verify integrity.
        """
        base_dir = os.path.join(self.root_dir, universe, dataset_version)
        if not os.path.exists(base_dir):
            return ""
            
        hasher = hashlib.sha256()
        
        # Sort files to ensure deterministic hash
        files = []
        for root, dirs, filenames in os.walk(base_dir):
            for name in filenames:
                if name.endswith(".parquet"):
                    files.append(os.path.join(root, name))
        files.sort()
        
        for file_path in files:
            # Hash relative path to be environment independent
            rel_path = os.path.relpath(file_path, base_dir)
            hasher.update(rel_path.encode('utf-8'))
            
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
                    
        return hasher.hexdigest()
