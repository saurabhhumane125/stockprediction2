class RegistryError(Exception):
    """Base exception for all Model Registry errors."""
    pass

class InvalidStateTransitionError(RegistryError):
    """Raised when an illegal promotion or demotion is attempted."""
    pass

class HashMismatchError(RegistryError):
    """Raised when cryptographic hashes of artifacts do not match the manifest."""
    pass

class MissingArtifactError(RegistryError):
    """Raised when a required artifact is missing during registration or promotion."""
    pass

class VersionConflictError(RegistryError):
    """Raised when attempting to register a model version that already exists."""
    pass
