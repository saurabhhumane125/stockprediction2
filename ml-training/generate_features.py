import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.trend import EMAIndicator

df = pd.read_csv("datasets/raw/RELIANCE.csv")

rsi = RSIIndicator(close=df["Close"], window=14)
df["RSI"] = rsi.rsi()

macd = MACD(close=df["Close"])
df["MACD"] = macd.macd()

ema20 = EMAIndicator(close=df["Close"], window=20)
df["EMA20"] = ema20.ema_indicator()

ema50 = EMAIndicator(close=df["Close"], window=50)
df["EMA50"] = ema50.ema_indicator()

print(df.head())
print(df.columns)

df.to_csv("datasets/featured_reliance.csv", index=False)

print("saved")
