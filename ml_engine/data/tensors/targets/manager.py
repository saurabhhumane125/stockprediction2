from typing import Any
from ml_engine.data.tensors.targets.base import BaseTargetStrategy
from ml_engine.data.tensors.targets.registry import StrategyRegistry

# Import all strategies and decoders to ensure they are registered
import ml_engine.data.tensors.targets.strategies.legacy
import ml_engine.data.tensors.targets.strategies.vol_adjusted

class TargetManager:
    """
    Orchestrator for the Target Strategy Framework.
    Resolves strategies and decoders from their respective registries.
    """

    @staticmethod
    def get_strategy(config: Any) -> BaseTargetStrategy:
        """
        Resolves the target strategy instance from the training configuration.
        """
        # Ensure fallback for legacy configurations missing the explicit strategy fields
        strategy_name = getattr(config.target, "strategy_name", "legacy")
        strategy_version = getattr(config.target, "strategy_version", "1.0")
        
        strategy_class = StrategyRegistry.get(strategy_name, strategy_version)
        return strategy_class()

    @staticmethod
    def get_decoder(metadata: dict) -> 'BaseInferenceDecoder':
        """
        Resolves the inference decoder instance from the model's metadata.
        """
        from ml_engine.inference.decoders.base import BaseInferenceDecoder
        from ml_engine.inference.decoders.registry import DecoderRegistry
        import ml_engine.inference.decoders.legacy_decoder
        import ml_engine.inference.decoders.vol_adjusted_decoder
        
        # Ensure fallback for existing registry models missing explicit strategy metadata
        strategy_name = metadata.get("strategy_name", "legacy")
        strategy_version = metadata.get("strategy_version", "1.0")
        
        decoder_class = DecoderRegistry.get(strategy_name, strategy_version)
        return decoder_class()
