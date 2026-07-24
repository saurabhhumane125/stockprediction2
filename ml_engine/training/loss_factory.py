import torch.nn as nn
from ml_engine.core.types import TaskType

class LossFactory:
    """
    Production Loss Factory.
    Selects the correct loss function strictly based on the TaskType.
    """

    @staticmethod
    def get_loss(task_type: TaskType) -> nn.Module:
        if task_type == TaskType.BINARY_CLASSIFICATION:
            return nn.BCEWithLogitsLoss()
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
            return nn.CrossEntropyLoss()
        elif task_type in (TaskType.REGRESSION, TaskType.MULTI_OUTPUT_REGRESSION):
            return nn.HuberLoss() # Defaulting to Huber for robust regression
        else:
            raise ValueError(f"Unsupported TaskType for loss generation: {task_type}")
