import glob
import json
for path in glob.glob('artifacts/candidates/NIFTY50/*/training_report.json'):
    with open(path, 'r') as f:
        data = json.load(f)
        eval = data.get('evaluation_metrics', {})
        history = data.get('training_history', [])
        epochs = len(history)
        print(f'{path} : epochs={epochs}, test_r2={eval.get("test_r2")}, test_loss={eval.get("test_loss")}')
