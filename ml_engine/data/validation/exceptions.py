"""
Custom exceptions for the ML Engine validation layer.
These exceptions are provider-independent and ensure structured error handling
throughout the dataset generation pipeline.
"""


class BaseValidationError(Exception):
    """Base exception for all ML engine validation errors."""
    pass


class DatasetValidationError(BaseValidationError):
    """Raised when a dataset fails integrity checks (e.g., empty, duplicates, missing days)."""
    pass


class SchemaValidationError(BaseValidationError):
    """Raised when a dataframe does not conform to the expected columns or types."""
    pass


class FeatureValidationError(BaseValidationError):
    """Raised when engineered features contain NaNs, infinities, or break constraints."""
    pass


class TrainingValidationError(BaseValidationError):
    """Raised when the final training dataset has invalid shapes, sequences, or extreme imbalance."""
    pass
