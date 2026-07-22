# Production Colab Orchestrator

This notebook contains **zero business logic**. It exists strictly to bootstrap the execution environment and launch the Training Runner CLI.

## Step 1: Mount Google Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```

## Step 2: Extract Production Package
```bash
!unzip -q -o /content/drive/MyDrive/STOCK-PREDICTION/stockprediction_v2.zip -d /content/
```

## Step 3: Validate Environment & Verify Dependencies
```bash
# Safely verify and install only missing dependencies
!python -m ml_engine.scripts.prepare_colab --check-deps

# Validate hardware, dataset, configuration, and manifests
!python -m ml_engine.scripts.prepare_colab --validate CORE/v1.0
```

## Step 4: Execute Production Training
```bash
# This triggers the core ML engine pipeline. 
# It handles tensor loading, hyperparameter reading, loop execution, and model registry syncing.
!python -m ml_engine.scripts.train_models --dataset CORE/v1.0 --experiment production_colab_run
```

## Step 5: Export Artifacts to Drive
```bash
# Automatically syncs trained candidates, execution logs, metrics, and metadata back to Google Drive
!python -m ml_engine.scripts.prepare_colab --sync-exports
```
