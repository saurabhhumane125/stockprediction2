import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Global settings for the ML Engine.
    All properties can be overridden by environment variables prefixed with 'ML_'.
    Example: ML_LOG_LEVEL="DEBUG"
    """
    
    LOG_LEVEL: str = Field(default="INFO", description="Global logging level")
    
    # Base paths
    _default_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    DATASETS_DIR: str = Field(
        default=os.path.join(_default_root, "data", "datasets"),
        description="Path to store versioned production datasets"
    )
    
    ARTIFACTS_DIR: str = Field(
        default=os.path.join(_default_root, "artifacts"),
        description="Path to store trained models and scalers"
    )
    
    CACHE_DIR: str = Field(
        default=os.path.join(_default_root, "data", "cache"),
        description="Path for temporary or cached raw downloads"
    )
    
    class Config:
        env_prefix = "ML_"
        case_sensitive = True


# Global singleton instance
settings = Settings()
