"""
ml_engine/data/tensors/validator.py
─────────────────────────────────────────────────────────────────────────────
Validates generated PyTorch tensors for ML integrity.
─────────────────────────────────────────────────────────────────────────────
"""
import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


from ml_engine.core.types import TaskType

class TensorValidator:
    """Validates PyTorch tensors before serialization."""

    @staticmethod
    def validate(X: np.ndarray, y: np.ndarray, expected_features: int, expected_seq_len: int, task_type: TaskType = TaskType.BINARY_CLASSIFICATION) -> bool:
        """
        Validates the integrity of the generated tensors.
        """
        try:
            # 1. Shapes
            if X.shape[0] != y.shape[0]:
                logger.error(f"[Validator] Dimension mismatch: X={X.shape[0]}, y={y.shape[0]}")
                return False
                
            if X.shape[0] > 0:
                if X.shape[1] != expected_seq_len:
                    logger.error(f"[Validator] Sequence length mismatch: got {X.shape[1]}, expected {expected_seq_len}")
                    return False
                    
                if X.shape[2] != expected_features:
                    logger.error(f"[Validator] Feature count mismatch: got {X.shape[2]}, expected {expected_features}")
                    return False

            # 2. NaNs / Infs
            if np.isnan(X).any() or np.isnan(y).any():
                logger.error("[Validator] NaNs detected in tensors.")
                return False
                
            if np.isinf(X).any() or np.isinf(y).any():
                logger.error("[Validator] Infs detected in tensors.")
                return False
                
            # 3. Label integrity
            if task_type == TaskType.BINARY_CLASSIFICATION:
                unique_labels = np.unique(y)
                if not np.all(np.isin(unique_labels, [0, 1])):
                    logger.error(f"[Validator] Invalid labels detected: {unique_labels}. Expected binary [0, 1].")
                    return False
            elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
                # Ensure labels are integers and no NaNs/Infs (already checked)
                if not np.array_equal(y, y.astype(int)):
                    logger.error("[Validator] Invalid multiclass labels: expected integers.")
                    return False
            elif task_type in (TaskType.REGRESSION, TaskType.MULTI_OUTPUT_REGRESSION):
                if y.dtype == object:
                    logger.error("[Validator] Invalid regression labels: expected numeric type, got object dtype.")
                    return False
                
            return True
        except Exception as e:
            logger.error(f"[Validator] Validation crashed: {e}")
            return False
