"""
ml_engine/optimization/report_builder.py
─────────────────────────────────────────────────────────────────────────────
Generates JSON, Markdown, and CSV evaluation reports for optimization studies.
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
from typing import Any, Dict, List

from ml_engine.optimization.results import OptimizationResult

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


class OptimizationReportBuilder:
    """
    Builds multi-format optimization reports from a completed ``OptimizationResult``.

    Args:
        output_dir: Directory where report files will be written.
    """

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def build(self, result: OptimizationResult) -> Dict[str, str]:
        """
        Generate JSON, Markdown, and CSV reports.

        Args:
            result: Completed ``OptimizationResult``.

        Returns:
            Dict with keys ``"json"``, ``"markdown"``, ``"csv"`` mapping to
            absolute file paths.
        """
        env = self._collect_env()
        paths: Dict[str, str] = {}

        paths["json"] = self._write_json(result, env)
        paths["markdown"] = self._write_markdown(result, env)
        paths["csv"] = self._write_csv(result)

        logger.info(f"[OptimizationReportBuilder] Reports written → {self.output_dir}")
        return paths

    def _collect_env(self) -> Dict[str, str]:
        return {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "git_commit": _git_hash(),
            "optuna": _pkg("optuna"),
            "torch": _pkg("torch"),
        }

    def _write_json(self, result: OptimizationResult, env: Dict[str, str]) -> str:
        data = result.to_dict()
        data["environment"] = env
        data["generated_at"] = datetime.now(timezone.utc).isoformat()
        
        path = os.path.join(self.output_dir, "optimization_report.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4, default=str)
        return path

    def _write_markdown(self, result: OptimizationResult, env: Dict[str, str]) -> str:
        lines: List[str] = []

        lines.append(f"# Optimization Report – {result.study_name}\n")
        lines.append(
            f"> Generated: {datetime.now(timezone.utc).isoformat()} | "
            f"Git: `{env.get('git_commit', 'N/A')}` | "
            f"Runtime: {result.optimization_time_seconds:.2f}s\n"
        )

        lines.append("## Summary")
        lines.append(f"- **Total Trials:** {result.n_trials}")
        lines.append(f"- **Best Trial Number:** {result.best_trial_number}")
        val_str = f"{result.best_value:.4f}" if result.best_value is not None else "N/A"
        lines.append(f"- **Best Objective Value:** {val_str}\n")

        lines.append("## Best Hyperparameters")
        for k, v in result.best_params.items():
            lines.append(f"- **{k}**: `{v}`")
        lines.append("\n")

        if result.parameter_importance:
            lines.append("## Parameter Importance")
            for imp in result.parameter_importance:
                lines.append(f"- **{imp.name}**: {imp.importance:.4f}")
            lines.append("\n")

        if result.top_n_trials:
            lines.append("## Top Trials")
            lines.append("| Rank | Trial | State | Value | Duration (s) |")
            lines.append("|---|---|---|---|---|")
            for idx, t in enumerate(result.top_n_trials, 1):
                tval = f"{t.value:.4f}" if t.value is not None else "N/A"
                lines.append(f"| {idx} | {t.number} | {t.state} | {tval} | {t.duration_seconds:.2f} |")
            lines.append("\n")
            
        if result.failed_trials:
            lines.append("## Failed Trials")
            lines.append(f"- **Count:** {len(result.failed_trials)}")
            failed_nums = ", ".join(str(t.number) for t in result.failed_trials[:10])
            if len(result.failed_trials) > 10:
                failed_nums += ", ..."
            lines.append(f"- **Trial IDs:** {failed_nums}\n")

        lines.append("## Environment")
        for k, v in env.items():
            lines.append(f"- **{k}**: `{v}`")
        lines.append("\n")

        if result.artifact_paths:
            lines.append("## Visual Artifacts")
            for name, path in result.artifact_paths.items():
                if path.endswith(".png"):
                    rel = os.path.relpath(path, self.output_dir)
                    lines.append(f"![{name}](./{rel})")
            lines.append("\n")

        path = os.path.join(self.output_dir, "optimization_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path

    def _write_csv(self, result: OptimizationResult) -> str:
        path = os.path.join(self.output_dir, "optimization_trials.csv")
        
        all_trials = result.top_n_trials + result.failed_trials
        all_trials.sort(key=lambda t: t.number)
        
        if not all_trials:
            with open(path, "w") as f:
                f.write("No trials recorded.\n")
            return path
            
        # Collect all parameter keys across all trials
        param_keys = set()
        for t in all_trials:
            param_keys.update(t.params.keys())
        param_keys = sorted(list(param_keys))

        fieldnames = ["trial_number", "state", "value", "duration_seconds", "datetime_start"] + param_keys
        
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in all_trials:
                row = {
                    "trial_number": t.number,
                    "state": t.state,
                    "value": t.value,
                    "duration_seconds": t.duration_seconds,
                    "datetime_start": t.datetime_start,
                }
                row.update(t.params)
                writer.writerow(row)
                
        return path
