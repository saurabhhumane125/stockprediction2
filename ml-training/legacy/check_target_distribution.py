import pandas as pd

df = pd.read_csv(
    "datasets/final_training_dataset.csv"
)

print(df["Target"].value_counts())
print(df["Target"].value_counts(normalize=True))
