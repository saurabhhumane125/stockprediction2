import pandas as pd

df = pd.read_csv(
    "datasets/combined_dataset.csv"
)

df["Target"] = (
    df["Close"].shift(-1) > df["Close"]
).astype(int)

df = df[:-1]

df.to_csv(
    "datasets/training_dataset.csv",
    index=False
)

print(df.shape)
print(df["Target"].value_counts())
print("saved")
