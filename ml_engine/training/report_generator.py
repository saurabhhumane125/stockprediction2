"""
ml_engine/training/report_generator.py
─────────────────────────────────────────────────────────────────────────────
Generates human-readable Markdown and machine-readable JSON training reports.

Reports include:
  • Hyperparameters from TrainingConfig
  • Dataset statistics (shapes, tickers, split dates)
  • Training curve (loss / metric per epoch)
  • Evaluation metrics
  • Hardware / environment information
  • Git commit hash (if inside a git repo)
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import logging
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_git_commit() -> str:
    """Returns the short git commit hash or 'N/A' if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "N/A"
    except Exception:
        return "N/A"


def _package_version(pkg: str) -> str:
    try:
        import importlib.metadata
        return importlib.metadata.version(pkg)
    except Exception:
        return "N/A"


class ReportGenerator:
    """
    Generates training reports after a training run completes.

    Usage::

        gen = ReportGenerator(output_dir="ml_engine/models/v2.0.0")
        gen.generate(
            config=training_config.to_dict(),
            dataset_info={...},
            history=[{"epoch": 0, "train_loss": 0.6, ...}, ...],
            eval_metrics={"test_accuracy": 0.87},
            feature_names=[...],
        )
    """

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # ── Public ────────────────────────────────────────────────────────────────

    def generate(
        self,
        config: Dict[str, Any],
        dataset_info: Dict[str, Any],
        history: List[Dict[str, Any]],
        eval_metrics: Dict[str, Any],
        feature_names: List[str],
        version: str = "unknown",
        execution_time_seconds: float = 0.0,
    ) -> Dict[str, str]:
        """
        Produce both a ``training_report.json`` and ``training_report.md`` in
        ``output_dir``.

        Args:
            config:                   ``TrainingConfig.to_dict()`` snapshot.
            dataset_info:             Keys: ``tickers``, ``train_rows``,
                                      ``val_rows``, ``test_rows``,
                                      ``train_end``, ``val_end``.
            history:                  List of per-epoch metric dicts,
                                      e.g. ``[{"epoch": 0, "train_loss": 0.6, ...}]``.
            eval_metrics:             Out-of-sample evaluation metric dict.
            feature_names:            Ordered list of feature column names fed
                                      to the model.
            version:                  Model version string.
            execution_time_seconds:   Total wall-clock training time.

        Returns:
            Dict with keys ``json_path`` and ``markdown_path``.
        """
        environment = self._collect_environment()
        # Pop plot paths from eval metrics if present
        plot_paths = {}
        if "plot_paths" in eval_metrics:
            plot_paths = eval_metrics.pop("plot_paths")

        report = {
            "version": version,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
            "execution_time_seconds": round(execution_time_seconds, 2),
            "git_commit": environment["git_commit"],
            "environment": environment,
            "hyperparameters": config,
            "dataset": dataset_info,
            "feature_names": feature_names,
            "training_history": history,
            "evaluation_metrics": {
                k: round(float(v), 6) if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('.','',1).isdigit()) else v 
                for k, v in eval_metrics.items()
            },
            "plot_paths": plot_paths,
        }

        json_path = os.path.join(self.output_dir, "training_report.json")
        md_path = os.path.join(self.output_dir, "training_report.md")

        with open(json_path, "w") as f:
            json.dump(report, f, indent=4)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self._render_markdown(report))

        logger.info(f"[ReportGenerator] Reports written → {json_path} | {md_path}")
        return {"json_path": json_path, "markdown_path": md_path}

    # ── Private ───────────────────────────────────────────────────────────────

    def _collect_environment(self) -> Dict[str, str]:
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "git_commit": _get_git_commit(),
            "numpy": _package_version("numpy"),
            "scikit_learn": _package_version("scikit-learn"),
            "tensorflow": _package_version("tensorflow"),
            "torch": _package_version("torch"),
            "pandas": _package_version("pandas"),
        }

    def _render_markdown(self, report: Dict[str, Any]) -> str:
        lines: List[str] = []

        def h(level: int, text: str) -> None:
            lines.append(f"{'#' * level} {text}\n")

        def kv(key: str, value: Any) -> None:
            lines.append(f"- **{key}**: `{value}`")

        h(1, f"Training Report – {report['version']}")
        lines.append(f"> Generated at {report['generated_at']} | "
                     f"Git commit: `{report['git_commit']}` | "
                     f"Execution time: {report['execution_time_seconds']}s\n")

        h(2, "Environment")
        for k, v in report["environment"].items():
            kv(k, v)
        lines.append("")

        h(2, "Hyperparameters")
        for k, v in report["hyperparameters"].items():
            kv(k, v)
        lines.append("")

        h(2, "Dataset")
        for k, v in report["dataset"].items():
            kv(k, v)
        lines.append("")

        h(2, "Features")
        lines.append(f"Total features: **{len(report['feature_names'])}**\n")
        lines.append("```")
        lines.append(", ".join(report["feature_names"]))
        lines.append("```\n")

        h(2, "Evaluation Metrics (Out-of-Sample)")
        
        # Highlight the optimal F1 threshold if available
        if "optimal_val_f1_threshold" in report["evaluation_metrics"]:
            thresh = report["evaluation_metrics"]["optimal_val_f1_threshold"]
            lines.append(f"> [!TIP]\n> **Optimal F1 Threshold (Validation)**: `{thresh:.4f}`\n")

        for k, v in report["evaluation_metrics"].items():
            kv(k, v)
        lines.append("")
        
        # Embed plots if available
        if report.get("plot_paths"):
            h(2, "Evaluation Plots")
            for plot_key, plot_filename in report["plot_paths"].items():
                lines.append(f"### {plot_key.replace('_', ' ').title()}")
                lines.append(f"![{plot_key}](./{plot_filename})\n")
            lines.append("")

        h(2, "Training Curve (last 10 epochs)")
        history = report["training_history"]
        tail = history[-10:]
        if tail:
            cols = list(tail[0].keys())
            header = "| " + " | ".join(cols) + " |"
            sep = "| " + " | ".join(["---"] * len(cols)) + " |"
            lines.append(header)
            lines.append(sep)
            for row in tail:
                def _fmt(val):
                    if isinstance(val, (int, float)):
                        return str(round(val, 6))
                    return str(val)
                lines.append("| " + " | ".join(_fmt(row.get(c, 0)) for c in cols) + " |")
        lines.append("")

        return "\n".join(lines)
