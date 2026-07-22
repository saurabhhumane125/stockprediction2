# TRAINING PIPELINE VERIFICATION REPORT v1.0

## 1. FILES INSPECTED
The following core training pipeline files were analyzed:
- `ml_engine/training/runner.py`
- `ml_engine/training/training_pipeline.py`
- `ml_engine/models/model_factory.py`
- `ml_engine/scripts/train_models.py`
- `ml_engine/training/callbacks.py`
- `ml_engine/config/training_config.py`
- `ml_engine/config/registry_config.py`

---

## 2. VERIFIED ARCHITECTURE
The verified execution flow is currently implemented as follows:
**CLI (`train_models.py`)**
  ↓
**`ProductionTrainingRunner`** (Initializes the Tracker, ModelFactory)
  ↓
**`TrainingOrchestrator`** (Executes PyTorch Training Loop, AMP, Early Stopping, Evaluation, Calibration)
  ↓
**`RegistryManager`** (Registers the resulting manifest and artifacts)
  ↓
**Artifacts** (`model.pt`, `scaler.pkl`, `calibrator.pkl`, `metadata.json`)

---

## 3. VERIFIED STRENGTHS
The following implementations strictly match the approved project architecture:
- **Reproducibility:** Seed everything is enforced prior to training.
- **Factory Pattern:** `model_factory.py` correctly uses `@ModelFactory.register("gru")`, eliminating `if/else` chains.
- **Mixed Precision:** Handled perfectly using PyTorch `GradScaler`.
- **Checkpointing:** `CheckpointManager` monitors validation loss and correctly restores the best weights.
- **Calibration:** Isotonic regression is seamlessly fitted on the validation set post-training.

---

## 4. VERIFIED PRODUCTION ISSUES

### Issue 1: CLI Overrides Ignored
- **File:** `ml_engine/scripts/train_models.py`
- **Function:** `main()`
- **Evidence:** Arguments like `--epochs`, `--batch-size`, and `--device` are parsed by `argparse` but are NEVER passed to `ProductionTrainingRunner` or applied to the config.
- **Why it violates architecture:** The CLI exists to allow orchestration flexibility (essential for HPO). Silently dropping arguments violates the strict, explicit execution rule.
- **Severity:** High
- **Implementation Required:** Fix immediately.

### Issue 2: Missing Callback Invocations (Epoch Metrics Lost)
- **File:** `ml_engine/training/runner.py` & `ml_engine/training/training_pipeline.py`
- **Function:** `run()`
- **Evidence:** `runner.py` initializes `ExperimentTrackingCallback` and triggers `on_train_begin` / `on_train_end`. However, `TrainingOrchestrator` is not provided with the callbacks. Therefore, `on_epoch_begin`, `on_epoch_end`, and `on_early_stopping` are NEVER invoked during the PyTorch loop.
- **Why it violates architecture:** Experiment tracking (SQLite) will permanently lose learning curve histories and per-epoch metrics. 
- **Severity:** High
- **Implementation Required:** Fix immediately.

### Issue 3: Misleading Legacy Artifact Keys
- **File:** `ml_engine/config/registry_config.py` & `ml_engine/training/training_pipeline.py`
- **Function:** `_register()`
- **Evidence:** `RegistryConfig.REQUIRED_ARTIFACTS` demands `best_model.keras`. The orchestrator maps the PyTorch `model.pt` to the key `best_model.keras` to bypass validation.
- **Why it violates architecture:** Pollutes the registry and manifest with legacy metadata that does not reflect the current PyTorch architecture.
- **Severity:** Medium
- **Implementation Required:** Fix immediately.

### Issue 4: In-Memory Tensor Loading Bottleneck
- **File:** `ml_engine/training/training_pipeline.py`
- **Function:** `_load_tensors()`
- **Evidence:** The dataloader reads the entire `.pt` sequence file into CPU memory using `torch.load` before converting to `.numpy()`. 
- **Why it violates architecture:** This will result in an Out-Of-Memory (OOM) crash when transitioning to the Intraday 3GB+ `CORE/v3.0` dataset.
- **Severity:** Low (currently), High (future).
- **Implementation Required:** Fix later (Before CORE/v3.0 dataset implementation).

---

## 5. UNVERIFIED ITEMS
- **`report_generator.py`**: The internal layout of the markdown metrics report was not heavily audited.
- **`ml_engine/optimization/`**: Hyperparameter optimization modules remain unverified at this phase.

---

## 6. REPOSITORY VS DOCUMENTATION
- **Training Pipeline & Runner:** Partially Verified (Issues 2 & 3 disrupt exact architectural adherence).
- **Experiment Tracking:** Partially Verified (Issue 2 blocks per-epoch metrics).
- **CLI implementation:** Partially Verified (Issue 1).
- **Model Registry:** Verified.
- **Colab Bootstrap:** Verified.
- **Datasets:** Verified.

---

## 7. IMPLEMENTATION RECOMMENDATION
- **Issue 1 (CLI Args):** Fix immediately. Ensure CLI kwargs override `training_config` temporarily at runtime.
- **Issue 2 (Callbacks):** Fix immediately. Inject a `callbacks` list into `TrainingOrchestrator`.
- **Issue 3 (Registry Keys):** Fix immediately. Update `registry_config.py` to require `model.pt`.
- **Issue 4 (OOM Loader):** Fix later. Will be addressed via `mmap` or HDF5 when v3.0 is built.

---

## 8. CURRENT READINESS
Is the production training pipeline ready for CORE/v2.0 GPU Training?
**PARTIALLY**
**Evidence:** The core mathematical implementations (PyTorch gradients, AMP, Evaluation) are fully production-ready and technically capable of training the model. However, executing a baseline Colab run now would result in an irreversible loss of epoch tracking telemetry in the SQLite DB and produce misleading registry manifests.

---

## 9. RECOMMENDED NEXT MILESTONE
**Training Pipeline Pre-Flight Hardening**
**Justification:** Before committing to Google Colab GPU execution, the pipeline's CLI overrides, callback wiring, and registry schema must be corrected to guarantee that the baseline metrics are accurately tracked and seamlessly comparable during future Hyperparameter Optimization.
