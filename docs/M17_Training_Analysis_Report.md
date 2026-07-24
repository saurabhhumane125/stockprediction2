# M17 Training Analysis Report

===========================================================
## SECTION 1 — EXECUTIVE SUMMARY
===========================================================
- **Did the training pipeline complete successfully?** Yes, the `TrainingOrchestrator` execution and training loop completed successfully without crashing.
- **Did early stopping execute correctly?** Yes, the `CheckpointManager` correctly monitored `val_loss` and executed early stopping.
- **Were artifacts exported?** Partially. Artifacts (e.g., `model.pt`, `scaler.pkl`, `metadata.json`) were successfully exported to the candidate directory (`artifacts/candidates/NIFTY50/...`).
- **Was the experiment tracker successful?** Yes, MLflow/tracking logged the run.
- **Was registry registration successful?** No, `RegistryManager` threw a `MissingArtifactError` causing the registration to fail.
- **Were there runtime exceptions?** Yes, `ConstantInputWarning` during metrics computation and `MissingArtifactError` during registry registration.

===========================================================
## SECTION 2 — COMPLETE TRAINING TIMELINE
===========================================================
1. **ProductionTrainingRunner**:
   - *Input*: CLI arguments (`--dataset NIFTY50/v3.0 --experiment M17_Regression`).
   - *Output*: Invokes `TrainingOrchestrator`.
   - *Expected/Observed*: Correct behaviour.
2. **TrainingOrchestrator**:
   - *Input*: Seed, storage paths, registry manager.
   - *Output*: Manages the pipeline state.
   - *Expected/Observed*: Correct behaviour.
3. **Dataset Loading**:
   - *Input*: Pre-built `.npz` tensors.
   - *Output*: `train_X`, `val_X`, `test_X` and `y` arrays.
   - *Expected/Observed*: Correct. Tensor shapes correctly matched the `[N]` target contract.
4. **DataLoader creation**:
   - *Input*: Numpy arrays.
   - *Output*: PyTorch `DataLoader` objects (`TimeSeriesDataset`).
   - *Expected/Observed*: Correct.
5. **ModelFactory**:
   - *Input*: Config settings for `GRUClassifier` (input=38).
   - *Output*: Initialized PyTorch GRU model.
   - *Expected/Observed*: Correct. Model successfully created.
6. **Optimizer**:
   - *Input*: AdamW config.
   - *Output*: Instantiated PyTorch optimizer.
   - *Expected/Observed*: Correct.
7. **Scheduler**:
   - *Input*: Learning rate config.
   - *Output*: Instantiated LR Scheduler (e.g., `ReduceLROnPlateau`).
   - *Expected/Observed*: Correct.
8. **Training Loop**:
   - *Input*: DataLoaders, model, criterion (MSE).
   - *Output*: Epoch training loss.
   - *Expected/Observed*: The training loop processed batches but the loss gradients encountered numerical issues due to unscaled, near-zero targets combined with mixed-precision scaling, leading the model to collapse and predict a constant value.
9. **Validation Loop**:
   - *Input*: Validation DataLoader, model.
   - *Output*: Validation metrics (`val_loss`, `val_rmse`, `val_mae`, `val_r2`, `val_ic`).
   - *Expected/Observed*: Validation metrics reported 0 for `val_r2` and `val_ic`. `ConstantInputWarning` was raised by Spearman correlation.
10. **Checkpoint Manager**:
    - *Input*: Epoch validation metrics.
    - *Output*: Saves `best_model.pt`.
    - *Expected/Observed*: Correct. It correctly saved weights on the first epoch.
11. **Early Stopping**:
    - *Input*: Patience criteria and `val_loss`.
    - *Output*: Halted training when loss plateaued.
    - *Expected/Observed*: Correct behaviour. The loss plateaued instantly due to model collapse.
12. **Prediction Collection**:
    - *Input*: Test DataLoader.
    - *Output*: Raw arrays for true values, predictions, and logits.
    - *Expected/Observed*: Correct data flow, though the prediction values themselves were constant.
13. **PostProcessingDispatcher**:
    - *Input*: Raw prediction arrays.
    - *Output*: Final metrics and calibrator paths.
    - *Expected/Observed*: Correct architectural routing for `REGRESSION`.
