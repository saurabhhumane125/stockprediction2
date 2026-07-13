from typing import Dict, Any, List

class PipelineConfig:
    """
    Configuration properties strictly for the Pipeline Runner.
    """
    
    # Chronological definitions of exact module stage execution strings
    STAGE_DOWNLOAD: str = "download"
    STAGE_VALIDATE: str = "validate"
    STAGE_CLEAN: str = "clean"
    STAGE_DATASET: str = "dataset"
    STAGE_SEQUENCE: str = "sequence"
    STAGE_TRAIN: str = "train"
    STAGE_EVALUATE: str = "evaluate"
    STAGE_CALIBRATE: str = "calibrate"
    STAGE_REGISTER: str = "register"
    STAGE_INFERENCE_TEST: str = "inference_test"

    @property
    def DEFAULT_STAGES(self) -> List[str]:
        return [
            self.STAGE_DOWNLOAD,
            self.STAGE_VALIDATE,
            self.STAGE_CLEAN,
            self.STAGE_DATASET,
            self.STAGE_SEQUENCE,
            self.STAGE_TRAIN,
            self.STAGE_EVALUATE,
            self.STAGE_CALIBRATE,
            self.STAGE_REGISTER,
            self.STAGE_INFERENCE_TEST
        ]
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }

pipeline_config = PipelineConfig()
