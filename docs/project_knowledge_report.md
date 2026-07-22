# PROJECT KNOWLEDGE REPORT (PRE-TRAINING BASELINE)

## SECTION 1: PROJECT OVERVIEW
**Project Purpose:**
TradePredict is an enterprise-grade, production-ready Machine Learning platform designed to forecast stock market trends (binary classification of positive/negative returns), analyze market risk, and optimize portfolio strategies.

**Architecture & Technology Stack:**
- **Frontend:** Next.js (App Router), React, Tailwind CSS, shadcn/ui, Lucide Icons, Recharts.
- **Backend:** FastAPI (Python), Uvicorn, SQLite (Database), Pydantic (Validation).
- **ML Engine:** PyTorch (Deep Learning), Pandas/NumPy (Data Processing), Scikit-Learn (Calibration/Metrics), yfinance (Data Source).
- **Deployment Architecture:** The system is decoupled into a frontend UI, a backend API server, and an offline ML Engine. The ML Engine is designed to be executable both locally and in Google Colab (for GPU acceleration) via a dedicated bootstrap layer. 
- **Overall Workflow:** 
  1. `ml_engine` orchestrates data ingestion from Yahoo Finance/NSE, validates it, engineers features, and serializes PyTorch tensors.
  2. The Training System trains models (e.g., GRU) using GPU acceleration, calibrates outputs, and registers them in the Model Registry.
  3. The FastAPI Backend loads the `Production` model from the Registry and serves inference endpoints.
  4. The Next.js Frontend consumes these endpoints to present real-time dashboards, historical predictions, and analytics.

## SECTION 2: FOLDER STRUCTURE
- **`backend/`**: Contains the FastAPI server, API routes, scheduled tasks, and prediction serving logic. It acts as the bridge between the ML Registry and the Frontend.
- **`frontend/`**: Contains the Next.js App Router application. Responsible for the user interface, routing, and data visualization.
- **`frontend_v1_reference/`**: PERMANENTLY READ ONLY. Contains legacy frontend code retained purely for architectural reference.
- **`ml_engine/`**: The core data science and machine learning platform. Contains all logic for dataset generation, model training, evaluation, and registry management.
- **`ml_engine/data/`**: Manages the ETL pipeline (download, validation, cleaning, feature engineering, and tensor generation).
- **`ml_engine/training/`**: Contains the PyTorch training loop, orchestrator, callbacks, and evaluation logic.
- **`ml_engine/registry/`**: Manages model lifecycle states (Candidate, Production, Archived, etc.) and semantic versioning.
- **`ml_engine/config/`**: Centralized configuration files (e.g., `colab.yaml`, `training_config.py`).
- **`ml_engine/scripts/`**: Executable CLI scripts (e.g., `generate_dataset.py`, `train_models.py`, `prepare_colab.py`) for orchestrating pipelines.
- **`ml_engine/colab/`**: Contains the bootstrap and synchronization logic for executing training workloads in Google Colab.
- **`ml_engine/experiments/`**: Contains the SQLite-based experiment tracking system for logging metrics, parameters, and run metadata.

## SECTION 3: BACKEND
- **FastAPI Architecture:** Modular design using APIRouters.
- **Routes:** API endpoints for predictions, historical analytics, system status, and vision processing.
- **Services:** Decoupled business logic handling prediction generation, data formatting, and registry interactions.
- **Utilities:** Logging, configuration, and error handling helpers.
- **Authentication:** JWT-based authentication via HttpOnly cookies.
- **Schedulers:** Background tasks for periodic data refreshing and predictions (Verified via APScheduler/FastAPI background tasks).
- **Model Loading:** Dynamically loads the active `Production` model and its corresponding calibrator from the Model Registry.
- **Prediction Flow:** Receives a ticker, fetches recent data, engineers features matching the training pipeline, runs the model forward pass, calibrates the probability, and returns the result.
- **Vision Pipeline:** Endpoints for OCR and visual data processing (Status: Retained and untouched as per permanent rules).

