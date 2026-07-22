import pandas as pd
import json
import os

try:
    df = pd.read_csv('d:/STOCK-PREDICTION-UI/datasets/final_training_dataset.csv')
    
    col_sym = "Stock" if "Stock" in df.columns else None
    col_date = "Date" if "Date" in df.columns else None

    print(f"Total rows: {len(df)}")
    
    if col_sym:
        tickers = df[col_sym].unique()
        print(f"Tickers ({len(tickers)}): {list(tickers)}")
        print("Rows per ticker:")
        print(df[col_sym].value_counts().to_string())
    else:
        print("No symbol col")
        
    if col_date:
        print(f"Min date: {df[col_date].min()}")
        print(f"Max date: {df[col_date].max()}")
    else:
        print("no date")
        
    print(f"Columns: {df.columns.tolist()}")
except Exception as e:
    print("Error:", e)
