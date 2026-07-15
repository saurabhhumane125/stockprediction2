"""
ml_engine/data/etl/metadata_manager.py
─────────────────────────────────────────────────────────────────────────────
Manages dataset versioning and metadata persistence.
─────────────────────────────────────────────────────────────────────────────
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MetadataManager:
    """
    Handles generation and storage of dataset metadata.
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        os.makedirs(self.root_dir, exist_ok=True)

    def write_metadata(
        self,
        universe: str,
        dataset_version: str,
        tickers: List[str],
        config_hash: str,
        data_checksum: str,
        additional_info: Dict[str, Any] = None
    ) -> str:
        """
        Write metadata.json alongside the partitioned dataset.
        """
        metadata = {
            "dataset_version": dataset_version,
            "universe": universe,
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            "ticker_count": len(tickers),
            "configuration_hash": config_hash,
            "data_checksum": data_checksum,
            "source": "YFinanceDownloader",
            "tickers": tickers
        }
        
        if additional_info:
            metadata.update(additional_info)
            
        base_dir = os.path.join(self.root_dir, universe, dataset_version)
        os.makedirs(base_dir, exist_ok=True)
        
        file_path = os.path.join(base_dir, "metadata.json")
        with open(file_path, "w") as f:
            json.dump(metadata, f, indent=4)
            
        logger.info(f"[MetadataManager] Metadata written to {file_path}")
        return file_path

    def read_metadata(self, universe: str, dataset_version: str) -> Dict[str, Any]:
        """
        Load metadata.json for a dataset.
        """
        file_path = os.path.join(self.root_dir, universe, dataset_version, "metadata.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No metadata found at {file_path}")
            
        with open(file_path, "r") as f:
            return json.load(f)
