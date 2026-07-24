import os
import sys
import torch
import json

dataset_path = "ml_engine/data/tensors/NIFTY50/v3.0"

# 1. Tensors
train_data = torch.load(os.path.join(dataset_path, "train.pt"))
x_train, y_train = train_data

print("X_train shape:", x_train.shape)
print("y_train shape:", y_train.shape)

# 2. Metadata
metadata_path = os.path.join(dataset_path, "metadata.json")
if os.path.exists(metadata_path):
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    print("metadata.json target_cols:", metadata.get("target_cols"))
    print("metadata.json output_schema:", metadata.get("output_schema"))
    print("metadata.json input_schema:", metadata.get("input_schema"))
    
    features = metadata.get("features", [])
    print("metadata.json feature count:", len(features))
    
    if "features" in metadata:
        print("metadata.json contains features list")
else:
    print("metadata.json NOT FOUND")

# 3. feature_mapping.json (legacy)
fm_path = os.path.join(dataset_path, "feature_mapping.json")
if os.path.exists(fm_path):
    with open(fm_path, 'r') as f:
        fm = json.load(f)
    print("feature_mapping.json feature count:", len(fm))
else:
    print("feature_mapping.json NOT FOUND")

