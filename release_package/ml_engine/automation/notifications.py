import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BaseNotifier(ABC):
    """Abstract interface for Automation notifications."""
    
    @abstractmethod
    def notify_success(self, job_name: str, payload: Dict[str, Any]):
        pass
        
    @abstractmethod
    def notify_failure(self, job_name: str, error: str, payload: Dict[str, Any]):
        pass

class ConsoleNotifier(BaseNotifier):
    """Default implementation routing notifications directly to standard logging securely."""
    
    def notify_success(self, job_name: str, payload: Dict[str, Any]):
        logger.info(f"[AUTOMATION SUCCESS] Job '{job_name}' completed cleanly. Payload: {payload}")
        
    def notify_failure(self, job_name: str, error: str, payload: Dict[str, Any]):
        logger.error(f"[AUTOMATION FAILURE] Job '{job_name}' permanently failed! Error: {error} | Payload: {payload}")
