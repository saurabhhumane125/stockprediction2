from typing import Dict, Type
from ml_engine.data.tensors.targets.base import BaseTargetStrategy

class StrategyRegistry:
    """
    Registry for Target Strategies.
    Manages registration and discovery of target generation logic.
    """
    _strategies: Dict[str, Type[BaseTargetStrategy]] = {}

    @classmethod
    def register(cls, strategy_class: Type[BaseTargetStrategy]):
        """Registers a strategy class, ensuring unique name and version combinations."""
        # Instantiate temporarily to get name and version properties
        temp_instance = strategy_class()
        key = f"{temp_instance.strategy_name}@{temp_instance.strategy_version}"
        
        if key in cls._strategies:
            raise ValueError(f"Target Strategy {key} is already registered.")
            
        cls._strategies[key] = strategy_class

    @classmethod
    def get(cls, name: str, version: str) -> Type[BaseTargetStrategy]:
        """Resolves and returns a registered strategy class."""
        key = f"{name}@{version}"
        if key not in cls._strategies:
            raise KeyError(f"Target Strategy {key} not found in registry.")
        return cls._strategies[key]

    @classmethod
    def clear(cls):
        """Clears the registry (useful for testing)."""
        cls._strategies.clear()
