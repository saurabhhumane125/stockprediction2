from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Tuple


class BaseValidator(ABC):
    """
    Abstract interface for validating data against strict schemas and contracts.
    Ensures data quality constraints (missing values, extreme outliers, datatypes)
    are strictly met before the data is allowed downstream into training or inference.
    """

    @abstractmethod
    def validate(self, df: pd.DataFrame, schema_name: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate the provided tabular data against a defined schema contract.
        
        Args:
            df (pd.DataFrame): The data to validate.
            schema_name (str): The identifier of the schema/contract to enforce 
                               (e.g., 'raw_ohlc', 'engineered_features').
            
        Returns:
            Tuple[bool, Dict[str, Any]]: A boolean indicating if validation passed, 
                                         and a dictionary containing detailed validation reports or errors.
                                         
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
