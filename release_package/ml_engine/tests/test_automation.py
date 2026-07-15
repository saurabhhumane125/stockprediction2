import pytest
from unittest.mock import patch, MagicMock

from ml_engine.automation.manager import AutomationManager
from ml_engine.config.automation_config import automation_config
from ml_engine.automation.exceptions import JobExecutionError
from ml_engine.pipeline.exceptions import PipelineExecutionError

@pytest.fixture
def mock_manager():
    # Setup mock notifier and manager
    mock_notifier = MagicMock()
    manager = AutomationManager(base_dir="test_dir", notifier=mock_notifier)
    return manager, mock_notifier

@patch("ml_engine.automation.manager.PipelineRunner")
@patch("time.sleep")
def test_successful_job_execution(mock_sleep, mock_runner_class, mock_manager):
    manager, mock_notifier = mock_manager
    
    mock_runner = mock_runner_class.return_value
    mock_runner.run.return_value = True
    mock_runner.summary = {"test": "success"}
    
    result = manager.execute_job("test_job", "TEST_TICKER")
    
    assert result is True
    assert mock_runner.run.call_count == 1
    mock_notifier.notify_success.assert_called_once()
    mock_notifier.notify_failure.assert_not_called()

@patch("ml_engine.automation.manager.PipelineRunner")
@patch("time.sleep")
def test_job_retry_on_failure_and_resume(mock_sleep, mock_runner_class, mock_manager):
    manager, mock_notifier = mock_manager
    
    mock_runner = mock_runner_class.return_value
    
    # First call raises an error from validate stage, Second call succeeds
    mock_runner.run.side_effect = [
        PipelineExecutionError("Stage 'validate' failed: Mock Error"),
        True
    ]
    mock_runner.summary = {"status": "completed"}
    
    result = manager.execute_job("test_job", "TEST_TICKER")
    
    assert result is True
    assert mock_runner.run.call_count == 2
    
    # Verify the first call was without resume_from
    call_1_kwargs = mock_runner.run.call_args_list[0][1]
    assert call_1_kwargs["resume_from"] is None
    
    # Verify the second call automatically injected 'validate' as the resume point
    call_2_kwargs = mock_runner.run.call_args_list[1][1]
    assert call_2_kwargs["resume_from"] == "validate"
    
    # Verify sleep was called for the backoff
    mock_sleep.assert_called_once()
    mock_notifier.notify_success.assert_called_once()

@patch("ml_engine.automation.manager.PipelineRunner")
@patch("time.sleep")
def test_job_max_retries_exceeded(mock_sleep, mock_runner_class, mock_manager):
    manager, mock_notifier = mock_manager
    mock_runner = mock_runner_class.return_value
    
    # Hard crash every time
    mock_runner.run.side_effect = PipelineExecutionError("Stage 'train' failed: Bad Loss")
    
    with pytest.raises(JobExecutionError) as excinfo:
        manager.execute_job("test_job", "TEST_TICKER")
        
    assert "failed completely after 3 attempts" in str(excinfo.value)
    
    assert mock_runner.run.call_count == automation_config.MAX_RETRIES
    mock_notifier.notify_failure.assert_called_once()
    mock_notifier.notify_success.assert_not_called()
