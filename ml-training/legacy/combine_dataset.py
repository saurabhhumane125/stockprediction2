import os
import pandas as pd

INPUT_DIR = "datasets/features"

all_data = []

for file in os.listdir(INPUT_DIR):

    if not file.endswith(".csv"):
        continue

    df = pd.read_csv(
        os.path.join(INPUT_DIR, file)
    )

    stock_name = file.replace(".csv", "")

    df["Stock"] = stock_name

    all_data.append(df)

combined = pd.concat(
    all_data,
    ignore_index=True
)

combined.to_csv(
    "datasets/combined_dataset.csv",
    index=False
)

print(combined.shape)
print("saved")
