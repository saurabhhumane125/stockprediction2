from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTrainer(ABC):
    """
    Abstract interface for executing model training pipelines.
    Ensures that different model architectures (GRU, LSTM, Transformer, TFT)
    can be trained, evaluated, and swapped seamlessly without modifying the overarching pipeline.
    """

    @abstractmethod
    def train(self, train_data: Any, val_data: Any, config: Dict[str, Any]) -> Any:
        """
        Execute the training loop using the provided datasets.
        
        Args:
            train_data (Any): The prepared training dataset (e.g., PyTorch DataLoaders, TF Datasets).
            val_data (Any): The prepared validation dataset for early stopping and metric tracking.
            config (Dict[str, Any]): A dictionary of training hyperparameters and configuration.
            
        Returns:
            Any: The trained model artifact/object in memory.
            
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, model: Any, test_data: Any) -> Dict[str, float]:
        """
        Evaluate the trained model on an out-of-sample testing dataset.
        
        Args:
            model (Any): The trained model artifact returned by train().
            test_data (Any): The out-of-sample testing dataset.
            
        Returns:
            Dict[str, float]: A dictionary mapping metric names (e.g., 'accuracy', 'sharpe') 
                              to their computed values.
                              
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
