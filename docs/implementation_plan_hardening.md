# Implementation Plan - Production Training Pipeline Hardening

This plan addresses ONLY the verified production blockers required to run the first CORE/v2.0 GPU baseline training. No unrelated refactoring or redesign is included.

---

## Section 1: Implementation Summary
This implementation will surgically modify the Colab YAML configuration, update the Registry schema from legacy Keras to PyTorch standards, wire the tracking callbacks into the PyTorch training loop, and propagate CLI overrides to the configuration object.

---

## Section 2: Blocker 1 Plan (Colab Default Dataset)
**Files to Modify:**
- `ml_engine/config/colab.yaml`

**Exact Functions/Classes to Change:**
- N/A (YAML configuration)

**Why Change is Required:**
The configuration is hardcoded to `CORE/v1.0`. The baseline run must use the expanded `CORE/v2.0` dataset.

**Why it does NOT alter architecture:**
Updating configuration properties is exactly how the configuration-driven architecture was intended to be used.

**Dependencies:** None.

**Validation Steps:**
- Check that running `prepare_colab.py --validate CORE/v2.0` successfully aligns with the YAML config.

**Risks:** Low.

---

## Section 3: Blocker 2 Plan (Registry Legacy Keys)
**Files to Modify:**
- `ml_engine/config/registry_config.py`
- `ml_engine/registry/manager.py`
- `ml_engine/training/training_pipeline.py`
- `ml_engine/training/runner.py`

**Exact Functions/Classes to Change:**
- `RegistryConfig.REQUIRED_ARTIFACTS` (`registry_config.py`)
- `RegistryManager.get_active_model()` (`manager.py`)
- `TrainingOrchestrator._register()` (`training_pipeline.py`)
- `ProductionTrainingRunner._export_and_register()` (`runner.py`)

**Why Change is Required:**
The production backend will crash if it tries to load `best_model.keras` for inference on a PyTorch model. We must enforce PyTorch native artifact naming (`model.pt`) directly in the registry schema.

**Why it does NOT alter architecture:**
It implements the existing architectural contract (Model Registry validates manifests) but corrects the underlying values from legacy to the new PyTorch standard.

**Dependencies:** None.

**Validation Steps:**
- Dry-run the pipeline and verify the `manifest.json` expects `model.pt`.
- Call `get_active_model()` and verify `"model_path"` points to `model.pt`.

**Risks:** Medium. Old `CORE/v1.0` Keras models in the registry (if any exist) will no longer pass manifest validation for promotion.

---

## Section 4: Blocker 3 Plan (Experiment Tracking Callback)
**Files to Modify:**
- `ml_engine/training/training_pipeline.py`
- `ml_engine/training/runner.py`

**Exact Functions/Classes to Change:**
- `TrainingOrchestrator.__init__()` and `TrainingOrchestrator.run()` (`training_pipeline.py`)
- `ProductionTrainingRunner.run()` (`runner.py`)

**Why Change is Required:**
The `ExperimentTrackingCallback` is instantiated but never fed per-epoch metrics because `TrainingOrchestrator` does not invoke it. The run must log per-epoch learning curves into the SQLite database.

**Why it does NOT alter architecture:**
The architecture already defines `TrainingCallback` and `ExperimentTrackingCallback`. We are simply calling its hooks inside the existing PyTorch training loop where they belong.

**Dependencies:** None.

**Validation Steps:**
- Dry-run the pipeline and verify the SQLite `tracking.db` contains records for each epoch.

**Risks:** Low.

---

## Section 5: Blocker 4 Plan (CLI Runtime Overrides)
**Files to Modify:**
- `ml_engine/scripts/train_models.py`
- `ml_engine/training/runner.py`

**Exact Functions/Classes to Change:**
- `main()` (`train_models.py`)
- `ProductionTrainingRunner.__init__()` (`runner.py`)

**Why Change is Required:**
The pipeline drops CLI arguments because they are not passed from `train_models.py` into `runner.py`, and `runner.py` never overrides `training_config.py`. 

**Why it does NOT alter architecture:**
CLI overrides are standard behavior and do not change the core architecture. It uses the `argparse` values already defined.

**Dependencies:** None.

**Validation Steps:**
- Run `python -m ml_engine.scripts.train_models --dataset CORE/v2.0 --experiment dev --epochs 2 --dry-run` and verify `runner.cfg.EPOCHS == 2`.

**Risks:** Low.

---

## Section 6: Files To Modify
1. `ml_engine/config/colab.yaml`
2. `ml_engine/config/registry_config.py`
3. `ml_engine/registry/manager.py`
4. `ml_engine/training/training_pipeline.py`
5. `ml_engine/training/runner.py`
6. `ml_engine/scripts/train_models.py`

---

## Section 7: Validation Plan
1. Ensure all test scripts compile and pass linting.
2. Execute a dry-run of the pipeline (`train_models.py --dry-run`).
3. Verify that `manifest.json` correctly requires `model.pt`.
4. Check that `tracking.db` logged dry-run metrics.

---

## Section 8: Implementation Risk
The primary risk involves the registry schemas. Any existing Keras models physically sitting in the `ml_engine/model_registry/` folders might fail promotion because `REQUIRED_ARTIFACTS` will now enforce `model.pt`. Since the objective is a fresh PyTorch GPU training run, this is acceptable.

---

## Section 9: Expected Result
The pipeline will cleanly ingest CLI overrides, execute the PyTorch training loop, log per-epoch telemetry correctly via callbacks, export PyTorch native artifacts, and successfully validate/register the artifact under `.pt` keys, fully preparing the repository for the Colab GPU execution.
