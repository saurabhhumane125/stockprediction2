from typing import Dict, Any

class AutomationConfig:
    """
    Configuration properties strictly for the Automation Layer.
    """
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: int = 2  # Exponential backoff multiplier
    
    # Standard predefined automation jobs
    JOB_DAILY_RETRAINING: str = "daily_retraining"
    JOB_EVALUATION_CHECK: str = "evaluation_check"
    JOB_HEALTH_CHECK: str = "health_check"

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }

automation_config = AutomationConfig()
