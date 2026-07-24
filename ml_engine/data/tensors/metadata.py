"""
ml_engine/data/tensors/metadata.py
─────────────────────────────────────────────────────────────────────────────
Generates metadata for the tensor datasets.
─────────────────────────────────────────────────────────────────────────────
"""
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from ml_engine.config.training_config import training_config
from ml_engine.colab.manifest_manager import ManifestManager

logger = logging.getLogger(__name__)


class MetadataGenerator:
    """Generates schema and statistics JSON for serialized tensors."""

    @staticmethod
    def generate(
        dataset_version: str, 
        feature_cols: List[str],
        train_shape: tuple,
        val_shape: tuple,
        test_shape: tuple,
        y_train_dist: dict,
        scaler_info: dict = None
    ) -> Dict[str, Any]:
        """
        Creates the metadata dictionary tracking sizes, shapes, and features.
        """
        logger.info("[Metadata] Generating tensor metadata...")
        
        metadata = {
            "dataset_version": dataset_version,
            "generation_timestamp": datetime.utcnow().isoformat() + "Z",
            "sequence_length": training_config.SEQUENCE_LENGTH,
            "features": {
                "count": len(feature_cols),
                "order": feature_cols
            },
            "task_type": training_config.target.task_type.value,
            "target_type": training_config.target.target_type,
            "forecast_horizons": training_config.target.horizons,
            "primary_horizon": training_config.target.primary_horizon,
            "output_schema": {
                "shape": [len(training_config.target.horizons)] if training_config.target.task_type.value == "MULTI_OUTPUT_REGRESSION" else [1]
            },
            "dimensions": {
                "train_samples": train_shape[0],
                "val_samples": val_shape[0],
                "test_samples": test_shape[0]
            },
            "statistics": {
                "target_distribution_train": y_train_dist
            },
            "configuration_hash": ManifestManager._compute_config_hash(),
        }
        
        if scaler_info:
            metadata["preprocessing"] = scaler_info
            
        return metadata
