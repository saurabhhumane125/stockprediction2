from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseStorage(ABC):
    """
    Abstract interface for persisting and loading tabular datasets and metadata.
    Ensures storage mechanism remains decoupled from the pipeline logic, supporting
    local file systems, cloud storage (S3), or database storage dynamically.
    """

    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a dataset or file exists at the given path.
        
        Args:
            path (str): The destination path or URI.
            
        Returns:
            bool: True if it exists, False otherwise.
            
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def save_dataframe(self, df: pd.DataFrame, path: str) -> None:
        """
        Save tabular data to the specified path.
        
        Args:
            df (pd.DataFrame): The tabular data to persist.
            path (str): The destination path or URI.
            
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def load_dataframe(self, path: str) -> pd.DataFrame:
        """
        Load tabular data from the specified path.
        
        Args:
            path (str): The source path or URI.
            
        Returns:
            pd.DataFrame: The loaded tabular data.
            
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def save_metadata(self, metadata: Dict[str, Any], path: str) -> None:
        """
        Save versioning and execution metadata alongside the datasets.
        
        Args:
            metadata (Dict[str, Any]): A dictionary containing metadata key-value pairs.
            path (str): The destination path or URI.
            
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
