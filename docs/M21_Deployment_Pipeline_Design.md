# M21 Production Model Deployment Pipeline Design

## 1. Input: Deployment Bundle Zip

The deployment pipeline will start with a single **deployment bundle zip** (e.g., `colab_sync.zip`). 
**Rationale**: In Google Colab, `ArtifactSynchronizer.sync()` already produces a self-contained zip containing the run directory (with the model, scaler, calibrator, and `metadata.json`/`manifest.json`) and the experiment tracker DB. Using a single zip file ensures atomicity during transport from Google Drive to the local production environment, preventing partial file downloads or accidental corruption.

## 2. Validation

Before importing any files into the local registry, the deployment pipeline must extract the zip into a temporary staging directory and execute the following strict validations:

1. **Manifest Existence**: Verify that `manifest.json` (or `metadata.json` depending on export) exists within the bundle.
2. **Artifact Existence**: Verify that all physical files referenced in the manifest (`best_model.keras` / `model.pt`, `feature_scaler.pkl`) exist in the extracted folder.
3. **SHA Verification**: Pre-compute the SHA-256 hash of each extracted artifact and compare it against the hashes declared in the manifest. This guarantees no corruption occurred during the Colab -> Google Drive -> Local transfer.
4. **Version Conflict Detection**: Check if the extracted `version` already exists in ANY state within the local `ml_data/registry`. If it does, the deployment must abort immediately.
5. **Framework Compatibility**: Ensure the `framework` (e.g., `tensorflow` vs `pytorch`) specified in the manifest is supported by the local `ProductionInferenceEngine`.

## 3. Import

Once validation passes, the import process will delegate file movement entirely to the existing `RegistryManager`. 
- The pipeline will NOT manually copy files into the registry folders. 
- Instead, it will call `RegistryManager.register_candidate(version, source_artifacts, metadata, authenticity="REAL")`. 
- The `RegistryManager` will internally handle copying the validated files from the temporary extraction directory into `ml_data/registry/candidate/{version}`, re-hash them for its own records, and write the immutable registry manifest.

## 4. Registry Promotion

The deployment pipeline will orchestrate state transitions via `RegistryManager.promote_model()`.

1. **Candidate State (`ml_data/registry/candidate/`)**
   - **Action**: Model artifacts are ingested safely. 
   - **Purpose**: At this stage, the model is physically in the registry but completely isolated from production. It is ready for staging.
2. **Staging State (`ml_data/registry/staging/`)**
   - **Action**: The deployment script calls `promote_model(version, "candidate", "staging")`.
   - **Purpose**: The bundle is moved. In a fully automated CI/CD pipeline, integration tests or shadow inference would run against the model in this state.
3. **Production State (`ml_data/registry/production/`)**
   - **Action**: The deployment script calls `promote_model(version, "staging", "production")`.
   - **Purpose**: The bundle is moved to the production folder. The `RegistryManager` atomically updates `ml_data/registry/active_production.json` to point `active_version` to this newly deployed model. 

## 5. Rollback

If validation fails, the script simply deletes the temporary extraction directory, leaving the local registry untouched.

If the model is successfully promoted to Production but immediately exhibits fatal errors (e.g., API 500s or severe accuracy degradation), the rollback procedure relies entirely on the existing `RegistryManager.rollback_production()` method:
- **Action**: The system administrator (or an automated health check) triggers a rollback.
- **Execution**: `RegistryManager` reads `active_production.json` to identify the `active_version` and the `previous_version`.
- **Preservation**: It promotes the failing `active_version` from `production` into the `rolled_back` state (preserving it for forensic analysis).
- **Reactivation**: It locates the `previous_version` (which remains safely stored in `production` or is recovered from `archived`) and updates `active_production.json` to restore it as the active pointer.

## 6. Backend Integration

**Immediate Requirement: Backend Restart**
Currently, the FastAPI application loads the active model weights and configuration into memory once during its lifecycle boot (`ProductionInferenceEngine._bootstrap_inference()` called via `artifacts.load_artifacts()` in `lifespan`). Therefore, after a successful promotion to Production, the system administrator **must restart the backend process** (e.g., restart Uvicorn or the Docker container) to force the `MLEngineAdapter` to read the updated `active_production.json` pointer and load the new model into memory.

**Future Enhancement: Hot Reload**
A hot reload capability can be added later without architectural redesign. We can expose an authenticated admin endpoint (e.g., `POST /admin/models/reload`) that safely triggers `ml_adapter.inference_engine._bootstrap_inference()`. This will read the new pointer, hot-swap the model and scaler in memory, and seamlessly serve the new version with zero downtime.
