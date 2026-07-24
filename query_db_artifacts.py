import sqlite3
import pandas as pd
conn = sqlite3.connect('ml_engine/experiments/tracking.db')
artifacts = pd.read_sql("SELECT * FROM run_artifacts WHERE run_id='36373d2e-def9-4074-a20a-25f622312528'", conn)
print(artifacts.to_string())
