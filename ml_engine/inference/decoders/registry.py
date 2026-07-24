from typing import Dict, Type
from ml_engine.inference.decoders.base import BaseInferenceDecoder

class DecoderRegistry:
    """
    Registry for Inference Decoders.
    Manages registration and discovery of prediction decoding logic.
    """
    _decoders: Dict[str, Type[BaseInferenceDecoder]] = {}

    @classmethod
    def register(cls, decoder_class: Type[BaseInferenceDecoder]):
        """Registers a decoder class, ensuring unique name and version combinations."""
        # Instantiate temporarily to get name and version properties
        temp_instance = decoder_class()
        key = f"{temp_instance.strategy_name}@{temp_instance.strategy_version}"
        
        if key in cls._decoders:
            raise ValueError(f"Inference Decoder {key} is already registered.")
            
        cls._decoders[key] = decoder_class

    @classmethod
    def get(cls, name: str, version: str) -> Type[BaseInferenceDecoder]:
        """Resolves and returns a registered decoder class."""
        key = f"{name}@{version}"
        if key not in cls._decoders:
            raise KeyError(f"Inference Decoder {key} not found in registry.")
        return cls._decoders[key]

    @classmethod
    def clear(cls):
        """Clears the registry (useful for testing)."""
        cls._decoders.clear()
