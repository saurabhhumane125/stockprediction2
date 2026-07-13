import time
import logging
from typing import Dict, Any, Optional, List

from ml_engine.config.automation_config import automation_config
from ml_engine.automation.exceptions import JobExecutionError, SchedulerError
from ml_engine.automation.notifications import BaseNotifier, ConsoleNotifier
from ml_engine.pipeline.runner import PipelineRunner
from ml_engine.pipeline.exceptions import PipelineExecutionError

logger = logging.getLogger(__name__)

class AutomationManager:
    """
    Production Automation Engine orchestrating scheduled jobs,
    managing retries, tracking status, and emitting telemetry reliably.
    """
    
    def __init__(self, base_dir: str = "ml_data", notifier: Optional[BaseNotifier] = None):
        self.base_dir = base_dir
        self.notifier = notifier or ConsoleNotifier()
        
    def execute_job(self, job_name: str, ticker: str, stages: Optional[List[str]] = None, resume_from: Optional[str] = None):
        """
        Executes a Pipeline job gracefully wrapped with resilient retry loops natively.
        """
        logger.info(f"AutomationManager triggering job: '{job_name}' for ticker: '{ticker}'")
        
        attempt = 1
        current_resume_stage = resume_from
        last_error = None
        
        while attempt <= automation_config.MAX_RETRIES:
            logger.info(f"--- Job Attempt {attempt}/{automation_config.MAX_RETRIES} ---")
            
            # Reinstantiate Runner to ensure state cleanliness across isolated retries
            runner = PipelineRunner(base_dir=self.base_dir, ticker=ticker)
            
            try:
                # Trigger the pipeline runner dynamically
                success = runner.run(stages=stages, resume_from=current_resume_stage)
                
                if success:
                    # Notify Success
                    payload = {
                        "ticker": ticker,
                        "attempts_used": attempt,
                        "summary": runner.summary
                    }
                    self.notifier.notify_success(job_name, payload)
                    return True
                    
            except PipelineExecutionError as e:
                # Intercept inner pipeline crashes safely
                last_error = str(e)
                logger.warning(f"Attempt {attempt} failed: {last_error}")
                
                # Check if we can extract exactly which stage failed to resume natively.
                # E.g. PipelineExecutionError: Stage 'validate' failed: ...
                if "Stage '" in last_error and "' failed" in last_error:
                    # Parse out the stage name safely:
                    try:
                        failed_stage = last_error.split("Stage '")[1].split("' failed")[0]
                        current_resume_stage = failed_stage
                        logger.info(f"Identified failed stage: '{failed_stage}'. Queuing resume.")
                    except IndexError:
                        pass # Fallback to original resume_from
                
                # Sleep with exponential backoff safely
                if attempt < automation_config.MAX_RETRIES:
                    sleep_time = automation_config.BACKOFF_FACTOR ** attempt
                    logger.info(f"Backing off for {sleep_time} seconds before retrying...")
                    time.sleep(sleep_time)
            except Exception as global_e:
                # Unknown exceptions outside standard Pipeline structural crashes
                last_error = str(global_e)
                logger.error(f"Critical unstructured failure during attempt {attempt}: {global_e}")
                break
                
            attempt += 1

        # We exhausted retries or hit a critical failure
        payload = {
            "ticker": ticker,
            "max_retries_exceeded": True,
            "final_resume_stage": current_resume_stage
        }
        self.notifier.notify_failure(job_name, last_error, payload)
        
        raise JobExecutionError(f"Job '{job_name}' failed completely after {attempt-1} attempts. Last Error: {last_error}")

    def run_daily_retraining(self, ticker: str):
        """Helper to run a full E2E pipeline for daily triggers."""
        self.execute_job(automation_config.JOB_DAILY_RETRAINING, ticker=ticker)
