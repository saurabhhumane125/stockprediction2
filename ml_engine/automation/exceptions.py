class AutomationError(Exception):
    """Base exception for all Automation Layer errors."""
    pass

class JobExecutionError(AutomationError):
    """Raised when an automation job completely fails after max retries."""
    pass

class SchedulerError(AutomationError):
    """Raised when an invalid job payload is passed to the manager."""
    pass
