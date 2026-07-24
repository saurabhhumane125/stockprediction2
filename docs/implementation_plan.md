# Milestone M16.3 – Comprehensive Implementation Plan: Task-Aware Post-Training Pipeline

## Overview & Executive Summary

During Milestone M16.1, a production incident investigation revealed that training completed successfully, but the pipeline failed post-training inside `CalibrationManager.fit()` with `IndexError: index 1 is out of bounds for axis 1 with size 1`. This failure occurred because legacy binary classification routines (`CalibrationManager`, F1 threshold optimization, and binary diagnostic plots) were executed unconditionally during regression model training runs.

This document details the architectural plan to replace the legacy binary-only post-training logic with a **TaskType-aware `PostProcessingDispatcher`**. The new architecture ensures that every task type (`BINARY_CLASSIFICATION`, `REGRESSION`, `MULTI_OUTPUT_REGRESSION`, `MULTICLASS_CLASSIFICATION`) executes its own dedicated, production-grade post-processing workflow without scattered `if task_type == ...` checks in the orchestrator.

---

## Complete Post-Training Architecture Diagram

```
Training & Checkpoint Restoration Complete
                   │
                   ▼
       PostProcessingDispatcher.dispatch()
                   │
         ┌─────────┼───────────────────────────┬──────────────────────────┐
         ▼         ▼                           ▼                          ▼
TaskType: BINARY   TaskType: REGRESSION        TaskType: MULTI_OUTPUT     TaskType: MULTICLASS
         │         │                           │                          │
         ├─ Metrics (Accuracy, F1, AUC)        ├─ Metrics (RMSE, MAE, R2, IC)             ├─ Metrics (Multi-output RMSE)             ├─ Metrics (Accuracy, Macro-F1)
         ├─ Calibration (Platt / Isotonic)     ├─ Residual Stats (mean, std, max_err)     ├─ Residual Stats (mean, std)              ├─ Multiclass Probabilities
         ├─ F1 Threshold Optimization          ├─ Regression Plots                        ├─ Identity Calibrator Artifact            └─ Identity Calibrator Artifact
         └─ Binary Plots (ROC, PR, Hist)       │  (pred_vs_actual.png,                    │  (method="none")                             (method="none")
                   │                           │   residual_histogram.png)                │                                          │
                   │                           └─ Identity Calibrator Artifact            │                                          │
                   │                              (method="none")                         │                                          │
                   │                                   │                                  │                                          │
                   └───────────────────────────────────┼──────────────────────────────────┴──────────────────────────────────────────┘
                                                       │
                                                       ▼
                                            Artifact Serialization
                                              (metadata.json)
                                                       │
                                                       ▼
                                                RegistryManager
                                              (register_candidate)
                                                       │
                                                       ▼
                                              Production Ingestion
                                               (InferenceEngine)
```

---

## Detailed File Analysis & Contract Specifications

### 1. `ml_engine/training/post_processing.py` [NEW]

- **Current Responsibility:** None (File does not exist).
- **Why It Must Be Added:** To provide a single, authoritative dispatcher (`PostProcessingDispatcher`) for post-training operations, eliminating scattered task-type logic from `TrainingOrchestrator`.
- **Exact Responsibility After Addition:** 
  - Expose static method `PostProcessingDispatcher.dispatch(...)`.
  - Route execution based on `TaskType` to private task-specific methods:
    - `_process_binary()`
    - `_process_regression()`
    - `_process_multi_output_regression()`
    - `_process_multiclass()`
  - Return standardized dictionary payload containing evaluation metrics, plot paths, and calibrator artifact path.
- **Public Interfaces Affected:** None (New module).
- **Internal Methods Introduced:** `dispatch()`, `_process_binary()`, `_process_regression()`, `_process_multi_output_regression()`, `_process_multiclass()`.
- **Dependencies:** `ml_engine.core.types.TaskType`, `ml_engine.training.metrics_registry.MetricsRegistry`, `ml_engine.calibration.calibrator.CalibrationManager`, `ml_engine.training.evaluation_plots`.
- **Risks:** Low. Isolated static module.
- **Backward Compatibility Impact:** None.
- **Test Cases Required:** Unit tests in `test_post_processing_dispatcher.py` for all 4 task types.

---

### 2. `ml_engine/training/evaluation_plots.py` [MODIFY]

