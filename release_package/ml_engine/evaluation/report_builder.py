"""
ml_engine/evaluation/report_builder.py
─────────────────────────────────────────────────────────────────────────────
Generates JSON, Markdown, and CSV evaluation reports from an ``EvaluationResult``.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import csv
import io
import json
import logging
import math
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

from ml_engine.evaluation.results import EvaluationResult

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


def _pkg(name: str) -> str:
    try:
        import importlib.metadata
        return importlib.metadata.version(name)
    except Exception:
        return "N/A"


class EvaluationReportBuilder:
    """
    Builds multi-format evaluation reports from a completed ``EvaluationResult``.

    Args:
        output_dir: Directory where report files will be written.
    """

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def build(self, result: EvaluationResult) -> Dict[str, str]:
        """
        Generate JSON, Markdown, and CSV reports.

        Args:
            result: Completed ``EvaluationResult``.

        Returns:
            Dict with keys ``"json"``, ``"markdown"``, ``"csv"`` mapping to
            absolute file paths.
        """
        env = self._collect_env()
        paths: Dict[str, str] = {}

        paths["json"] = self._write_json(result, env)
        paths["markdown"] = self._write_markdown(result, env)
        paths["csv"] = self._write_csv(result)

        logger.info(f"[ReportBuilder] Reports written → {self.output_dir}")
        return paths

    # ── Private ───────────────────────────────────────────────────────────

    def _collect_env(self) -> Dict[str, str]:
        return {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "git_commit": _git_hash(),
            "numpy": _pkg("numpy"),
            "scikit_learn": _pkg("scikit-learn"),
            "torch": _pkg("torch"),
            "matplotlib": _pkg("matplotlib"),
        }

    def _write_json(self, result: EvaluationResult, env: Dict[str, str]) -> str:
        data = result.to_dict()
        data["environment"] = env
        path = os.path.join(self.output_dir, "evaluation_report.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4, default=str)
        return path

    def _write_markdown(self, result: EvaluationResult, env: Dict[str, str]) -> str:
        lines: List[str] = []

        def h(level: int, text: str) -> None:
            lines.append(f"{'#' * level} {text}\n")

        def kv(key: str, val: Any) -> None:
            lines.append(f"- **{key}**: `{val}`")

        h(1, f"Evaluation Report – {result.model_name} v{result.model_version}")
        lines.append(
            f"> {result.evaluation_timestamp} | "
            f"git: `{env.get('git_commit', 'N/A')}` | "
            f"runtime: {result.execution_time_seconds:.2f}s\n"
        )

        h(2, f"Verdict: {result.decision.verdict}")
        if result.decision.passed:
            lines.append("✅ This model **PASSES** all production acceptance thresholds.\n")
        else:
            lines.append("❌ This model **FAILS** production acceptance.\n")
            lines.append("**Failed checks:**")
            for reason in result.decision.reasons:
                lines.append(f"- {reason}")
            lines.append("")

        h(2, "Metrics")
        for k, v in result.metrics.to_dict().items():
            val_str = "nan" if isinstance(v, float) and math.isnan(v) else f"{v:.4f}"
            kv(k.replace("_", " ").title(), val_str)
        lines.append("")

        h(2, "Confusion Matrix")
        cm = result.confusion_matrix
        lines.append(
            f"| | Pred 0 | Pred 1 |\n"
            f"|---|---|---|\n"
            f"| True 0 | {cm.tn} | {cm.fp} |\n"
            f"| True 1 | {cm.fn} | {cm.tp} |\n"
        )

        h(2, "Calibration")
        kv("ECE", f"{result.calibration.ece:.6f}")
        kv("MCE", f"{result.calibration.mce:.6f}")
        lines.append("")

        if result.walk_forward:
            h(2, "Walk-Forward Validation")
            kv("Folds", result.walk_forward.n_folds)
            h(3, "Mean Metrics")
            for k, v in result.walk_forward.mean_metrics.items():
                val_str = "nan" if math.isnan(v) else f"{v:.4f} ± {result.walk_forward.std_metrics.get(k, 0):.4f}"
                kv(k, val_str)
            lines.append("")

        h(2, "Environment")
        for k, v in env.items():
            kv(k, v)
        lines.append("")

        h(2, "Visual Artifacts")
        for name, path in result.artifact_paths.items():
            if path.endswith(".png"):
                rel = os.path.relpath(path, self.output_dir)
                lines.append(f"![{name}](./{rel})")
        lines.append("")

        path = os.path.join(self.output_dir, "evaluation_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path

    def _write_csv(self, result: EvaluationResult) -> str:
        path = os.path.join(self.output_dir, "evaluation_summary.csv")
        rows = [
            {"field": "model_name", "value": result.model_name},
            {"field": "model_version", "value": result.model_version},
            {"field": "verdict", "value": result.decision.verdict},
            {"field": "n_test_samples", "value": result.n_test_samples},
            {"field": "execution_time_s", "value": result.execution_time_seconds},
        ]
        for k, v in result.metrics.to_dict().items():
            rows.append({"field": k, "value": v})
        rows.append({"field": "ece", "value": result.calibration.ece})
        rows.append({"field": "mce", "value": result.calibration.mce})

        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["field", "value"])
            writer.writeheader()
            writer.writerows(rows)
        return path
