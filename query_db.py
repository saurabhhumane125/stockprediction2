import sqlite3
import pandas as pd
import json

conn = sqlite3.connect('ml_engine/experiments/tracking.db')
df_runs = pd.read_sql("SELECT * FROM runs ORDER BY end_time DESC LIMIT 2", conn)
for i, run in df_runs.iterrows():
    print(f"Run ID: {run['run_id']}")
    print(f"Status: {run['status']}")
    metrics = pd.read_sql(f"SELECT * FROM run_metrics WHERE run_id='{run['run_id']}'", conn)
    print("METRICS:")
    print(metrics.to_string())
    params = pd.read_sql(f"SELECT * FROM run_parameters WHERE run_id='{run['run_id']}'", conn)
    print("PARAMS:")
    print(params.to_string())
    meta = pd.read_sql(f"SELECT * FROM run_metadata WHERE run_id='{run['run_id']}'", conn)
    print("META:")
    print(meta.to_string())
    print("-" * 50)