- **Current Responsibility:** Generates binary evaluation plots (ROC curves, PR curves, calibration curves, probability histograms, logit histograms, metrics vs. threshold).
- **Why It Must Change:** Lacks diagnostic plotting functions for regression models (`y_true` and `y_pred` continuous arrays). Furthermore, headless server execution must be enforced (`matplotlib.use('Agg')`) to prevent Tcl/Tk GUI display errors.
- **Exact Responsibility After Modification:** 
  - Enforce headless Matplotlib execution (`matplotlib.use('Agg')`).
  - Retain binary plotting `generate_evaluation_plots()`.
  - Provide `generate_regression_evaluation_plots(y_true, y_pred, output_dir, prefix="val")` generating:
    1. `pred_vs_actual.png`: Scatter plot of Actual vs Predicted values with a 1:1 reference line.
    2. `residual_histogram.png`: Histogram distribution of model prediction errors (`y_true - y_pred`).
- **Public Interfaces Affected:** New public function `generate_regression_evaluation_plots()`. Existing `generate_evaluation_plots()` signature remains unchanged.
- **Internal Methods Affected:** Top-level module import statements.
- **Dependencies:** `matplotlib`, `numpy`, `os`.
- **Risks:** Low.
- **Backward Compatibility Impact:** None. Binary plot generation is untouched.
- **Test Cases Required:** Verify image files are generated on disk for regression inputs without Tcl/Tk exceptions.

---

### 3. `ml_engine/calibration/calibrator.py` [MODIFY]

- **Current Responsibility:** Fits and applies probability calibrator models (`IsotonicRegression`, Platt scaling).
- **Why It Must Change:** Currently, `CalibrationManager.transform()` attempts binary array slicing (`y_prob[:, 1]`) unconditionally if `y_prob.ndim > 1`. For regression models saved with an uncalibrated identity calibrator (`method_name == "none"`), `transform()` crashed on 2D arrays of shape `(N, 1)`.
- **Exact Responsibility After Modification:** 
  - If `self.method_name == "none"`, return `y_prob` directly as an uncalibrated identity pass-through.
  - Apply binary 2D array slicing (`y_prob[:, 1]`) only if `is_2d and y_prob.shape[1] == 2`.
- **Public Interfaces Affected:** `CalibrationManager.transform(y_prob)` signature remains unchanged; internal handling updated.
- **Internal Methods Affected:** `CalibrationManager.transform()`.
- **Dependencies:** `numpy`, `ml_engine.calibration.methods`.
- **Risks:** Low.
- **Backward Compatibility Impact:** 100% backward compatible. Legacy binary models retain full calibration capability.
- **Test Cases Required:** Verify `CalibrationManager("none").transform()` returns 2D regression arrays `(N, 1)` without error.

---

### 4. `ml_engine/training/training_pipeline.py` [MODIFY]

- **Current Responsibility:** Orchestrates PyTorch model training, validation, evaluation, calibration, plotting, artifact serialization, and registry registration.
- **Why It Must Change:** Contains legacy inline post-training code that unconditionally executes binary probability calibration and binary plot generation regardless of `TaskType`.
- **Exact Responsibility After Modification:** 
  - Delegate post-training metrics calculation, calibration, thresholding, and plotting to `PostProcessingDispatcher.dispatch()`.
  - Maintain clean, readable orchestrator control flow without inline task-type checks.
- **Public Interfaces Affected:** `TrainingOrchestrator.run()` return payload remains consistent.
- **Internal Methods Affected:** `TrainingOrchestrator.run()`.
- **Dependencies:** `ml_engine.training.post_processing.PostProcessingDispatcher`.
- **Risks:** Low. Simplifies control flow.
- **Backward Compatibility Impact:** None.
- **Test Cases Required:** End-to-end dry runs for both Binary Classification and Regression tasks.

---

### 5. `ml_engine/inference/engine.py` [MODIFY]

- **Current Responsibility:** Loads active production models from registry, applies feature scaling, creates sequences, executes neural network forward pass, applies calibration, and decodes predictions.
- **Why It Must Change:** Currently executes calibration in `predict()` whenever `self.calibrator` is present, assuming binary classification.
- **Exact Responsibility After Modification:** 
  - Check `task_type` from model manifest.
  - Apply probability calibration only if `task_type == TaskType.BINARY_CLASSIFICATION`.
  - Pass `raw_logits` directly through for `REGRESSION` and `MULTI_OUTPUT_REGRESSION`.
