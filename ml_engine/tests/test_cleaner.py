import pandas as pd
import numpy as np
import pytest

from ml_engine.data.preprocess.cleaner import ProductionCleaner


@pytest.fixture
def dirty_dataframe():
    dates = ["2023-01-01", "2023-01-01", "2023-01-03", "2023-01-02", "2023-01-04"]
    df = pd.DataFrame({
        "open": [100, 100, np.nan, 102, 105],
        "high": [105, 105, 108, 106, 2000], # Outlier 2000
        "low": [95, 95, 98, np.nan, 100],
        "close": [102, 102, 105, 104, 108],
        "volume": [1000, 1000, np.nan, 1500, 2000]
    }, index=pd.to_datetime(dates).tz_localize("Asia/Kolkata"))
    return df


def test_cleaner_execution(dirty_dataframe):
    cleaner = ProductionCleaner(outlier_std_devs=2.0)
    df_clean = cleaner.clean(dirty_dataframe)
    
    # 1. Deduplication (2023-01-01 was duplicated)
    assert len(df_clean) == 4
    
    # 2. Sorting (2023-01-03 and 2023-01-02 were out of order)
    assert df_clean.index.is_monotonic_increasing
    
    # 3. Timezone normalization (must be UTC naive)
    assert df_clean.index.tz is None
    
    # 4. Missing value handling (forward fill for prices, 0 for volume)
    # 2023-01-03 open was NaN. Previous chronological was 2023-01-02 open=102.
    assert df_clean.loc["2023-01-03", "open"] == 102
    assert df_clean.loc["2023-01-03", "volume"] == 0.0
    
    # 5. Type normalization
    assert df_clean["open"].dtype == np.float64
    
def test_cleaner_empty():
    cleaner = ProductionCleaner()
    df = cleaner.clean(pd.DataFrame())
    assert df.empty
    
def test_cleaner_all_missing():
    cleaner = ProductionCleaner()
    dates = ["2023-01-01", "2023-01-02"]
    df = pd.DataFrame({
        "open": [np.nan, np.nan],
        "close": [np.nan, np.nan],
    }, index=pd.to_datetime(dates))
    
    # Should drop rows that can't be forward filled
    df_clean = cleaner.clean(df)
    assert df_clean.empty
