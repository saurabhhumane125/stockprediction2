"""
ml_engine/colab/environment.py
─────────────────────────────────────────────────────────────────────────────
Detects the Colab environment runtime capabilities.
─────────────────────────────────────────────────────────────────────────────
"""
import sys
import platform
import os
import psutil
import shutil
import logging

logger = logging.getLogger(__name__)


class EnvironmentDetector:
    """Detects Colab specific environment details."""

    @staticmethod
    def is_colab() -> bool:
        """Returns True if running in a Google Colab environment."""
        return "COLAB_GPU" in os.environ or "google.colab" in sys.modules

    @staticmethod
    def get_report() -> dict:
        """Generates an environment report including Python, RAM, Disk, etc."""
        report = {
            "is_colab": EnvironmentDetector.is_colab(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        }

        # RAM
        vm = psutil.virtual_memory()
        report["ram_total_gb"] = round(vm.total / (1024**3), 2)
        report["ram_available_gb"] = round(vm.available / (1024**3), 2)

        # Disk
        disk = shutil.disk_usage("/")
        report["disk_total_gb"] = round(disk.total / (1024**3), 2)
        report["disk_free_gb"] = round(disk.free / (1024**3), 2)

        # PyTorch & CUDA
        try:
            import torch
            report["torch_version"] = torch.__version__
            report["cuda_available"] = torch.cuda.is_available()
            if report["cuda_available"]:
                report["cuda_version"] = torch.version.cuda
        except ImportError:
            report["torch_version"] = None
            report["cuda_available"] = False

        return report

    @staticmethod
    def log_environment():
        """Logs the environment report."""
        report = EnvironmentDetector.get_report()
        logger.info("=== Environment Report ===")
        for k, v in report.items():
            logger.info(f"{k}: {v}")
