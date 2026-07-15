from typing import Dict, Any, List

class RegistryConfig:
    """
    Configuration properties strictly for the Model Registry.
    """
    
    # Supported Environments/States
    STATE_CANDIDATE: str = "candidate"
    STATE_STAGING: str = "staging"
    STATE_PRODUCTION: str = "production"
    STATE_ARCHIVED: str = "archived"
    STATE_DEPRECATED: str = "deprecated"
    STATE_ROLLED_BACK: str = "rolled_back"
    
    @property
    def VALID_STATES(self) -> List[str]:
        return [
            self.STATE_CANDIDATE,
            self.STATE_STAGING,
            self.STATE_PRODUCTION,
            self.STATE_ARCHIVED,
            self.STATE_DEPRECATED,
            self.STATE_ROLLED_BACK
        ]
        
    @property
    def REQUIRED_ARTIFACTS(self) -> List[str]:
        return [
            "best_model.keras",
            "feature_scaler.pkl",
            "calibrator.pkl",
            "evaluation_report.json",
            "calibration_report.json"
        ]
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }

registry_config = RegistryConfig()
