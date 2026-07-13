import pandas as pd

INPUT_FILE = "datasets/combined_dataset.csv"
OUTPUT_FILE = "datasets/training_dataset.csv"

# Load dataset
df = pd.read_csv(INPUT_FILE)

# Ensure proper ordering within each stock
df["Date"] = pd.to_datetime(df["Date"])

df = (
    df.sort_values(["Stock", "Date"])
      .reset_index(drop=True)
)

# Create target independently for each stock
df["Target"] = (
    df.groupby("Stock")["Close"]
      .shift(-1)
      .gt(df["Close"])
)

# Remove the last row of every stock
df = df.dropna(subset=["Target"]).copy()

# Convert boolean target to integer
df["Target"] = df["Target"].astype(int)

# Save
df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Shape:", df.shape)

print("\nTarget Distribution:")
print(df["Target"].value_counts())

print("\nStocks:")
print(df["Stock"].value_counts())

print("\nSaved:", OUTPUT_FILE)
