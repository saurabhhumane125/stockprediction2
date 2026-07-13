import os
import json
import logging
import pandas as pd
from typing import Dict, Any

from ml_engine.interfaces.base_storage import BaseStorage

logger = logging.getLogger(__name__)


class ParquetStorage(BaseStorage):
    """
    Production storage layer implementing BaseStorage for Parquet files.
    Ensures atomic writes, metadata sidecar creation, and efficient persistence.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def exists(self, path: str) -> bool:
        """
        Check if a file exists. For parquet, it checks the exact file path.
        """
        full_path = os.path.join(self.base_path, path)
        return os.path.exists(full_path)

    def save_dataframe(self, df: pd.DataFrame, path: str) -> None:
        """
        Save tabular data to parquet, ensuring atomic replacement.
        """
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write to temporary file first to guarantee atomicity
        temp_path = f"{full_path}.tmp"
        try:
            df.to_parquet(temp_path, engine="pyarrow", index=True)
            if os.path.exists(full_path):
                os.replace(temp_path, full_path)
            else:
                os.rename(temp_path, full_path)
            logger.info(f"Saved dataset to {full_path}")
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Failed to save dataset to {full_path}: {e}")
            raise

    def load_dataframe(self, path: str) -> pd.DataFrame:
        """
        Load tabular data from a parquet file.
        """
        full_path = os.path.join(self.base_path, path)
        if not self.exists(path):
            raise FileNotFoundError(f"Dataset not found at {full_path}")
        
        df = pd.read_parquet(full_path, engine="pyarrow")
        logger.info(f"Loaded dataset from {full_path}")
        return df

    def save_metadata(self, metadata: Dict[str, Any], path: str) -> None:
        """
        Save metadata as a JSON sidecar file next to the dataset.
        """
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        temp_path = f"{full_path}.tmp"
        try:
            with open(temp_path, "w") as f:
                json.dump(metadata, f, indent=4)
            if os.path.exists(full_path):
                os.replace(temp_path, full_path)
            else:
                os.rename(temp_path, full_path)
            logger.info(f"Saved metadata to {full_path}")
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Failed to save metadata to {full_path}: {e}")
            raise
