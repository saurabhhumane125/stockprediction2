import logging
from typing import List, Tuple
from app.schemas import VisionFeatureSet
from app.core.model_loader import ml_adapter

logger = logging.getLogger(__name__)

class CompatibilityValidator:
    """
    Validates VisionFeatureSet properties against the active ProductionInferenceEngine registry metadata.
    Prevents inference crashing dynamically.
    """
    def validate(self, feature_set: VisionFeatureSet) -> Tuple[bool, List[str]]:
        errors = []
        
        if not feature_set.is_valid:
            errors.append("Feature set is already marked as invalid.")
            
        if not ml_adapter.is_available or not ml_adapter.inference_engine:
            errors.append("ProductionInferenceEngine is unavailable.")
            return False, errors
            
        engine = ml_adapter.inference_engine
        
        # Determine active constraints
        expected_seq_len = getattr(engine, "sequence_length", 48)
        expected_feat_count = getattr(engine, "feature_count", 20)
        
        # Verify sequence length (features array shape should be [seq_length + 1, feature_count] ideally 
        # because the prediction logic converts to sequences. But let's check basic lengths.)
        if not feature_set.features:
            errors.append("Feature set contains no rows.")
        else:
            row_count = len(feature_set.features)
            
            # The engine builds sequences of expected_seq_len. It needs at least expected_seq_len rows.
            if row_count < expected_seq_len:
                errors.append(f"Insufficient history. Engine requires {expected_seq_len} rows, but only {row_count} provided.")
                
            col_count = len(feature_set.features[0])
            if col_count != expected_feat_count:
                errors.append(f"Feature count mismatch. Engine requires {expected_feat_count}, received {col_count}.")
                
            # Verify feature names count
            if len(feature_set.feature_names) != expected_feat_count:
                errors.append(f"Feature names mismatch. Engine requires {expected_feat_count}, received {len(feature_set.feature_names)}.")
                
        is_compatible = len(errors) == 0
        if not is_compatible:
            logger.error(f"Compatibility validation failed: {errors}")
            
        return is_compatible, errors

compatibility_validator = CompatibilityValidator()
