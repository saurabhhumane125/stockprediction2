import json
import os
import logging
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)


class ValidationReport:
    """
    Structured validation report generator.
    Produces both JSON and human-readable Markdown reports.
    """
    def __init__(self, dataset_version: str, pipeline_version: str):
        self.dataset_version = dataset_version
        self.pipeline_version = pipeline_version
        self.status = "PENDING"
        
        # Reproducibility Hashes
        self.dataset_hash = ""
        self.feature_config_hash = ""
        self.training_config_hash = ""
        self.ticker_list_hash = ""
        
        self.logs: List[Dict[str, str]] = []
        
        self.stats: Dict[str, Any] = {
            "rows_processed": 0,
            "rows_rejected": 0,
            "missing_values": 0,
            "duplicate_rows": 0,
            "ohlc_violations": 0,
            "feature_statistics": {}
        }

    def add_log(self, severity: str, message: str):
        """Adds a log with severity: INFO, WARNING, ERROR, CRITICAL"""
        if severity not in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
            severity = "INFO"
        self.logs.append({"severity": severity, "message": message})
        
        # Escalate status if necessary
        if severity == "CRITICAL":
            self.status = "FAILED"
        elif severity == "ERROR" and self.status != "FAILED":
            self.status = "FAILED"
        elif severity == "WARNING" and self.status not in ["FAILED", "ERROR"]:
            self.status = "WARNING"

    def finalize(self, passed: bool):
        if not passed:
            self.status = "FAILED"
        elif self.status == "PENDING":
            self.status = "PASSED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_version": self.dataset_version,
            "pipeline_version": self.pipeline_version,
            "status": self.status,
            "hashes": {
                "dataset_hash": self.dataset_hash,
                "feature_config_hash": self.feature_config_hash,
                "training_config_hash": self.training_config_hash,
                "ticker_list_hash": self.ticker_list_hash
            },
            "stats": self.stats,
            "logs": self.logs
        }

    def save_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def save_markdown(self, path: str):
        md = f"# Validation Report: {self.status}\n\n"
        md += f"**Dataset Version**: {self.dataset_version}\n"
        md += f"**Pipeline Version**: {self.pipeline_version}\n\n"
        
        md += "## Hashes (Reproducibility)\n"
        md += f"- **Dataset**: {self.dataset_hash}\n"
        md += f"- **Feature Config**: {self.feature_config_hash}\n"
        md += f"- **Training Config**: {self.training_config_hash}\n"
        md += f"- **Ticker List**: {self.ticker_list_hash}\n\n"
        
        md += "## Statistics\n"
        for k, v in self.stats.items():
            md += f"- **{k}**: {v}\n"
            
        md += "\n## Logs\n"
        if not self.logs:
            md += "- None\n"
        for log in self.logs:
            md += f"- **[{log['severity']}]** {log['message']}\n"
            
        with open(path, "w") as f:
            f.write(md)
