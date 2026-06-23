import yfinance as yf
import os

stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "INFY.NS",
    "LT.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "HINDUNILVR.NS"
]

os.makedirs("datasets/raw", exist_ok=True)

for stock in stocks:
    print(f"Downloading {stock}...")

    df = yf.download(
        stock,
        start="2018-01-01",
        end="2026-06-23",
        auto_adjust=True,
        progress=False
    )

    if hasattr(df.columns, "droplevel"):
        try:
            df.columns = df.columns.droplevel(1)
        except:
            pass

    filename = stock.replace(".NS", ".csv")

    df.to_csv(f"datasets/raw/{filename}")

print(df.shape)
print(f"Saved {filename}")
print("Done")
