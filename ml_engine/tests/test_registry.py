import os
import json
import tempfile
import pytest

from ml_engine.registry.manager import RegistryManager
from ml_engine.registry.exceptions import (
    InvalidStateTransitionError,
    HashMismatchError,
    MissingArtifactError,
    VersionConflictError
)
from ml_engine.config.registry_config import registry_config


@pytest.fixture
def mock_registry_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "registry")
        manager = RegistryManager(registry_base_path=registry_path)
        
        # Create mock source artifacts
        source_dir = os.path.join(tmpdir, "source")
        os.makedirs(source_dir)
        
        source_artifacts = {}
        for req in registry_config.REQUIRED_ARTIFACTS:
            file_path = os.path.join(source_dir, req)
            with open(file_path, "w") as f:
                f.write(f"dummy data for {req}")
            source_artifacts[req] = file_path
            
        yield manager, registry_path, source_artifacts


def test_registry_registration(mock_registry_env):
    manager, registry_path, source_artifacts = mock_registry_env
    
    version = "v1"
    manifest = manager.register_candidate(version, source_artifacts)
    
    # Assert manifest returns properly
    assert manifest["model_version"] == version
    assert len(manifest["artifacts"]) == len(registry_config.REQUIRED_ARTIFACTS)
    
    # Assert physically copied to candidate
    candidate_dir = os.path.join(registry_path, registry_config.STATE_CANDIDATE, version)
    assert os.path.exists(candidate_dir)
    assert os.path.exists(os.path.join(candidate_dir, "manifest.json"))
    
    # Assert Duplicate Conflict
    with pytest.raises(VersionConflictError):
        manager.register_candidate(version, source_artifacts)


def test_registry_promotion(mock_registry_env):
    manager, registry_path, source_artifacts = mock_registry_env
    version = "v2"
    
    manager.register_candidate(version, source_artifacts)
    manager.promote_model(version, registry_config.STATE_CANDIDATE, registry_config.STATE_STAGING)
    
    # Verify moved from candidate to staging
    assert not os.path.exists(os.path.join(registry_path, registry_config.STATE_CANDIDATE, version))
    assert os.path.exists(os.path.join(registry_path, registry_config.STATE_STAGING, version))
    
    # Promote to production
    manager.promote_model(version, registry_config.STATE_STAGING, registry_config.STATE_PRODUCTION)
    
    # Verify Active pointer
    active_model = manager.get_active_model()
    assert active_model["version"] == version
    assert "best_model.keras" in active_model["model_path"]


def test_hash_mismatch_validation(mock_registry_env):
    manager, registry_path, source_artifacts = mock_registry_env
    version = "v3"
    
    manager.register_candidate(version, source_artifacts)
    
    # Intentionally corrupt the artifact in candidate folder
    candidate_model_path = os.path.join(
        registry_path, registry_config.STATE_CANDIDATE, version, registry_config.REQUIRED_ARTIFACTS[0]
    )
    with open(candidate_model_path, "w") as f:
        f.write("corrupted data")
        
    # Attempt promotion
    with pytest.raises(HashMismatchError):
        manager.promote_model(version, registry_config.STATE_CANDIDATE, registry_config.STATE_STAGING)


def test_rollback_production(mock_registry_env):
    manager, registry_path, source_artifacts = mock_registry_env
    
    # Register and Promote v1
    manager.register_candidate("v1", source_artifacts)
    manager.promote_model("v1", registry_config.STATE_CANDIDATE, registry_config.STATE_PRODUCTION)
    
    # Create v2 artifacts (dummy content change so hash is different if we care, but same is fine for this test)
    manager.register_candidate("v2", source_artifacts)
    manager.promote_model("v2", registry_config.STATE_CANDIDATE, registry_config.STATE_PRODUCTION)
    
    assert manager.get_active_model()["version"] == "v2"
    
    # Rollback
    manager.rollback_production()
    
    # Verify active is v1 again
    assert manager.get_active_model()["version"] == "v1"
    
    # Verify v2 is in rolled_back
    assert os.path.exists(os.path.join(registry_path, registry_config.STATE_ROLLED_BACK, "v2"))


def test_invalid_state_transitions(mock_registry_env):
    manager, registry_path, source_artifacts = mock_registry_env
    
    manager.register_candidate("v1", source_artifacts)
    
    # Attempt promotion to non-existent state
    with pytest.raises(InvalidStateTransitionError):
        manager.promote_model("v1", registry_config.STATE_CANDIDATE, "invalid_state")
        
    # Attempt promotion from non-existent state
    with pytest.raises(InvalidStateTransitionError):
        manager.promote_model("v1", "invalid_state", registry_config.STATE_PRODUCTION)
