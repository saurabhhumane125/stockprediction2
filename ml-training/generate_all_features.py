import os
import pandas as pd

from ta.momentum import RSIIndicator, ROCIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange, BollingerBands

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

    df["ATR"] = AverageTrueRange(
    high=df["High"],
    low=df["Low"],
    close=df["Close"]
    ).average_true_range()

    df["ADX"] = ADXIndicator(
    high=df["High"],
    low=df["Low"],
    close=df["Close"]
    ).adx()

    bb = BollingerBands(
    close=df["Close"],
    window=20,
    window_dev=2
    )

    df["BB_UPPER"] = bb.bollinger_hband()
    df["BB_LOWER"] = bb.bollinger_lband()
    df["BB_WIDTH"] = (
    df["BB_UPPER"] - df["BB_LOWER"]
    )

    df["ROC"] = ROCIndicator(
    close=df["Close"],
    window=12
    ).roc()

    df["MOMENTUM"] = (
    df["Close"] - df["Close"].shift(10)
    )

    df["DAILY_RETURN"] = (
    df["Close"].pct_change()
    )

    df["VOLATILITY"] = (
    df["DAILY_RETURN"]
    .rolling(10)
    .std()
    )

    df["VOLUME_CHANGE"] = (
    df["Volume"].pct_change()
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        file
    )

    df.to_csv(output_path, index=False)

    print(f"Processed {file}")

print("Done")