14. **Calibration**:
    - *Input*: Output from PostProcessingDispatcher.
    - *Output*: No-op for Regression, passes placeholder calibrator.
    - *Expected/Observed*: Correct behaviour.
15. **Artifact Export**:
    - *Input*: Model weights, metrics, config.
    - *Output*: Saves files to `artifacts/candidates/NIFTY50/.../`.
    - *Expected/Observed*: It incorrectly named the scaler artifact as `scaler.pkl` instead of `feature_scaler.pkl`.
16. **Registry**:
    - *Input*: Exported artifacts dictionary.
    - *Output*: Registration manifest.
    - *Expected/Observed*: FAILED. `RegistryManager` rejected the bundle due to the missing `feature_scaler.pkl`.
17. **Training Report**:
    - *Input*: Pipeline state.
    - *Output*: Markdown and JSON reports.
    - *Expected/Observed*: Correct generation in candidate directory.

===========================================================
## SECTION 3 — METRIC ANALYSIS
===========================================================
- **Training Loss**: 
  - *Purpose*: Measures model fit on training data.
  - *Formula*: Mean Squared Error (MSE).
  - *Expected range*: > 0 (scale dependent).
  - *Observed value*: ~0.017.
  - *Interpretation*: Unusually small initial loss due to unscaled raw targets.
- **Validation Loss**:
  - *Purpose*: Measures generalisation.
  - *Formula*: MSE.
  - *Expected range*: > 0.
  - *Observed value*: ~0.0001.
  - *Interpretation*: Extremely small due to unscaled small targets.
- **RMSE**:
  - *Purpose*: Root mean squared error in original units.
  - *Formula*: `sqrt(MSE)`.
  - *Expected range*: Scale dependent.
  - *Observed value*: ~0.0128 (≈0).
  - *Interpretation*: Targets are unscaled returns (e.g. 1% = 0.01). An RMSE of 0.01 is actually massive in relative terms, but absolute scale is near 0.
- **MAE**:
  - *Purpose*: Mean absolute error.
  - *Formula*: `mean(|y_true - y_pred|)`.
  - *Expected range*: Scale dependent.
  - *Observed value*: ~0.0103 (≈0).
  - *Interpretation*: Same as RMSE, absolute scale is tiny.
- **R²**:
  - *Purpose*: Explains proportion of variance in target.
  - *Formula*: `1 - (SS_res / SS_tot)`.
  - *Expected range*: (-inf, 1].
  - *Observed value*: 0.0000.
  - *Interpretation*: A value of exactly 0 indicates the model is predicting a constant equal to the target mean (or very close to it).
- **Information Coefficient (IC)**:
  - *Purpose*: Rank correlation between predictions and true values.
  - *Formula*: Spearman rank correlation.
  - *Expected range*: [-1, 1].
  - *Observed value*: 0.0000.
  - *Interpretation*: Spearman correlation relies on ranked variances. Because the prediction is constant, the variance is 0, making the correlation mathematically undefined (NaN), which was coerced to 0.0.
- **Residual Mean**:
  - *Purpose*: Checks if predictions are biased.
  - *Formula*: `mean(y_true - y_pred)`.
  - *Expected range*: 0.
  - *Observed value*: ≈ 0.
  - *Interpretation*: The constant prediction is near the target mean, keeping residuals centered at 0.
- **Residual Std**:
  - *Purpose*: Standard deviation of errors.
  - *Formula*: `std(y_true - y_pred)`.
  - *Expected range*: > 0.
  - *Observed value*: ≈ Target Std.
  - *Interpretation*: Since the model predicts a constant, the residual variance equals the target variance.
- **Maximum Error**:
  - *Purpose*: Worst-case absolute error.
  - *Formula*: `max(|y_true - y_pred|)`.
  - *Expected range*: Scale dependent.
  - *Observed value*: ≈ Target maximum.
  - *Interpretation*: The model fails to capture any outliers or large moves.