- **Public Interfaces Affected:** `ProductionInferenceEngine.predict()` signature remains unchanged.
- **Internal Methods Affected:** `ProductionInferenceEngine.predict()`.
- **Dependencies:** `ml_engine.core.types.TaskType`.
- **Risks:** Low.
- **Backward Compatibility Impact:** None.
- **Test Cases Required:** Run `test_inference.py` suite.

---

## Design Decisions & Architectural Justifications

1. **Why current implementation is insufficient:**
   The current post-training code in `training_pipeline.py` contains hardcoded assumptions that every model outputs binary class probabilities. As a result, regression runs crash post-epoch during calibration fitting.

2. **Why proposed architecture is superior:**
   By introducing `PostProcessingDispatcher`, post-training logic is centralized and driven strictly by `TaskType`. Adding support for new task types in the future requires modifying only the dispatcher, preserving the Open-Closed Principle.

3. **Alternative approaches considered:**
   - *Inline `if task_type == TaskType.REGRESSION: pass` checks in `training_pipeline.py`*: Rejected because it leaves dead code, pollutes orchestrator logic, and violates architectural design rules.
   - *Disabling calibration completely*: Rejected because binary classification models still require probability calibration for downstream decision engines.

4. **Long-Term Maintainability & Production Implications:**
   The architecture remains 100% configuration-driven, robust against runtime shape mismatches, and fully compliant with the production model registry contract.

---

## Sub-Milestone Implementation Breakdown

### Milestone M16.3.1 – Dispatcher Scaffolding & Calibration Refactoring
- **Files Touched:** `ml_engine/training/post_processing.py` (New), `ml_engine/calibration/calibrator.py`.
- **Expected Output:** `PostProcessingDispatcher` class structure and pass-through support for `method_name == "none"`.
- **Verification Steps:** Unit tests in `test_post_processing_dispatcher.py`.
- **Rollback Risk:** Zero (New isolated file).

### Milestone M16.3.2 – Regression Evaluation Plotting
- **Files Touched:** `ml_engine/training/evaluation_plots.py`.
- **Expected Output:** Headless Matplotlib execution and `generate_regression_evaluation_plots()`.
- **Verification Steps:** Run function with synthetic regression arrays and check on-disk PNG generation.
- **Rollback Risk:** Zero.

### Milestone M16.3.3 – Orchestrator Refactoring
- **Files Touched:** `ml_engine/training/training_pipeline.py`.
- **Expected Output:** `TrainingOrchestrator.run()` calls `PostProcessingDispatcher.dispatch()`.
- **Verification Steps:** Run full pipeline test suite across binary and regression configs.
- **Rollback Risk:** Low (Single method replacement in orchestrator).

### Milestone M16.3.4 – Inference Engine Alignment
- **Files Touched:** `ml_engine/inference/engine.py`.
- **Expected Output:** Task-aware calibration dispatch in `predict()`.
- **Verification Steps:** `test_inference.py`.
- **Rollback Risk:** Low.

---

## Verification Plan

1. **Unit Testing:**
   Run `pytest` across all modified and newly created modules:
   ```powershell
   python -m pytest ml_engine/tests/test_post_processing_dispatcher.py ml_engine/tests/test_target_framework.py ml_engine/tests/test_feature_target_separation.py ml_engine/tests/test_tensors.py ml_engine/tests/test_inference.py
   ```
2. **Binary Task Verification:**
   Confirm binary runs generate `calibrator.pkl`, F1 thresholds, ROC curves, PR curves, and probability histograms.
3. **Regression Task Verification:**
   Confirm regression runs generate regression metrics (RMSE, MAE, R2, IC), residual statistics (`mean_residual`, `std_residual`), regression diagnostic plots (`pred_vs_actual.png`, `residual_histogram.png`), and identity calibrator artifacts (`calibrator.pkl`).
4. **Registry Verification:**
   Confirm model artifacts pass sha256 checksum verification and `RegistryManager.register_candidate()` without missing artifact errors.

---

## STOP CONDITION

**No source code has been modified during this planning milestone.**
Execution is stopped. Awaiting explicit user approval before proceeding to implementation.
