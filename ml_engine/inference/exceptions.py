class InferenceError(Exception):
    """Base exception for all Inference Engine errors."""
    pass

class InferenceInputError(InferenceError):
    """Raised when input features are malformed, missing, or unsupported."""
    pass

class RegistryResolutionError(InferenceError):
    """Raised when the active model pointer cannot be resolved or is corrupted."""
    pass

class CalibrationError(InferenceError):
    """Raised when the calibration pipeline fails to execute."""
    pass