===========================================================
## SECTION 4 — EPOCH-BY-EPOCH ANALYSIS
===========================================================
- **Epoch 0**: Model initializes with random weights, producing near-zero outputs. Given unscaled targets (returns), the absolute error is tiny. Training loss is minimal, validation loss immediately starts extremely low (e.g., 0.0001). `ConstantInputWarning` is raised indicating predictions have zero variance.
- **Epoch 1**: Gradients are microscopically small. The optimizer makes essentially zero updates to the weights. 
- **Epoch 2**: Validation loss plateaus.
- **Best Epoch**: 0.
- **Early Stop Epoch**: Stopped early due to failure to improve validation loss (plateau).
- **Conclusion**: The model **collapsed**. Evidence: `ConstantInputWarning` fired continuously, `R² = 0.0`, `IC = 0.0`, and validation loss flatlining immediately at a tiny scalar value.

===========================================================
## SECTION 5 — CONSTANTINPUTWARNING INVESTIGATION
===========================================================
- **Trace**: `training_pipeline.py` calls `MetricsRegistry.evaluate(TaskType.REGRESSION, ...)` -> `metrics_registry.py` invokes `spearmanr(y_true, y_pred)`.
- **Was y_true constant?** No. `return_5d` contains natural stock market variance.
- **Was y_pred constant?** Yes. The model collapsed to a static, non-varying tensor of predictions (effectively 0.0 or the initial bias).
- **Were both constant?** No, only predictions were constant.
- **Was either nearly constant?** The model predictions were identically constant across the batch/epoch, causing `scipy.stats.spearmanr` to detect zero variance in the `y_pred` array, thereby throwing `ConstantInputWarning`.

===========================================================
## SECTION 6 — WHY IS IC = 0?
===========================================================
- **Explanation**: The Information Coefficient (IC) is calculated using Spearman rank correlation. The formula involves the covariance of the ranked variables divided by the product of their standard deviations. 
- **Cause**: Because `y_pred` is a constant array, its standard deviation is exactly 0. This results in a division by zero error mathematically. `scipy.stats.spearmanr` catches this, issues a `ConstantInputWarning`, and returns `NaN`. The evaluation pipeline in `metrics_registry.py` safely guards against `NaN` by coercing it to `0.0`.
- **Root Cause**: Model predictions (model collapse).

===========================================================
## SECTION 7 — WHY IS R² = 0?
===========================================================
- **Inputs**: `y_true` (raw unscaled returns), `y_pred` (constant predictions near 0).
- **Formula**: `R² = 1 - (MSE / Variance(y_true))`.
- **Output**: 0.0.
- **Explanation**: When a regression model collapses, it defaults to predicting a constant value. The best constant value to minimize MSE is the mean of `y_true`. Since the mean of raw stock returns is extremely close to 0, the model predicting ~0 results in an MSE that perfectly matches the intrinsic variance of `y_true`. Thus, `MSE ≈ Variance(y_true)`, making `1 - 1 = 0`. This is mathematically expected for a collapsed model.

===========================================================
## SECTION 8 — RMSE VS R² CONSISTENCY CHECK
===========================================================
- **Determination**: YES, these values can and do simultaneously occur.
- **Mathematical Explanation**: RMSE and MAE are absolute metrics measured in the units of the target variable. Since the target variable (`return_5d`) is unscaled log-returns, typical values range between -0.05 and 0.05. A model predicting exactly `0.0` for all instances will yield an RMSE and MAE of roughly ~0.01 to ~0.02 (which appears as "≈ 0" at a glance). However, because the model is predicting a constant, it captures absolutely zero variance of the target, resulting in an R² of exactly 0.0 and an undefined IC. The metrics are perfectly internally consistent.

===========================================================
## SECTION 9 — PREDICTION DISTRIBUTION
===========================================================
- **Prediction minimum**: ≈ 0.000
- **Prediction maximum**: ≈ 0.000
- **Prediction mean**: ≈ 0.000
- **Prediction standard deviation**: 0.000
- **Target minimum**: ~ -0.300
- **Target maximum**: ~ +0.300
- **Target mean**: ≈ 0.000
- **Target standard deviation**: ≈ 0.015
- **Conclusion**: The predictions collapsed entirely to a constant value near zero. They completely failed to model the target distribution.

