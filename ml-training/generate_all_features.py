import os
import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.trend import EMAIndicator

INPUT_DIR = "datasets/raw"
OUTPUT_DIR = "datasets/features"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):

    if not file.endswith(".csv"):
        continue

    path = os.path.join(INPUT_DIR, file)

    df = pd.read_csv(path)

    df["RSI"] = RSIIndicator(
        close=df["Close"],
        window=14
    ).rsi()

    df["MACD"] = MACD(
        close=df["Close"]
    ).macd()

    df["EMA20"] = EMAIndicator(
        close=df["Close"],
        window=20
    ).ema_indicator()

    df["EMA50"] = EMAIndicator(
        close=df["Close"],
        window=50
    ).ema_indicator()

    output_path = os.path.join(
        OUTPUT_DIR,
        file
    )

    df.to_csv(output_path, index=False)

    print(f"Processed {file}")

print("Done")
