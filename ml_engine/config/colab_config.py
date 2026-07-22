"""
ml_engine/config/colab_config.py
─────────────────────────────────────────────────────────────────────────────
Configuration loader for Colab execution settings.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import yaml
import logging

logger = logging.getLogger(__name__)


class ColabConfig:
    """Wrapper for colab.yaml configuration."""
    
    _config_data = {}
    _loaded = False
    
    @classmethod
    def load(cls, config_path: str = "ml_engine/config/colab.yaml"):
        if not cls._loaded:
            if not os.path.exists(config_path):
                logger.warning(f"[ColabConfig] Config not found at {config_path}. Using defaults.")
                cls._config_data = {
                    "project_root": "/content/drive/MyDrive/STOCK-PREDICTION",
                    "package_filename": "stockprediction_v2.zip",
                    "dataset_id": "NIFTY50/v2.0",
                    "experiment_name": "production_colab_run",
                    "datasets_location": "datasets",
                    "packages_location": "packages",
                    "registry_location": "ml_engine/model_registry",
                    "exports_location": "artifacts/exports",
                    "artifacts_location": "artifacts/candidates",
                    "logs_location": "artifacts/logs",
                    "device_selection_policy": "auto",
                    "resume_policy": "auto_resume",
                    "default_model": "GRU",
                    "default_epochs": 100,
                    "default_batch_size": 64
                }
            else:
                try:
                    import yaml
                    with open(config_path, "r") as f:
                        cls._config_data = yaml.safe_load(f) or {}
                except ImportError:
                    logger.warning("[ColabConfig] PyYAML not installed. Using defaults.")
            cls._loaded = True
            
    @classmethod
    def get(cls, key: str, default=None):
        if not cls._loaded:
            cls.load()
        return cls._config_data.get(key, default)

    @classmethod
    def get_project_root(cls) -> str:
        return cls.get("project_root", "/content/drive/MyDrive/STOCK-PREDICTION")