## SECTION 4: FRONTEND
- **Architecture:** Next.js 14+ App Router with React Server/Client Components.
- **Feature Modules:** Grouped by business domain (e.g., `(auth)`, `(dashboard)`).
- **Routing:** Route groups for `/login`, `/dashboard`, `/analytics`, `/stocks`, `/history`, `/vision`, etc.
- **API Layer:** Axios-based interceptors (`src/lib/api`) for communicating with the FastAPI backend.
- **Shared Components:** Reusable UI elements built on Radix UI and Tailwind CSS (`@/components/ui`).
- **State Management:** React Hooks (`useState`, `useEffect`) and form state via `react-hook-form` + `zod`.
- **Authentication Flow:** Users log in via the `/login` route, which calls the backend to set an HttpOnly cookie. The frontend relies on this cookie for subsequent authorized requests.

## SECTION 5: ML ENGINE
- **`data/download/`**: Parallelized data fetching via `yfinance`.
- **`data/validation/`**: Strict schema and bounds checking for raw and engineered data. Ensures fail-fast behavior.
- **`data/cleaning/`**: Outlier detection, NaN imputation, and forward/backward filling.
- **`data/features/`**: Calculates 23 technical indicators (e.g., MACD, RSI, Bollinger Bands).
- **`data/tensors/`**: The `TensorBuilder` applies chronological splitting, sequence windowing, and serializes outputs into `.pt` (PyTorch) format.
- **`training/`**: The `TrainingOrchestrator` manages the epoch loop, optimizer, loss function (BCEWithLogitsLoss), and metric calculation.
- **`evaluation/`**: Calculates Accuracy, Precision, Recall, F1-Score, AUC, and Confusion Matrices.
- **`optimization/`**: (Not verified - currently reserved for future HPO).
- **`calibration/`**: Uses `IsotonicRegression` to map raw logits to true probabilities.
- **`registry/`**: The `ModelRegistry` component handles reading/writing `manifest.json` metadata for models and tracking their status.
- **`experiments/`**: SQLite-based tracking (`tracking.db`) that captures parameters, epoch metrics, and system metadata via `ExperimentTrackingCallback`.
- **`scripts/train_models.py`**: CLI entry point to orchestrate the end-to-end training and registration process.

## SECTION 6: DATASETS
- **CORE/v1.0**: The baseline dataset. Built using 5 hardcoded tickers (e.g., RELIANCE.NS, TCS.NS). Used for initial pipeline verification.
- **CORE/v2.0**: The newly generated expansion dataset. Contains 50 active NIFTY 50 constituents dynamically fetched from the NSE archive. 
  - **Rows**: 100,381
  - **Date Range**: 2018-01-01 to 2026-06-22
  - **Tensor Size**: ~433 MB
- **CORE/v3.0**: Future placeholder (Intraday 15m data).
- **Features**: 23 technical indicators.
- **Sequence Length**: 48 days.
- **Forecast Horizon**: 1 day.
- **Tensor Layout**: `[batch_size, sequence_length, num_features]`. Saved as `train.pt`, `val.pt`, `test.pt`.
- **Versioning Strategy**: Datasets are completely immutable. New configurations result in a new `/vX.X/` subdirectory with its own `manifest.json`.

## SECTION 7: MODEL REGISTRY
- **Candidate**: Models that have completed training but have not yet been evaluated for production.
- **Production**: The single active model used by the Backend for live inference.
- **Archived**: Previously production models that have been replaced.
- **Rolled Back**: Models that failed in production and were demoted.
- **Deprecated**: Models that are no longer supported.
- **Promotion Workflow**: A strict transition from `Candidate` -> `Production`. Automatically archives the previous production model.
- **Rollback Workflow**: Demotes the current `Production` model to `Rolled Back` and restores the most recent `Archived` model.

