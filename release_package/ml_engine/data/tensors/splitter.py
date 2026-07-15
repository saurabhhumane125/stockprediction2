"""
ml_engine/data/tensors/splitter.py
─────────────────────────────────────────────────────────────────────────────
Handles chronological splitting of dataframes into Train/Val/Test.
─────────────────────────────────────────────────────────────────────────────
"""
import pandas as pd
from typing import Tuple
from ml_engine.config.training_config import training_config


class ChronologicalSplitter:
    """Strictly chronological data splitting (no random shuffles)."""

    @staticmethod
    def split_by_date(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Splits dataframe by configured dates.
        """
        train_end = training_config.TRAIN_END_DATE
        val_end = training_config.VAL_END_DATE
        
        # Ensure index is datetime if it isn't already
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            try:
                df.index = pd.to_datetime(df.index)
            except Exception:
                pass # If it fails, fallback to string comparison
        
        train_df = df.loc[:train_end]
        val_df = df.loc[train_end:val_end]
        
        # Avoid overlap
        if len(val_df) > 0 and len(train_df) > 0 and val_df.index[0] == train_df.index[-1]:
            val_df = val_df.iloc[1:]
            
        test_df = df.loc[val_end:]
        if len(test_df) > 0 and len(val_df) > 0 and test_df.index[0] == val_df.index[-1]:
            test_df = test_df.iloc[1:]
            
        return train_df, val_df, test_df
