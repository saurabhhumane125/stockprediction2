"""
ml_engine/colab/gpu_manager.py
─────────────────────────────────────────────────────────────────────────────
Manages GPU configuration and verification.
─────────────────────────────────────────────────────────────────────────────
"""
import logging

logger = logging.getLogger(__name__)


class GPUManager:
    """Verifies and logs GPU availability."""

    @staticmethod
    def verify_gpu() -> bool:
        """Returns True if a valid GPU is found."""
        try:
            import torch
            if not torch.cuda.is_available():
                logger.warning("[GPUManager] CUDA is not available!")
                return False
                
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"[GPUManager] GPU Detected: {gpu_name}")
            
            # Print memory stats
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            reserved = torch.cuda.memory_reserved(0) / (1024**3)
            logger.info(f"[GPUManager] Allocated: {allocated:.2f} GB | Reserved: {reserved:.2f} GB")
            return True
        except ImportError:
            logger.warning("[GPUManager] PyTorch is not installed. Cannot verify GPU.")
            return False