## SECTION 8: TRAINING SYSTEM
- **Training Pipeline**: Managed by `TrainingOrchestrator`. Iterates through PyTorch DataLoaders.
- **Callbacks**: Extensible interface (`TrainingCallback`). Used for experiment tracking and early stopping.
- **Metrics**: Tracked per epoch (Train/Val Loss, Accuracy) and finalized with F1/AUC/Precision/Recall.
- **Experiment Tracking**: SQLite backend logging system metadata, hyperparams, and metrics.
- **Checkpointing**: `CheckpointManager` saves the best weights based on validation loss and restores them at the end of training.
- **Mixed Precision**: Supported via PyTorch AMP (`torch.cuda.amp.GradScaler`).
- **GPU Support**: Automatic detection and utilization of CUDA devices.
- **Calibration**: Post-training step using `CalibratorModelWrapper` to wrap the base PyTorch model with an Isotonic Regressor for inference.

## SECTION 9: COLAB
- **Bootstrap**: `prepare_colab.py` initializes the environment, installs dependencies, and resolves paths.
- **Drive Mounting**: Automatically mounts Google Drive for persistent storage of artifacts and datasets across ephemeral sessions.
- **Execution Flow**: Designed to be portable. The exact same scripts (`generate_dataset.py`, `train_models.py`) are executed in Colab without modification.
- **Artifact Synchronization**: Model artifacts, calibrators, and manifests are saved directly to the mounted Google Drive, immediately becoming available to the local machine synced to that Drive.

## SECTION 10: CURRENT VERIFIED PROJECT STATUS
- **Backend Status**: Operational and serving endpoints on port 8000.
- **Frontend Status**: Operational on port 3000 (Next.js routing glitch recently resolved).
- **ML Engine Status**: Operational. Dataset generation and tensor building are fully functional.
- **Registry Status**: Operational. Promotion and rollback workflows are intact.
- **GPU Status**: Verified in Colab (Tesla T4 compatible).
- **Dataset Status**: `CORE/v1.0` (Immutable baseline) and `CORE/v2.0` (NIFTY50 expansion) are fully generated and verified.
- **Training Readiness**: Ready for Baseline GPU Training on `CORE/v2.0`.
- **Current Limitations**: In-memory tensor loading may face limits if dataset scales to `v3.0` (Intraday).

## SECTION 11: CURRENT ROADMAP
Current
↓
Baseline Training
↓
Architecture Comparison
↓
Hyperparameter Optimization
↓
Model Promotion
↓
CORE/v3.0
↓
Intraday
↓
Production Deployment

## SECTION 12: KNOWN LIMITATIONS
- **Current Prediction Horizon**: Fixed at 1 day.
- **Current Stock Universe**: NIFTY 50 (via `CORE/v2.0`).
- **Current Dataset Size**: ~433 MB (100,000+ rows).
- **Vision Pipeline Status**: Unmodified and untested in recent sprints.
- **Current Production Risks**: The PyTorch DataLoader currently loads entire `.pt` tensor files into RAM. This is viable for 433 MB but will cause Out-Of-Memory (OOM) crashes when transitioning to Intraday data (~3 GB+).

## SECTION 13: PROJECT RULES
1. **Production-grade implementations only:** No placeholders, mock data, or notebook-only logic.
2. **Never overwrite datasets:** Existing `CORE/vX.X` folders are strictly immutable.
3. **Never overwrite production models:** The registry handles versioning; artifacts are immutable.
4. **Version everything:** Datasets, models, and manifests are all explicitly versioned.
5. **Reuse production code:** Avoid duplicating logic across the ML engine.
6. **Notebook only orchestrates:** Jupyter/Colab notebooks contain zero business logic; they only import and call `ml_engine` scripts.
7. **Business logic belongs in ml_engine:** All ML data processing, training, and evaluation logic is encapsulated within the package.
8. **Analyze before implementing:** All tasks must begin with a thorough inspection of existing code and architecture.
9. **frontend_v1_reference is PERMANENTLY READ ONLY:** Never modify the legacy reference code.
