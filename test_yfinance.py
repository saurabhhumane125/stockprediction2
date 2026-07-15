import yfinance as yf

print("Downloading...")

df = yf.download(
    "RELIANCE.NS",
    start="2023-08-11",
    end="2024-01-12",
    interval="1d",
    progress=False,
)

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nFirst 5 rows:")
print(df.head())

print("\nLast 5 rows:")
print(df.tail())