import pandas as pd
import numpy as np
from typing import List, Tuple
from ml_engine.core.types import TaskType
from ml_engine.data.tensors.targets.base import BaseTargetStrategy
from ml_engine.data.tensors.targets.registry import StrategyRegistry

class LegacyTargetStrategy(BaseTargetStrategy):
    """
    Legacy Target Strategy.
    Encapsulates the original TargetFactory logic to ensure backward compatibility.
    """
    
    @property
    def strategy_name(self) -> str:
        return "legacy"
        
    @property
    def strategy_version(self) -> str:
        return "1.0"

    def get_target_cols(self, target_config: type) -> List[str]:
        """
        Returns the explicit list of target column names generated for the configuration.
        """
        task_type = getattr(target_config, "task_type", TaskType.BINARY_CLASSIFICATION)
        horizons = getattr(target_config, "horizons", [1])
        primary_h = getattr(target_config, "primary_horizon", horizons[0] if horizons else 1)

        if task_type in (TaskType.BINARY_CLASSIFICATION, TaskType.MULTICLASS_CLASSIFICATION):
            return ["target"]
        elif task_type == TaskType.REGRESSION:
            return [f"return_{primary_h}d"]
        elif task_type == TaskType.MULTI_OUTPUT_REGRESSION:
            return [f"return_{h}d" for h in horizons]
        else:
            return ["target"]

    def generate(self, df: pd.DataFrame, target_config: type) -> Tuple[pd.DataFrame, List[str]]:
        """
        Applies the configured target logic to the DataFrame and returns (df, target_cols).
        """
        df = df.copy()
        horizons = getattr(target_config, "horizons", [1])
        primary_h = getattr(target_config, "primary_horizon", horizons[0] if horizons else 1)
        task_type = getattr(target_config, "task_type", TaskType.BINARY_CLASSIFICATION)
        target_type = getattr(target_config, "target_type", "CLASS")
        thresholds = getattr(target_config, "thresholds", [0.0])
        
        target_cols = self.get_target_cols(target_config)

        # Calculate base future returns for active horizons needed by the target logic
        active_horizons = horizons if task_type == TaskType.MULTI_OUTPUT_REGRESSION else [primary_h]
        return_cols = []
        for h in active_horizons:
            col_name = f"return_{h}d"
            if target_type == "LOG_RETURN":
                df[col_name] = np.log(df["close"].shift(-h) / df["close"])
            elif target_type == "PRICE":
                df[col_name] = df["close"].shift(-h)
            else: # RETURN or CLASS base
                df[col_name] = (df["close"].shift(-h) - df["close"]) / df["close"]
            return_cols.append(col_name)

        # Drop NaNs at the tail where future horizon cannot be calculated
        df = df.dropna(subset=return_cols)

        # Apply Task-Specific Labeling
        if task_type == TaskType.BINARY_CLASSIFICATION:
            base_col = f"return_{primary_h}d"
            threshold = thresholds[0] if thresholds else 0.0
            df["target"] = (df[base_col] > threshold).astype(int)
            df = df.drop(columns=return_cols)
            
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
            base_col = f"return_{primary_h}d"
            if len(thresholds) >= 2:
                lower, upper = thresholds[0], thresholds[1]
                conditions = [
                    (df[base_col] < lower),
                    (df[base_col] >= lower) & (df[base_col] <= upper),
                    (df[base_col] > upper)
                ]
                choices = [0, 1, 2]
                df["target"] = np.select(conditions, choices, default=1)
            else:
                threshold = thresholds[0] if thresholds else 0.0
                df["target"] = (df[base_col] > threshold).astype(int)
            df = df.drop(columns=return_cols)

        elif task_type == TaskType.REGRESSION:
            # Leave return_{primary_h}d column as target
            pass

        elif task_type == TaskType.MULTI_OUTPUT_REGRESSION:
            # Leave return_{h}d columns as targets
            pass

        return df, target_cols

# Register the strategy
StrategyRegistry.register(LegacyTargetStrategy)
