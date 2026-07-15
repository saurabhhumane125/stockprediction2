"""
ml_engine/data/reports/data_quality.py
─────────────────────────────────────────────────────────────────────────────
Generates data quality reports for an expanded dataset.
─────────────────────────────────────────────────────────────────────────────
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

import pandas as pd
from ml_engine.data.storage.parquet_partitioner import PartitionedParquetStorage

logger = logging.getLogger(__name__)


class DataQualityReportBuilder:
    """
    Analyzes an expanded dataset and builds quality reports.
    """
    def __init__(self, storage: PartitionedParquetStorage, output_dir: str):
        self.storage = storage
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def build_report(
        self,
        universe: str,
        dataset_version: str,
        expected_tickers: List[str]
    ) -> Dict[str, str]:
        """
        Analyze the dataset and generate JSON and Markdown reports.
        """
        logger.info(f"[DataQuality] Analyzing {universe} {dataset_version}")
        
        stats = {
            "universe": universe,
            "version": dataset_version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "expected_count": len(expected_tickers),
            "actual_count": 0,
            "missing_tickers": [],
            "ticker_stats": {}
        }
        
        for t in expected_tickers:
            df = self.storage.read_partition(universe, dataset_version, t)
            if df.empty:
                stats["missing_tickers"].append(t)
                continue
                
            stats["actual_count"] += 1
            
            # Basic stats
            n_rows = len(df)
            date_min = df.index.min().strftime("%Y-%m-%d")
            date_max = df.index.max().strftime("%Y-%m-%d")
            
            # Missing trading days approximation (weekdays)
            expected_days = len(pd.bdate_range(start=date_min, end=date_max))
            actual_days = n_rows
            missing_pct = max(0.0, (expected_days - actual_days) / expected_days * 100)
            
            # Corporate Actions
            divs = (df["dividends"] > 0).sum() if "dividends" in df.columns else 0
            splits = (df["stock_splits"] > 0).sum() if "stock_splits" in df.columns else 0
            
            stats["ticker_stats"][t] = {
                "rows": int(n_rows),
                "start_date": date_min,
                "end_date": date_max,
                "missing_days_pct": float(missing_pct),
                "dividends_events": int(divs),
                "split_events": int(splits)
            }
            
        json_path = self._write_json(stats, universe, dataset_version)
        md_path = self._write_markdown(stats, universe, dataset_version)
        
        return {"json": json_path, "markdown": md_path}

    def _write_json(self, stats: Dict[str, Any], universe: str, version: str) -> str:
        path = os.path.join(self.output_dir, f"{universe}_{version}_quality.json")
        with open(path, "w") as f:
            json.dump(stats, f, indent=4)
        return path

    def _write_markdown(self, stats: Dict[str, Any], universe: str, version: str) -> str:
        path = os.path.join(self.output_dir, f"{universe}_{version}_quality.md")
        lines = [
            f"# Data Quality Report: {universe} ({version})",
            f"> Generated: {stats['generated_at']}",
            "",
            "## Summary",
            f"- **Expected Tickers:** {stats['expected_count']}",
            f"- **Successfully Collected:** {stats['actual_count']}",
            f"- **Missing:** {len(stats['missing_tickers'])}",
            ""
        ]
        
        if stats['missing_tickers']:
            lines.append("## Missing Tickers")
            lines.append(", ".join(stats['missing_tickers']))
            lines.append("")
            
        lines.append("## Ticker Statistics (Sample of 10)")
        lines.append("| Ticker | Rows | Date Range | Missing Days | Corporate Actions |")
        lines.append("|---|---|---|---|---|")
        
        sample = list(stats['ticker_stats'].items())[:10]
        for t, s in sample:
            drange = f"{s['start_date']} to {s['end_date']}"
            ca = f"{s['dividends_events']} Div, {s['split_events']} Spl"
            md = f"{s['missing_days_pct']:.1f}%"
            lines.append(f"| {t} | {s['rows']} | {drange} | {md} | {ca} |")
            
        if len(stats['ticker_stats']) > 10:
            lines.append(f"| ... | ... | ... | ... | ... |")
            
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path
