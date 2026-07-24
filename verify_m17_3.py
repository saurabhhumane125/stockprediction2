import os
import torch
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import r2_score
import warnings

# Load configurations
from ml_engine.config.training_config import training_config
from ml_engine.config.model_config import model_config
from ml_engine.models.model_factory import ModelFactory
from ml_engine.training.loss_factory import LossFactory
from ml_engine.core.types import TaskType

def investigate():
    print("--- STARTING M17.3 INVESTIGATION ---")
    
    # 1. Load data
    train_path = "ml_engine/data/tensors/NIFTY50/v3.0/train.pt"
    test_path = "ml_engine/data/tensors/NIFTY50/v3.0/test.pt"
    
    train_X, train_y = torch.load(train_path)
    test_X, test_y = torch.load(test_path)
    
    print(f"Loaded Train: {train_X.shape}, {train_y.shape}")
    print(f"Loaded Test: {test_X.shape}, {test_y.shape}")
    
    # Target Distribution
    y_np = test_y.numpy()
    print("TARGET_MIN:", np.min(y_np))
    print("TARGET_MAX:", np.max(y_np))
    print("TARGET_MEAN:", np.mean(y_np))
    print("TARGET_MEDIAN:", np.median(y_np))
    print("TARGET_STD:", np.std(y_np))
    print("TARGET_VAR:", np.var(y_np))
    print("TARGET_P25:", np.percentile(y_np, 25))
    print("TARGET_P75:", np.percentile(y_np, 75))
    print("TARGET_FIRST_100:", list(np.round(y_np[:100], 6)))
    
    # 2. Build model and optimizer
    input_shape = (train_X.shape[1], train_X.shape[2])
    # The config expects output dimension = 1 for Regression
    model = ModelFactory.create(
        model_type="GRU",
        input_size=input_shape[1],
        
        overrides={'output_classes': 1}
    )
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=training_config.LEARNING_RATE)
    criterion = LossFactory.get_loss(TaskType.REGRESSION)
    scaler = torch.cuda.amp.GradScaler(enabled=training_config.MIXED_PRECISION)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Get parameters before step
    params_before = {name: p.clone().detach() for name, p in model.named_parameters()}
    
    # 3. Training dynamics
    batch_size = training_config.BATCH_SIZE
    losses = {}
    
    model.train()
    for batch_idx, start in enumerate(range(0, len(train_X), batch_size), 1):
        end = start + batch_size
        if end > len(train_X):
            break
            
        X_batch = train_X[start:end].float().to(device)
        y_batch = train_y[start:end].float().to(device)
        
        optimizer.zero_grad()
        
        # Following exact logic in training_pipeline
        with torch.cuda.amp.autocast(enabled=training_config.MIXED_PRECISION):
            logits = model(X_batch)
            logits = logits.view_as(y_batch)
            loss = criterion(logits, y_batch)
            
        losses[f"Batch_{batch_idx}"] = loss.item()
        
        scaler.scale(loss).backward()
        
        if batch_idx == 1:
            # Capture gradients
            print("--- GRADIENTS BATCH 1 ---")
            for name, p in model.named_parameters():
                if p.grad is not None:
                    # Unscale gradients for inspection if they were scaled
                    inv_scale = 1.0 / scaler.get_scale()
                    grad = p.grad.detach() * inv_scale
                    print(f"GRAD_{name}: NORM={grad.norm().item():.8e} MIN={grad.min().item():.8e} MAX={grad.max().item():.8e} MEAN={grad.mean().item():.8e}")
                else:
                    print(f"GRAD_{name}: NONE")
            
            # Parameter update verification
            scaler.unscale_(optimizer)
            if training_config.GRADIENT_CLIP_NORM > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), training_config.GRADIENT_CLIP_NORM)
            scaler.step(optimizer)
            scaler.update()
            
            params_after = {name: p.clone().detach() for name, p in model.named_parameters()}
            print("--- PARAMETER UPDATES BATCH 1 ---")
            for name in params_before:
                diff = (params_after[name] - params_before[name]).abs().mean().item()
                print(f"UPDATE_{name}: MEAN_ABS_DIFF={diff:.8e}")
    
    for k, v in losses.items():
        print(f"LOSS_{k}: {v:.8f}")

    # 4. Predictions on test set (to match artifacts)
    model.eval()
    all_preds = []
    with torch.no_grad():
        for i in range(0, len(test_X), batch_size):
            X_batch = test_X[i:i+batch_size].float().to(device)
            y_batch = test_y[i:i+batch_size].float().to(device)
            logits = model(X_batch).view_as(y_batch)
            all_preds.append(logits.cpu().numpy())
            
    test_preds = np.concatenate(all_preds)
    
    print("PRED_MIN:", np.min(test_preds))
    print("PRED_MAX:", np.max(test_preds))
    print("PRED_MEAN:", np.mean(test_preds))
    print("PRED_MEDIAN:", np.median(test_preds))
    print("PRED_STD:", np.std(test_preds))
    print("PRED_VAR:", np.var(test_preds))
    print("PRED_P25:", np.percentile(test_preds, 25))
    print("PRED_P75:", np.percentile(test_preds, 75))
    print("PRED_FIRST_100:", list(np.round(test_preds[:100], 6)))
    
    # 5. R2 Calculation exactly as sklearn
    # R2 = 1 - (SS_res / SS_tot)
    ss_res = np.sum((y_np - test_preds) ** 2)
    ss_tot = np.sum((y_np - np.mean(y_np)) ** 2)
    r2 = 1 - (ss_res / ss_tot)
    print(f"R2_SS_RES: {ss_res:.8f}")
    print(f"R2_SS_TOT: {ss_tot:.8f}")
    print(f"R2_COMPUTED: {r2:.8f}")
    print(f"R2_SKLEARN: {r2_score(y_np, test_preds):.8f}")
    
    # 6. IC / ConstantInputWarning Calculation
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        corr, pval = spearmanr(y_np, test_preds)
        print(f"SPEARMAN_RAW: {corr}")
        if len(w) > 0:
            print(f"WARNING_CAUGHT: {w[-1].message}")

if __name__ == "__main__":
    investigate()
