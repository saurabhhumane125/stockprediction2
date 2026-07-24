from abc import ABC, abstractmethod
from typing import List, Tuple
import pandas as pd
from typing import Any

class BaseTargetStrategy(ABC):
    """
    Abstract base class for all target generation strategies.
    Generates targets from historical price data.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Returns the unique name of the strategy (e.g., 'legacy')."""
        pass

    @property
    @abstractmethod
    def strategy_version(self) -> str:
        """Returns the semantic version of the strategy (e.g., '1.0')."""
        pass

    @abstractmethod
    def get_target_cols(self, config: Any) -> List[str]:
        """
        Returns the exact list of target column names that will be generated.
        """
        pass

    @abstractmethod
    def generate(self, df: pd.DataFrame, config: Any) -> Tuple[pd.DataFrame, List[str]]:
        """
        Calculates mathematical targets from the dataframe.
        Returns the modified dataframe and the list of target columns.
        """
        pass
