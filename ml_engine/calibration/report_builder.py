"""
ml_engine/calibration/report_builder.py
─────────────────────────────────────────────────────────────────────────────
Generates JSON, Markdown, and CSV reports for calibration metrics.
─────────────────────────────────────────────────────────────────────────────
"""
import csv
import json
import logging
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List

from ml_engine.calibration.results import CalibrationResult

logger = logging.getLogger(__name__)


def _git_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "N/A"
    except Exception:
        return "N/A"


class CalibrationReportBuilder:
    """
    Builds multi-format calibration reports.
    """
    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def build(self, result: CalibrationResult) -> Dict[str, str]:
        env = self._collect_env()
        paths = {}
        paths["json"] = self._write_json(result, env)
        paths["markdown"] = self._write_markdown(result, env)
        paths["csv"] = self._write_csv(result)
        logger.info(f"[CalibrationReportBuilder] Reports written → {self.output_dir}")
        return paths

    def _collect_env(self) -> Dict[str, str]:
        return {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "git_commit": _git_hash(),
        }

    def _write_json(self, result: CalibrationResult, env: Dict[str, str]) -> str:
        data = result.to_dict()
        data["environment"] = env
        data["generated_at"] = datetime.now(timezone.utc).isoformat()
        
        path = os.path.join(self.output_dir, "calibration_report.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return path

    def _write_markdown(self, result: CalibrationResult, env: Dict[str, str]) -> str:
        lines: List[str] = []
        lines.append(f"# Calibration Report ({result.method.title()})\n")
        lines.append(
            f"> Generated: {datetime.now(timezone.utc).isoformat()} | "
            f"Git: `{env.get('git_commit', 'N/A')}` | "
            f"Runtime: {result.execution_time_seconds:.2f}s\n"
        )

        lines.append("## Metrics Comparison\n")
        lines.append("| Metric | Before | After | Improvement |")
        lines.append("|---|---|---|---|")
        
        metrics = ["ece", "mce", "brier_score", "log_loss"]
        for m in metrics:
            before = getattr(result.before_metrics, m)
            after = getattr(result.after_metrics, m)
            # Lower is better for all these metrics
            improv = before - after
            icon = "✅" if improv > 0 else "❌"
            if abs(improv) < 1e-6:
                icon = "➖"
            lines.append(f"| **{m.upper().replace('_', ' ')}** | {before:.4f} | {after:.4f} | {improv:+.4f} {icon} |")
        lines.append("\n")

        if result.artifact_paths:
            lines.append("## Visual Artifacts\n")
            for name, path in result.artifact_paths.items():
                if path.endswith(".png"):
                    rel = os.path.relpath(path, self.output_dir)
                    lines.append(f"![{name}](./{rel})")
            lines.append("\n")

        path = os.path.join(self.output_dir, "calibration_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path

    def _write_csv(self, result: CalibrationResult) -> str:
        path = os.path.join(self.output_dir, "calibration_metrics.csv")
        
        fieldnames = ["metric", "before", "after", "improvement"]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for m in ["ece", "mce", "brier_score", "log_loss"]:
                before = getattr(result.before_metrics, m)
                after = getattr(result.after_metrics, m)
                writer.writerow({
                    "metric": m,
                    "before": before,
                    "after": after,
                    "improvement": before - after
                })
        return path
