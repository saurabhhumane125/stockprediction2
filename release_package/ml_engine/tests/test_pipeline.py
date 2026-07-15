import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from ml_engine.pipeline.runner import PipelineRunner
from ml_engine.config.pipeline_config import pipeline_config
from ml_engine.pipeline.exceptions import PipelineExecutionError


@pytest.fixture
def mock_pipeline_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = PipelineRunner(base_dir=tmpdir, ticker="MOCK_TICKER")
        yield runner, tmpdir


@patch("ml_engine.pipeline.runner.YFinanceDownloader")
@patch("ml_engine.pipeline.runner.ProductionDataValidator")
@patch("ml_engine.pipeline.runner.ProductionCleaner")
@patch("ml_engine.pipeline.runner.FeatureGenerator")
@patch("ml_engine.pipeline.runner.DatasetBuilder")
@patch("ml_engine.pipeline.runner.SequenceBuilder")
@patch("ml_engine.pipeline.runner.KerasTrainer")
@patch("ml_engine.pipeline.runner.ProductionEvaluator")
@patch("ml_engine.pipeline.runner.ProductionCalibrator")
@patch("ml_engine.registry.manager.RegistryManager.register_candidate")
@patch("ml_engine.registry.manager.RegistryManager.promote_model")
@patch("ml_engine.pipeline.runner.ProductionInferenceEngine")
def test_full_pipeline_execution(
    mock_inference, mock_promote, mock_register,
    mock_calibrator, mock_evaluator, mock_trainer, mock_seq_builder,
    mock_builder, mock_feat, mock_cleaner, mock_val, mock_download,
    mock_pipeline_env
):
    runner, tmpdir = mock_pipeline_env
    
    mock_builder_instance = mock_builder.return_value
    mock_builder_instance.build.return_value = {"dataset_version": "v1"}
    
    mock_seq_instance = mock_seq_builder.return_value
    mock_seq_instance.build_sequences.return_value = {"seq": "meta"}
    
    with patch.object(runner.tabular_storage, "load_dataframe", return_value=MagicMock()):
        with patch.object(runner.tabular_storage, "save_dataframe"):
            # Execute full pipeline
            result = runner.run()
    assert result is True
    
    # Check that it saves the summary
    summary_path = os.path.join(tmpdir, "pipeline_summary.json")
    assert os.path.exists(summary_path)
    with open(summary_path, "r") as f:
        summary = json.load(f)
        
    assert summary["status"] == "completed"
    assert len(summary["stages"]) == len(pipeline_config.DEFAULT_STAGES)
    assert summary["stages"][0]["stage"] == pipeline_config.STAGE_DOWNLOAD


@patch("ml_engine.pipeline.runner.YFinanceDownloader")
def test_pipeline_failure_recovery(mock_download, mock_pipeline_env):
    runner, tmpdir = mock_pipeline_env
    
    # Force failure on download
    mock_download_instance = mock_download.return_value
    mock_download_instance.download.side_effect = Exception("Mock Download Failed")
    
    with pytest.raises(PipelineExecutionError):
        runner.run([pipeline_config.STAGE_DOWNLOAD, pipeline_config.STAGE_VALIDATE])
        
    # Verify it logged failure
    summary_path = os.path.join(tmpdir, "pipeline_summary.json")
    with open(summary_path, "r") as f:
        summary = json.load(f)
        
    assert summary["status"] == "failed"
    assert summary["stages"][-1]["status"] == "failed"


@patch("ml_engine.pipeline.runner.ProductionCleaner")
def test_resume_from_stage(mock_cleaner, mock_pipeline_env):
    runner, tmpdir = mock_pipeline_env
    
    # Run a pipeline but start from Clean, skipping download/validate
    # Note: normally context might be empty, but we just verify it starts exactly there.
    
    mock_cleaner_instance = mock_cleaner.return_value
    mock_cleaner_instance.clean.return_value = MagicMock()
    
    runner.context["raw_data_path"] = "dummy.parquet"
    
    with patch.object(runner, "_execute_stage") as mock_exec:
        runner.run(stages=None, resume_from=pipeline_config.STAGE_CLEAN)
        # Verify that it executed from CLEAN onwards
        executed_stages = [call[0][0] for call in mock_exec.call_args_list]
        expected_stages = pipeline_config.DEFAULT_STAGES[pipeline_config.DEFAULT_STAGES.index(pipeline_config.STAGE_CLEAN):]
        assert executed_stages == expected_stages
            
    summary_path = os.path.join(tmpdir, "pipeline_summary.json")
    with open(summary_path, "r") as f:
        summary = json.load(f)
        
    # Stages should start from Clean -> end
    assert summary["stages"][0]["stage"] == pipeline_config.STAGE_CLEAN
    assert len(summary["stages"]) == len(pipeline_config.DEFAULT_STAGES) - pipeline_config.DEFAULT_STAGES.index(pipeline_config.STAGE_CLEAN)


def test_invalid_resume_stage(mock_pipeline_env):
    runner, tmpdir = mock_pipeline_env
    
    with pytest.raises(PipelineExecutionError, match="not in pipeline"):
        runner.run(resume_from="invalid_stage_name")
