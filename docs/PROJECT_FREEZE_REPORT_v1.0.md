# PROJECT FREEZE REPORT v1.0

## SECTION 1: CURRENT PROJECT PHASE
- **Current Phase:** Production ML Training
- **Current Objective:** Baseline GPU Training using CORE/v2.0
- **Next Objective:** Architecture Comparison

## SECTION 2: EXPERIMENT LIFECYCLE
The complete machine learning lifecycle for TradePredict strictly follows this sequence:
1. **Dataset**: Raw data is fetched in parallel via `yfinance` for a configured stock universe (e.g., NIFTY 50).
2. **Feature Engineering**: Calculates 23 technical indicators and applies strict outlier cleaning, filling missing values dynamically.
3. **Tensor Generation**: The `TensorBuilder` splits the dataset chronologically (Train/Val/Test), generates overlapping fixed-length sequences (48 days), assigns 1-day future binary targets, and saves to PyTorch `.pt` files.
4. **Training**: `TrainingOrchestrator` executes the training loop using GPU (if available) with PyTorch AMP mixed precision. Early stopping is monitored via Validation Loss.
5. **Evaluation**: Computes Accuracy, Precision, Recall, F1-Score, AUC, and Confusion Matrices on the Test set.
6. **Calibration**: An Isotonic Regression calibrator is fitted to the test outputs to convert raw model logits into true probability estimates.
7. **Candidate**: Training outputs are serialized to `artifacts/candidates/` and registered with a unique run ID in `manifest.json`.
8. **Production**: The best performing candidate is explicitly promoted in the Registry via semantic versioning, which the FastAPI backend instantly detects and loads for live inference.
9. **Monitoring**: (Future Phase) Real-world performance tracking via the analytics backend.
10. **Rollback**: If degradation is detected, the registry demotes the `Production` model and seamlessly restores the previous `Archived` model.

## SECTION 3: TRAINING OUTPUTS
After the training pipeline successfully completes, it produces a strict set of immutable artifacts:
- **Model Weights (`model.pth`)**: The saved PyTorch `state_dict` of the trained neural network (e.g., GRU).
- **Calibrator (`calibrator.pkl`)**: The serialized scikit-learn `IsotonicRegression` model used to scale logits to probabilities.
- **Scaler (`scaler.pkl`)**: The fitted Scikit-Learn `StandardScaler` used to normalize live inference inputs to match training scales.
- **Metadata (`metadata.json`)**: Feature lists, sequence lengths, and architecture parameters required to reconstruct the model forward pass perfectly.
- **Manifest (`manifest.json`)**: The registry entry that defines the model's lineage, dataset version, and lifecycle status (e.g., Candidate).
- **Training History (`training_report.json`)**: Epoch-by-epoch loss/accuracy values and final evaluation metrics.
- **Metrics (`training_report.md`)**: A human-readable markdown version of the training history.
- **Experiment Record (`tracking.db`)**: SQLite entries logging the system hardware, exact hyperparameters, and timestamps via `ExperimentTrackingCallback`.

## SECTION 4: VERIFIED PROJECT DECISIONS
The following architectural decisions have been strictly enforced and are permanently frozen:
- **CORE/v1.0 remains immutable.** It is the legacy baseline verification dataset.
- **CORE/v2.0 is the official production daily dataset.** Uses 50 active NIFTY 50 constituents.
- **CORE/v3.0 will be intraday only.** A future expansion targeting 15m intervals.
- **Notebook contains orchestration only.** Jupyter/Colab notebooks do not hold business logic, only top-level imports and function calls.
- **Business logic belongs inside ml_engine.**
- **Training comparisons use identical datasets.** Models are only compared if trained and evaluated on the exact same dataset version (e.g. `CORE/v2.0`).
- **Registry controls promotion.** Artifacts do not move; their status tag in `manifest.json` dictates their environment.
- **Backend always loads Production model.** FastAPI specifically queries the Model Registry for the active `Production` flag.
- **Version everything.** 
- **Never overwrite datasets.** Re-runs create new versions.
- **Never overwrite models.** Retraining creates a new unique run hash.
- **Analyze before implementing.**
- **Only production-grade implementations.** No placeholders, no `pass`, no hardcoded lists, no notebook-only implementations.

## SECTION 5: CURRENT VERIFIED LIMITATIONS
- **Prediction horizon:** Fixed at exactly 1 day.
- **Dataset scope:** Limited to the top 50 active NIFTY 50 constituents.
- **Dataset size:** ~433 MB (approx 100k rows, 97k overlapping sequences).
- **Vision pipeline status:** Exists as legacy codebase in `frontend_v1_reference`, deliberately disabled/untested in current v2 sprint.
- **Current production risks:** The PyTorch pipeline loads the entire `.pt` tensors into CPU RAM before sending mini-batches to the GPU. This is safe for 433 MB, but risks Out-Of-Memory (OOM) failures for the future Intraday datasets (~3 GB+).
- **Training status:** A baseline GPU test run was successfully completed on `CORE/v1.0`. Real training on `CORE/v2.0` has not yet begun.

## SECTION 6: FUTURE ROADMAP
**Current Phase**
↓
Baseline GPU Training
↓
Training Analysis
↓
Architecture Comparison
↓
Hyperparameter Optimization
↓
Best Model Promotion
↓
CORE/v3.0 (Intraday)
↓
Intraday Training
↓
Vision Integration
↓
**Production Deployment**

## SECTION 7: PROJECT STATUS SUMMARY
- **Overall Completion Percentage:** ~65%
- **Completed Milestones:**
  - Engineering Platform Setup (Backend + Frontend)
  - Unified Registry Integration
  - Data Pipeline (Download, Validation, Cleaning, Features, Tensors)
  - Production `CORE/v2.0` Dataset Generation
  - Colab Environment GPU Bootstrap
- **Current Milestone:** Baseline GPU Training (CORE/v2.0)
- **Remaining Milestones:** Architecture Comparison, HPO, Model Promotion, Intraday V3, Live Deployment.
- **Overall Engineering Readiness:** Fully ready. The codebase correctly routes frontend requests to the FastAPI backend, which seamlessly interfaces with the ML Registry and Prediction Service.
- **Overall ML Readiness:** Fully ready. PyTorch datasets, dataloaders, mixed precision scaling, and metrics are successfully verified end-to-end.
- **Production Readiness:** **Blocked** (Awaiting finalized trained model promotion).
