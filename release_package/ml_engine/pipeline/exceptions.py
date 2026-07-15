class PipelineError(Exception):
    """Base exception for all Pipeline Runner errors."""
    pass

class PipelineExecutionError(PipelineError):
    """Raised when a specific pipeline stage fails to execute."""
    pass

class StageDependencyError(PipelineError):
    """Raised when a stage requires artifacts from a prior unexecuted stage."""
    pass
