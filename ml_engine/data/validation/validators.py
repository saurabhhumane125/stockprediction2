import logging
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

from ml_engine.interfaces.base_validator import BaseValidator
from ml_engine.data.validation.reports import ValidationReport
from ml_engine.data.validation.exceptions import (
    DatasetValidationError,
    SchemaValidationError,
    FeatureValidationError,
    TrainingValidationError
)

logger = logging.getLogger(__name__)


class ProductionDataValidator(BaseValidator):
    """
    Production validator that strictly enforces OHLCV constraints, data integrity,
    and schema correctness using pure Pandas to avoid unnecessary external dependencies.
    """

    def __init__(self, dataset_version: str = "v1", pipeline_version: str = "1.0.0"):
        self.dataset_version = dataset_version
        self.pipeline_version = pipeline_version
        
    def _create_report(self) -> ValidationReport:
        return ValidationReport(self.dataset_version, self.pipeline_version)

    def validate(self, df: pd.DataFrame, schema_name: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Main entry point for validation matching the BaseValidator interface.
        """
        logger.info(f"Starting validation for schema: {schema_name}")
        start_time = time.time()
        
        report = self._create_report()
        report.stats["rows_processed"] = len(df)
        
        try:
            if schema_name == "raw_ohlc":
                self._validate_raw_ohlc(df, report)
            elif schema_name == "engineered_features":
                self._validate_features(df, report)
            elif schema_name == "training":
                self._validate_training(df, report)
            else:
                raise SchemaValidationError(f"Unknown schema name: {schema_name}")
                
            error_logs = [log for log in report.logs if log["severity"] in ["ERROR", "CRITICAL"]]
            passed = len(error_logs) == 0
            report.finalize(passed)
            
        except Exception as e:
            logger.error(f"Validation fatally interrupted: {e}")
            report.add_log("CRITICAL", f"Fatal error during validation: {str(e)}")
            report.finalize(False)
            
        duration = time.time() - start_time
        report.stats["duration_seconds"] = round(duration, 4)
        
        logger.info(f"Completed validation ({schema_name}) in {duration:.4f}s. Status: {report.status}")
        return report.status == "PASSED", report.to_dict()

    def _validate_data_integrity(self, df: pd.DataFrame, report: ValidationReport):
        """Checks missing values, duplicates, and empty datasets."""
        if df.empty:
            report.add_log("CRITICAL", "Dataset is empty.")
            raise DatasetValidationError("Empty dataset.")
            
        # Missing values
        missing_count = int(df.isna().sum().sum())
        if missing_count > 0:
            report.stats["missing_values"] = missing_count
            report.add_log("WARNING", f"Dataset contains {missing_count} missing values.")
            
        # Duplicates
        if df.index.has_duplicates:
            dup_count = df.index.duplicated().sum()
            report.stats["duplicate_rows"] = int(dup_count)
            report.add_log("ERROR", f"Dataset has {dup_count} duplicate timestamps.")
            
    def _validate_raw_ohlc(self, df: pd.DataFrame, report: ValidationReport):
        """Strict OHLC schema validation."""
        self._validate_data_integrity(df, report)
        
        expected_cols = ["open", "high", "low", "close", "volume"]
        missing_cols = [c for c in expected_cols if c not in df.columns]
        if missing_cols:
            report.add_log("CRITICAL", f"Missing required columns: {missing_cols}")
            raise SchemaValidationError(f"Missing cols: {missing_cols}")
            
        # OHLC logic violations
        ohlc_violations = 0
        
        # High >= Open, Close, Low
        if not (df["high"] >= df["open"]).all():
            ohlc_violations += int((df["high"] < df["open"]).sum())
        if not (df["high"] >= df["close"]).all():
            ohlc_violations += int((df["high"] < df["close"]).sum())
        if not (df["high"] >= df["low"]).all():
            ohlc_violations += int((df["high"] < df["low"]).sum())
            
        # Low <= Open, Close
        if not (df["low"] <= df["open"]).all():
            ohlc_violations += int((df["low"] > df["open"]).sum())
        if not (df["low"] <= df["close"]).all():
            ohlc_violations += int((df["low"] > df["close"]).sum())
            
        # Strict positivity
        for col in ["open", "high", "low", "close"]:
            if (df[col] <= 0).any():
                ohlc_violations += int((df[col] <= 0).sum())
                report.add_log("ERROR", f"{col} contains values <= 0")
                
        # Volume Validation
        if (df["volume"] < 0).any():
            vol_errs = int((df["volume"] < 0).sum())
            ohlc_violations += vol_errs
            report.add_log("ERROR", f"Found {vol_errs} rows with negative volume.")
            
        # Corporate Actions
        if "stock_splits" in df.columns and (df["stock_splits"] < 0).any():
            report.add_log("ERROR", "Found negative stock splits.")
        if "dividends" in df.columns and (df["dividends"] < 0).any():
            report.add_log("ERROR", "Found negative dividends.")
            
        report.stats["ohlc_violations"] = ohlc_violations
        if ohlc_violations > 0:
            report.add_log("ERROR", f"Found {ohlc_violations} OHLC/Volume logic violations.")
            
    def _validate_features(self, df: pd.DataFrame, report: ValidationReport):
        """Validates that engineered features do not contain infinities or massive anomalies."""
        self._validate_data_integrity(df, report)
        
        # Check for infinities
        inf_count = np.isinf(df.select_dtypes(include=[np.number])).values.sum()
        if inf_count > 0:
            report.add_log("ERROR", f"Engineered features contain {inf_count} infinite values.")
            
        # Check for NaNs
        nan_count = int(df.isna().sum().sum())
        if nan_count > 0:
            report.add_log("ERROR", f"Engineered features contain {nan_count} NaN values. Must be imputed first.")
            
    def _validate_training(self, df: pd.DataFrame, report: ValidationReport):
        """Validates sequence logic and target shapes."""
        self._validate_data_integrity(df, report)
        
        if "target" not in df.columns:
            report.add_log("ERROR", "Missing 'target' column in training dataset.")

            
        # Log balance stats
        if "target" in df.columns:
            report.stats["target_balance"] = df["target"].value_counts(normalize=True).to_dict()
