"""
ml_engine/evaluation/comparator.py
─────────────────────────────────────────────────────────────────────────────
Model Comparator — ranks multiple ``EvaluationResult`` objects by a
configurable primary metric and generates a comparison table.

Future-compatible: simply append more ``EvaluationResult`` objects to
compare GRU / BiGRU / LSTM / Transformer / sector-grouped models.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import csv
import io
import json
import logging
import math
import os
from typing import Dict, List, Optional

from ml_engine.config.evaluation_config import evaluation_config
from ml_engine.evaluation.results import EvaluationResult

logger = logging.getLogger(__name__)



class ComparisonRow:
    """Immutable summary row for a single model in the comparison table."""

    def __init__(self, model_name: str, version: str, metrics: dict, verdict: str) -> None:
        self.model_name = model_name
        self.version = version
        self.metrics = metrics
        self.verdict = verdict

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "version": self.version,
            "verdict": self.verdict,
            **self.metrics,
        }


class ModelComparator:
    """
    Collects evaluation results for multiple models and ranks them.

    Args:
        primary_metric: Metric key used for ranking
                        (defaults to ``EvaluationConfig.COMPARATOR_PRIMARY_METRIC``).
        metrics_to_show: Ordered list of metric keys in the table
                         (defaults to ``EvaluationConfig.COMPARATOR_METRICS``).
    """

    def __init__(
        self,
        primary_metric: Optional[str] = None,
        metrics_to_show: Optional[List[str]] = None,
    ) -> None:
        self.primary_metric = primary_metric or evaluation_config.COMPARATOR_PRIMARY_METRIC
        self.metrics_to_show = metrics_to_show or list(evaluation_config.COMPARATOR_METRICS)
        self._results: List[EvaluationResult] = []

    # ── API ────────────────────────────────────────────────────────────────

    def add(self, result: EvaluationResult) -> None:
        """
        Add an ``EvaluationResult`` to the comparison set.

        Args:
            result: Completed evaluation result for one model.
        """
        self._results.append(result)
        logger.debug(f"[Comparator] Added model '{result.model_name}' v{result.model_version}.")

    def rank(self) -> List[ComparisonRow]:
        """
        Return models ranked by the primary metric (descending — higher is better).

        Models with NaN primary metric are ranked last.

        Returns:
            List of ``ComparisonRow`` sorted best → worst.
        """
        rows = [self._to_row(r) for r in self._results]

        def sort_key(row: ComparisonRow) -> float:
            val = row.metrics.get(self.primary_metric, float("nan"))
            if not isinstance(val, (int, float)):
                return float("-inf")
            return float("-inf") if math.isnan(val) else -val  # negate for desc sort

        rows.sort(key=sort_key)
        # Reverse the negation so the list reads best → worst
        return rows

    def to_json(self) -> str:
        """Serialise the ranked comparison table as a JSON string."""
        ranked = self.rank()
        return json.dumps([r.to_dict() for r in ranked], indent=4)

    def to_markdown(self) -> str:
        """Render the ranked comparison table as a Markdown string."""
        ranked = self.rank()
        if not ranked:
            return "_No models to compare._\n"

        cols = ["rank", "model_name", "version", "verdict"] + self.metrics_to_show
        header = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        lines = [header, sep]

        for idx, row in enumerate(ranked, start=1):
            values = [str(idx), row.model_name, row.version, row.verdict]
            for m in self.metrics_to_show:
                val = row.metrics.get(m, float("nan"))
                if not isinstance(val, (int, float)):
                    values.append(str(val))
                else:
                    values.append("nan" if math.isnan(val) else f"{val:.4f}")
            lines.append("| " + " | ".join(values) + " |")

        return "\n".join(lines) + "\n"

    def to_csv(self) -> str:
        """Render the ranked comparison table as a CSV string."""
        ranked = self.rank()
        out = io.StringIO()
        cols = ["rank", "model_name", "version", "verdict"] + self.metrics_to_show
        writer = csv.DictWriter(out, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for idx, row in enumerate(ranked, start=1):
            row_dict = {"rank": idx, **row.to_dict()}
            writer.writerow(row_dict)
        return out.getvalue()

    def save(self, output_dir: str) -> Dict[str, str]:
        """
        Save JSON, Markdown, and CSV comparison reports to *output_dir*.

        Args:
            output_dir: Directory where files will be written.

        Returns:
            Dict of ``{"json": path, "markdown": path, "csv": path}``.
        """
        os.makedirs(output_dir, exist_ok=True)
        paths: Dict[str, str] = {}

        json_path = os.path.join(output_dir, "model_comparison.json")
        with open(json_path, "w") as f:
            f.write(self.to_json())
        paths["json"] = json_path

        md_path = os.path.join(output_dir, "model_comparison.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Model Comparison\n\n**Primary metric:** {self.primary_metric}\n\n")
            f.write(self.to_markdown())
        paths["markdown"] = md_path

        csv_path = os.path.join(output_dir, "model_comparison.csv")
        with open(csv_path, "w", newline="") as f:
            f.write(self.to_csv())
        paths["csv"] = csv_path

        logger.info(f"[Comparator] Reports saved → {output_dir}")
        return paths

    # ── Internal ───────────────────────────────────────────────────────────

    def _to_row(self, result: EvaluationResult) -> ComparisonRow:
        m = result.metrics
        all_metrics = {k: v for k, v in m.to_dict().items() if k in self.metrics_to_show}
        return ComparisonRow(
            model_name=result.model_name,
            version=result.model_version,
            metrics=all_metrics,
            verdict=result.decision.verdict,
        )
