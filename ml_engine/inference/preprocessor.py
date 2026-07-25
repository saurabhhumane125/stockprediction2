import logging
import numpy as np
import pandas as pd
from typing import Dict, Any

from ml_engine.data.features.generator import FeatureGenerator
from ml_engine.inference.exceptions import InferenceInputError

logger = logging.getLogger(__name__)

class LiveFeaturePipeline:
    """
    Dedicated ML Engine pipeline for live inference preprocessing.
    Ensures zero training-serving skew by invoking the exact same FeatureGenerator
    used during training.
    """
    
    def __init__(self, manifest: Dict[str, Any]):
        self.manifest = manifest
        self.feature_names = manifest.get("feature_names", [])
        if not self.feature_names:
            raise ValueError("Manifest does not contain 'feature_names'. Cannot build live features.")
            
        self.generator = FeatureGenerator()

    def process(self, raw_df: pd.DataFrame, market_data: Dict[str, pd.DataFrame] = None) -> np.ndarray:
        """
        Accepts raw OHLCV data, generates features, orders them, and handles NaNs.
        Returns a strict Numpy array ready for the Inference Engine.
        """
        # Ensure column names are standardized to match FeatureGenerator and Training Downloader
        raw_df = raw_df.copy()
        raw_df.columns = [str(c).lower().replace(" ", "_") for c in raw_df.columns]
        
        processed_market = {}
        if market_data:
            for k, v in market_data.items():
                v_copy = v.copy()
                v_copy.columns = [str(c).lower().replace(" ", "_") for c in v_copy.columns]
                processed_market[k] = v_copy
                
        try:
            # Generate all features using the canonical generator
            features_df = self.generator.generate_all_features(raw_df, market_data=processed_market)
        except Exception as e:
            raise InferenceInputError(f"Feature generation failed: {e}")
            
        # Reorder and filter columns exactly as training
        missing = [f for f in self.feature_names if f not in features_df.columns]
        
        if missing:
            raise InferenceInputError(f"FeatureGenerator failed to produce required features: {missing}")
            
        final_df = features_df[self.feature_names].copy()
        
        # Handle NaNs strictly
        if final_df.isna().any().any():
            logger.warning("NaNs detected after feature generation. Dropping affected rows.")
            final_df = final_df.dropna()
            
        if len(final_df) == 0:
            raise InferenceInputError("No valid rows remaining after feature generation and NaN dropping.")
            
        feature_tensor = final_df.to_numpy(dtype=np.float32)
        
        # Extract latest features for explanation/regime services
        latest_row = final_df.iloc[-1].to_dict()
        latest_features = {k: (float(v) if pd.notna(v) else None) for k, v in latest_row.items()}
        
        return feature_tensor, latest_features
