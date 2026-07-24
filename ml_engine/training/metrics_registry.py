import numpy as np
from typing import Dict, Any, Callable
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, mean_squared_error, mean_absolute_error, r2_score
from ml_engine.core.types import TaskType
from scipy.stats import spearmanr

class MetricsRegistry:
    """
    Registry pattern for evaluation metrics.
    Avoids long if-else blocks in the training pipeline.
    """
    _registry = {}

    @classmethod
    def register(cls, task_type: TaskType):
        def wrapper(func: Callable):
            cls._registry[task_type] = func
            return func
        return wrapper

    @classmethod
    def evaluate(cls, task_type: TaskType, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
        if task_type not in cls._registry:
            raise ValueError(f"No metric evaluator registered for task: {task_type}")
        return cls._registry[task_type](y_true, y_pred, y_prob)

@MetricsRegistry.register(TaskType.BINARY_CLASSIFICATION)
def evaluate_binary(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    if y_prob is not None:
        try:
            # For binary, AUC needs probabilities of the positive class
            # y_prob might be raw logits (which we should sigmoid before calling roc_auc)
            # or it might be [N, 1] after sigmoid. Assuming it's the class 1 prob.
            metrics["auc"] = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            pass
    return metrics

@MetricsRegistry.register(TaskType.MULTICLASS_CLASSIFICATION)
def evaluate_multiclass(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }
    if y_prob is not None:
        try:
            # Expecting y_prob to be shape [N, C] with probabilities
            metrics["auc"] = float(roc_auc_score(y_true, y_prob, multi_class="ovr"))
        except ValueError:
            pass
    return metrics

@MetricsRegistry.register(TaskType.REGRESSION)
def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
    y_true = y_true.squeeze()
    y_pred = y_pred.squeeze()
    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }
    if len(y_true) > 1:
        corr, _ = spearmanr(y_true, y_pred)
        metrics["ic"] = float(corr) if not np.isnan(corr) else 0.0
    return metrics

@MetricsRegistry.register(TaskType.MULTI_OUTPUT_REGRESSION)
def evaluate_multi_output_regression(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
    # Similar to regression but averaged over outputs
    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }
    return metrics
