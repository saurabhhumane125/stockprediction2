# CORE/v2.0 Dataset Implementation Report

## 1. Files Modified
To safely generate the new dataset dynamically while avoiding hardcoded outdated symbol lists and disconnected paths, the following files were updated:
- **`ml_engine/data/universe/manager.py`**: Added dynamic web-fetch fallback for `NIFTY50`. It automatically downloads the latest official active constituent CSV list directly from the NSE India archive.
- **`ml_engine/data/tensors/builder.py`**: Fixed a legacy hardcoded path where `TensorBuilder` mistakenly pulled from `production/` instead of syncing dynamically with the output directory `datasets/` used by the dataset generator.

## 2. Pipeline Reused
The generation utilized the exact same battle-tested production pipeline established in Phase 1:
- `UniverseManager`: Resolved 50 active NIFTY 50 tickers.
- `ParallelDownloadEngine`: 10 background workers fetched OHLCV via `yfinance`.
- `ProductionCleaner`: Cleansed 100k+ rows and automatically purged statistical outliers.
- `FeatureGenerator`: Generated the required 23 technical indicator features.
- `ProductionDataValidator`: Validated schemas and bounds safely.
- `TensorBuilder`: Executed rigorous sequence chunking & windowing.

## 3. Dataset Statistics (NIFTY50/v2.0)
- **Number of Stocks**: 50
- **Rows**: 100,381 total cleaned OHLCV days.
- **Date Range**: `2018-01-01` to `2026-06-22`
- **Missing Values Imputed**: 0 (Handled organically by cleaner).
- **Feature Count**: 23 engineered features.
- **Sequence Count (Seq=48)**:
  - **Train**: 43,310 samples
  - **Validation**: 18,130 samples
  - **Test**: 36,541 samples
- **Class Balance (Train)**: 
  - `0` (Negative Return): 21,193 (~48.9%)
  - `1` (Positive Return): 22,117 (~51.1%)

## 4. Storage Size
- **Total Tensors**: 3 (`train.pt`, `val.pt`, `test.pt`)
- **Storage Profile**:
  - `train.pt`: 191.4 MB
  - `val.pt`: 80.1 MB
  - `test.pt`: 161.5 MB
  - **Total Tensor Footprint**: ~433 MB

## 5. Generation Time
- **Download & Feature Generation**: 45.3 seconds (Parallelized processing).
- **Tensor Generation**: ~59.3 seconds.
- **Total End-to-End Pipeline**: ~1.7 minutes.

## 6. Remaining Production Risks
- **Memory Pressure:** With the full tensor now weighing in at ~433 MB, loading this entirely into VRAM during training is perfectly fine on a Tesla T4 (16GB). However, if we scale to `v3.0` (15m Intraday, ~3 GB), we will need to augment `train_models.py` to use batched disk-loading (via PyTorch DataLoaders with `num_workers`) rather than aggressively loading everything into RAM at once.

## 7. Confirmation 
> [!IMPORTANT]
> **`CORE/v1.0` remains 100% immutable and intact.** 
> The new dataset was successfully siloed directly into `ml_engine/data/tensors/NIFTY50/v2.0/`. The original baseline dataset is completely isolated and retains all original verification hashes. No model training was executed on `v2.0`.
