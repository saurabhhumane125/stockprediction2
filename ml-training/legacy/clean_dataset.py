import pandas as pd

df = pd.read_csv(
    "datasets/training_dataset.csv"
)

before = len(df)

df = df.dropna()

after = len(df)

print("Before:", before)
print("After :", after)

df.to_csv(
    "datasets/final_training_dataset.csv",
    index=False
)

print("saved")
