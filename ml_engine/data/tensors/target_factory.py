import pandas as pd
import numpy as np
from typing import List, Tuple
from ml_engine.core.types import TaskType

class TargetFactory:
    """
    Production Target Factory.
    Generates targets based on configuration without hardcoding logic in the Builder.
    """

    @staticmethod
    def generate(df: pd.DataFrame, target_config: type) -> pd.DataFrame:
        """
        Applies the configured target logic to the DataFrame.
        """
        df = df.copy()
        
        # Determine the target column(s) based on Horizons
        horizons = getattr(target_config, "horizons", [1])
        task_type = getattr(target_config, "task_type", TaskType.BINARY_CLASSIFICATION)
        target_type = getattr(target_config, "target_type", "CLASS")
        thresholds = getattr(target_config, "thresholds", [0.0])
        
        # Calculate base future returns for active horizons
        return_cols = []
        for h in horizons:
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
            h = target_config.primary_horizon
            base_col = f"return_{h}d"
            threshold = thresholds[0] if thresholds else 0.0
            df["target"] = (df[base_col] > threshold).astype(int)
            df = df.drop(columns=return_cols)
            
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
            h = target_config.primary_horizon
            base_col = f"return_{h}d"
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
            # Leave the return_{h}d column as is, no rename to target
            pass

        elif task_type == TaskType.MULTI_OUTPUT_REGRESSION:
            # Leave the return_{h}d columns as is
            pass

        return df
