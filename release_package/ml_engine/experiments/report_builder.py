"""
ml_engine/experiments/report_builder.py
─────────────────────────────────────────────────────────────────────────────
Generates Markdown, JSON, and CSV reports for experiment runs.
─────────────────────────────────────────────────────────────────────────────
"""
import json
import csv
import io
from typing import List, Dict, Any

from ml_engine.experiments.schemas import RunRecord


class ExperimentReportBuilder:
    
    @staticmethod
    def build_comparison_markdown(runs: List[RunRecord]) -> str:
        if not runs:
            return "No runs provided for comparison."
            
        md = ["# Run Comparison", ""]
        
        # Determine common keys
        all_metrics = set()
        all_params = set()
        for r in runs:
            all_metrics.update(r.metrics.keys())
            all_params.update(r.parameters.keys())
            
        all_metrics = sorted(list(all_metrics))
        all_params = sorted(list(all_params))
        
        # Basic Info Table
        md.append("## Basic Info")
        header = "| Run Name | Status | Duration |"
        separator = "|---" * 3 + "|"
        md.extend([header, separator])
        for r in runs:
            md.append(f"| {r.run_name} | {r.status} | {r.end_time or 'N/A'} |")
            
        md.append("")
        
        # Metrics Table
        md.append("## Metrics")
        header_cols = ["Metric"] + [r.run_name for r in runs]
        md.append("| " + " | ".join(header_cols) + " |")
        md.append("|---" * len(header_cols) + "|")
        for m in all_metrics:
            row = [m] + [str(r.metrics.get(m, "N/A")) for r in runs]
            md.append("| " + " | ".join(row) + " |")
            
        md.append("")
        
        # Parameters Table
        md.append("## Parameters")
        header_cols = ["Parameter"] + [r.run_name for r in runs]
        md.append("| " + " | ".join(header_cols) + " |")
        md.append("|---" * len(header_cols) + "|")
        for p in all_params:
            row = [p] + [str(r.parameters.get(p, "N/A")) for r in runs]
            md.append("| " + " | ".join(row) + " |")
            
        return "\n".join(md)

    @staticmethod
    def build_leaderboard_markdown(runs: List[RunRecord], metric: str) -> str:
        if not runs:
            return "No runs found."
            
        md = [f"# Leaderboard (Sorted by {metric})", ""]
        header = "| Rank | Run Name | Status | " + metric + " |"
        separator = "|---" * 4 + "|"
        md.extend([header, separator])
        
        for i, r in enumerate(runs, start=1):
            val = r.metrics.get(metric, "N/A")
            md.append(f"| {i} | {r.run_name} | {r.status} | {val} |")
            
        return "\n".join(md)

    @staticmethod
    def export_json(runs: List[RunRecord]) -> str:
        out = []
        for r in runs:
            # Need to convert dataclass to dict cleanly
            out.append({
                "run_id": r.run_id,
                "experiment_id": r.experiment_id,
                "run_name": r.run_name,
                "status": r.status,
                "metrics": r.metrics,
                "parameters": r.parameters,
                "artifacts": r.artifacts,
                "metadata": r.metadata
            })
        return json.dumps(out, indent=4)
        
    @staticmethod
    def export_csv(runs: List[RunRecord]) -> str:
        if not runs:
            return ""
            
        output = io.StringIO()
        
        all_metrics = set()
        all_params = set()
        for r in runs:
            all_metrics.update(r.metrics.keys())
            all_params.update(r.parameters.keys())
            
        fieldnames = ["run_id", "run_name", "status"] + \
                     [f"metric_{m}" for m in all_metrics] + \
                     [f"param_{p}" for p in all_params]
                     
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in runs:
            row = {
                "run_id": r.run_id,
                "run_name": r.run_name,
                "status": r.status
            }
            for m in all_metrics:
                row[f"metric_{m}"] = r.metrics.get(m, "")
            for p in all_params:
                row[f"param_{p}"] = r.parameters.get(p, "")
            writer.writerow(row)
            
        return output.getvalue()
