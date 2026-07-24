from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class BaseInferenceDecoder(ABC):
    """
    Abstract base class for all inference prediction decoders.
    Decodes raw model output tensors into human-readable business logic.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Returns the unique name of the target strategy this decoder supports."""
        pass

    @property
    @abstractmethod
    def strategy_version(self) -> str:
        """Returns the version of the target strategy this decoder supports."""
        pass

    @abstractmethod
    def decode(self, raw_prediction: float, current_features: pd.Series, metadata: dict, calibrator: Any = None) -> Dict[str, Any]:
        """
        Translates the raw model scalar back into actual expected returns or signals.
        
        Args:
            raw_prediction: The raw scalar output from the neural network.
            current_features: A Pandas Series containing the latest features (useful for un-scaling).
            metadata: The registry metadata describing the model's target schema.
            calibrator: Optional calibrator object for classification.
            
        Returns:
            The decoded business-logic prediction dictionary.
        """
        pass
