"""
ml_engine/scripts/experiment_cli.py
─────────────────────────────────────────────────────────────────────────────
CLI for querying and comparing experiments and runs in the Tracker.
─────────────────────────────────────────────────────────────────────────────
"""
import argparse
import sys
import json

from ml_engine.experiments.manager import ExperimentManager
from ml_engine.experiments.report_builder import ExperimentReportBuilder


def main():
    parser = argparse.ArgumentParser(description="Experiment Tracking CLI")
    parser.add_argument("--db-path", type=str, default="ml_engine/experiments/tracking.db", help="Path to tracking DB")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # List Experiments
    list_parser = subparsers.add_parser("list", help="List all experiments")
    
    # Leaderboard
    leader_parser = subparsers.add_parser("leaderboard", help="Show leaderboard for an experiment")
    leader_parser.add_argument("experiment_name", type=str)
    leader_parser.add_argument("--metric", type=str, default="f1_score")
    leader_parser.add_argument("--asc", action="store_true", help="Sort ascending (default is descending)")
    
    # Compare
    compare_parser = subparsers.add_parser("compare", help="Compare multiple runs")
    compare_parser.add_argument("run_ids", type=str, nargs="+", help="Run UUIDs to compare")
    compare_parser.add_argument("--format", type=str, choices=["markdown", "json", "csv"], default="markdown")
    
    # Show
    show_parser = subparsers.add_parser("show", help="Show details of a specific run")
    show_parser.add_argument("run_id", type=str)
    
    args = parser.parse_args()
    
    manager = ExperimentManager(args.db_path)
    
    if args.command == "list":
        exps = manager.list_experiments()
        print(f"Found {len(exps)} experiments:\n")
        for e in exps:
            print(f"- {e.name} (ID: {e.experiment_id}) [Created: {e.created_at}]")
            
    elif args.command == "leaderboard":
        runs = manager.get_leaderboard(args.experiment_name, sort_metric=args.metric, descending=not args.asc)
        md = ExperimentReportBuilder.build_leaderboard_markdown(runs, args.metric)
        print(md)
        
    elif args.command == "compare":
        runs = manager.compare_runs(args.run_ids)
        if args.format == "markdown":
            print(ExperimentReportBuilder.build_comparison_markdown(runs))
        elif args.format == "json":
            print(ExperimentReportBuilder.export_json(runs))
        elif args.format == "csv":
            print(ExperimentReportBuilder.export_csv(runs))
            
    elif args.command == "show":
        run = manager.get_run(args.run_id)
        if not run:
            print(f"Run {args.run_id} not found.")
            sys.exit(1)
        print(json.dumps({
            "run_id": run.run_id,
            "experiment": run.experiment_id,
            "name": run.run_name,
            "status": run.status,
            "metrics": run.metrics,
            "parameters": run.parameters,
            "metadata": run.metadata
        }, indent=4))

if __name__ == "__main__":
    main()
