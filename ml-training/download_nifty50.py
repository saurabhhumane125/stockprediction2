import yfinance as yf

ticker = "RELIANCE.NS"

df = yf.download(
    ticker,
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

df.to_csv("datasets/reliance.csv")

print(df.head())
print(df.columns)
print(df.shape)
print("saved")
