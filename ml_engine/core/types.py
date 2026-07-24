from enum import Enum

class TaskType(str, Enum):
    """
    Production Task Types for the ML Framework.
    Strongly typed to prevent hardcoded strings downstream.
    """
    BINARY_CLASSIFICATION = "BINARY_CLASSIFICATION"
    MULTICLASS_CLASSIFICATION = "MULTICLASS_CLASSIFICATION"
    REGRESSION = "REGRESSION"
    MULTI_OUTPUT_REGRESSION = "MULTI_OUTPUT_REGRESSION"