===========================================================
## SECTION 10 — MODEL OUTPUT ANALYSIS
===========================================================
- **Model output tensor shape**: `[Batch, 1]`
- **Loss input**: The pipeline correctly reshapes logits via `logits.view_as(y_batch)` in `_train_epoch`, making the input `[Batch]`. 
- **Metric input**: Correctly squeezed to `[Batch]` in `MetricsRegistry`.
- **Prediction exported to PostProcessingDispatcher**: Passed seamlessly as `[N]` arrays.
- **Prediction written into reports**: Correctly serialized.
- **Verification**: The tensor contract `[N]` is respected. The failure is not dimensional; it is numeric.

===========================================================
## SECTION 11 — REGISTRY ANALYSIS
===========================================================
- **Investigation**: `RegistryManager.register_candidate()` checks `source_artifacts` against `registry_config.REQUIRED_ARTIFACTS`.
- **Required Artifacts**: `model_file`, `feature_scaler.pkl`, `calibrator.pkl`.
- **Exported Artifacts Map** (from `TrainingOrchestrator`): 
  - `model.pt` -> `model.pt`
  - `scaler.pkl` -> `scaler.pkl` (Hardcoded string!)
  - `label_encoder.pkl` -> `label_encoder.pkl`
- **Determination**: This is an orchestration issue / registry contract mismatch. `TrainingOrchestrator` hardcodes the key `"scaler.pkl"` when mapping artifacts for export, while `RegistryManager` rigidly enforces `"feature_scaler.pkl"` based on `registry_config`. Because `"feature_scaler.pkl"` is missing from the dictionary keys provided to the registry, it legitimately throws a `MissingArtifactError`.

===========================================================
## SECTION 12 — PRODUCTION READINESS
===========================================================
- **Dataset**: PASS
- **Tensor Builder**: WARNING (Targets are unscaled)
- **Training Loop**: WARNING (Susceptible to scale collapse)
- **Checkpointing**: PASS
- **Metrics**: PASS
- **Dispatcher**: PASS
- **Calibration**: PASS
- **Inference**: PASS
- **Registry**: PASS (Enforces contract correctly)
- **Artifact Export**: FAIL (Violates registry contract)
- **Experiment Tracking**: PASS

===========================================================
## SECTION 13 — ROOT CAUSE SUMMARY
===========================================================
1. **Model Collapse (IC=0, R²=0)**:
   - *Evidence*: `ConstantInputWarning`, Validation Loss plateauing at Epoch 0.
   - *Affected files*: `ml_engine/data/tensors/builder.py`, `ml_engine/training/training_pipeline.py`.
   - *Runtime impact*: Model learns nothing and predicts a constant value.
   - *Severity*: CRITICAL.
2. **Registry MissingArtifactError**:
   - *Evidence*: Registry rejection stacktrace, `TrainingOrchestrator` dictionary mapping.
   - *Affected files*: `ml_engine/training/training_pipeline.py` (specifically `_register()` method).
   - *Runtime impact*: Successfully trained models cannot be promoted to the registry.
   - *Severity*: CRITICAL.

===========================================================
## SECTION 14 — IMPLEMENTATION RECOMMENDATIONS
===========================================================
- **Recommendation 1**: Fix the Registry Contract Mismatch. 
  - *Implementation*: Update `TrainingOrchestrator._register()` and `_export_artifacts()` to save and reference the scaler file as `"feature_scaler.pkl"`.
  - *Files likely affected*: `ml_engine/training/training_pipeline.py`.
  - *Risk*: Low.
  - *Complexity*: Low.
  - *Testing required*: Verify `RegistryManager` successfully accepts candidate bundle.
- **Recommendation 2**: Scale Regression Targets.
  - *Implementation*: Implement a Target Scaler in `TensorBuilder` (e.g. `StandardScaler` for targets) and inverse-transform predictions during post-processing or inference, so the neural network operates on well-conditioned gradients.
  - *Files likely affected*: `ml_engine/data/tensors/builder.py`, PostProcessing components.
  - *Risk*: High (touches core tensor generation and post-processing).
  - *Complexity*: Medium.
  - *Testing required*: End-to-end training and inference regression tests.
