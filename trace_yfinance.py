import yfinance as yf
import pandas as pd

def _standardize_dataframe(df: pd.DataFrame, ticker: str):
    print(f"\n[INIT] Shape before standardization: {df.shape}")
    print(df.columns)
    
    if df.empty:
        print("DF is empty at start")
        return pd.DataFrame()
        
    df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
    print(f"[STEP 1] Shape after tz_localize: {df.shape}")
    
    df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
    print(f"[STEP 2] Shape after lowercase columns: {df.shape}")
    print(f"Columns: {df.columns}")
    
    expected_cols = ["open", "high", "low", "close", "volume", "dividends", "stock_splits"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0.0 if col in ["dividends", "stock_splits"] else pd.NA
            
    print(f"[STEP 3] Shape after adding missing cols: {df.shape}")
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        print(f"[STEP 4] Shape after flattening MultiIndex: {df.shape}")
        
    df["ticker"] = ticker
    print(f"[STEP 5] Shape after adding ticker col: {df.shape}")
    
    df = df[expected_cols + ["ticker"]]
    print(f"[STEP 6] Shape after keeping expected cols: {df.shape}")
    print(f"Final columns: {df.columns}")
    return df

print("Downloading with Ticker.history...")
t = yf.Ticker("RELIANCE.NS")
df1 = t.history(start="2023-08-11", end="2024-01-12", interval="1d", actions=True, auto_adjust=True)
_standardize_dataframe(df1, "RELIANCE.NS")

print("\nDownloading with yf.download...")
df2 = yf.download("RELIANCE.NS", start="2023-08-11", end="2024-01-12", interval="1d", progress=False)
_standardize_dataframe(df2, "RELIANCE.NS")
