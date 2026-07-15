"""
ml_engine/colab/execution_validator.py
─────────────────────────────────────────────────────────────────────────────
Validates the execution environment before starting a heavy training job.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import logging
from typing import List

logger = logging.getLogger(__name__)


class ExecutionValidator:
    """Validates paths, configs, and datasets before execution."""

    @staticmethod
    def validate_pre_flight(dataset_version: str) -> bool:
        """
        Runs pre-flight checks. Returns True if successful, False otherwise.
        """
        logger.info("=== Pre-flight Validation ===")
        checks_passed = True

        # 1. Dataset Check
        tensor_path = os.path.join("ml_engine/data/tensors", dataset_version)
        if not os.path.exists(tensor_path) or not os.path.exists(os.path.join(tensor_path, "metadata.json")) or not os.path.exists(os.path.join(tensor_path, "train.pt")):
            logger.error(f"[Validator] Dataset tensors missing at: {tensor_path}")
            checks_passed = False
        else:
            logger.info(f"[Validator] Dataset found: {tensor_path}")

        # 2. Registry Check
        registry_path = "ml_engine/model_registry"
        if not os.path.exists(registry_path):
            logger.error(f"[Validator] Registry path missing: {registry_path}")
            checks_passed = False
        else:
            logger.info(f"[Validator] Registry found: {registry_path}")

        # 3. Output Folder Permissions
        candidates_dir = "artifacts/candidates"
        try:
            os.makedirs(candidates_dir, exist_ok=True)
            test_file = os.path.join(candidates_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            logger.info("[Validator] Output folders are writable.")
        except Exception as e:
            logger.error(f"[Validator] Output folders are not writable: {e}")
            checks_passed = False

        if not checks_passed:
            logger.critical("[Validator] Pre-flight validation FAILED. Aborting.")
        else:
            logger.info("[Validator] Pre-flight validation PASSED.")
            
        return checks_passed
