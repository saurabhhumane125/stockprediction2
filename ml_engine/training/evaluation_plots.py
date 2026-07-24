"""
ml_engine/training/evaluation_plots.py
─────────────────────────────────────────────────────────────────────────────
Utilities to generate diagnostic evaluation plots and threshold optimizations.
─────────────────────────────────────────────────────────────────────────────
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_curve, auc, precision_recall_curve, average_precision_score,
    confusion_matrix, f1_score, precision_score, recall_score, accuracy_score
)
from sklearn.calibration import calibration_curve

def find_optimal_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Find the threshold that maximizes the F1 score."""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_prob)
    
    # Calculate F1 score for each threshold
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)
    
    # Handle the case where thresholds might be shorter than precisions/recalls
    if len(thresholds) > 0:
        optimal_idx = np.argmax(f1_scores[:-1]) # the last value corresponds to recall=0
        return float(thresholds[optimal_idx])
    return 0.5

def generate_evaluation_plots(
    y_true: np.ndarray, 
    y_prob: np.ndarray, 
    logits: np.ndarray, 
    output_dir: str, 
    prefix: str = "val"
) -> dict:
    """
    Generate and save evaluation plots.
    Args:
        y_true: (N,) true binary labels
        y_prob: (N,) predicted probabilities for class 1
        logits: (N, 2) raw logits
        output_dir: directory to save plots
        prefix: prefix for filenames (e.g., 'val' or 'test')
    Returns:
        dict mapping plot names to filenames.
    """
    os.makedirs(output_dir, exist_ok=True)
    paths = {}
    
    # 1. ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'{prefix.capitalize()} ROC Curve')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    p = os.path.join(output_dir, f"{prefix}_roc_curve.png")
    plt.savefig(p, bbox_inches='tight', dpi=100)
    plt.close()
    paths['roc_curve'] = f"{prefix}_roc_curve.png"

    # 2. Precision-Recall Curve
    precisions, recalls, _ = precision_recall_curve(y_true, y_prob)
    ap = average_precision_score(y_true, y_prob)
    plt.figure(figsize=(6, 5))
    plt.plot(recalls, precisions, color='blue', lw=2, label=f'PR curve (AP = {ap:.3f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'{prefix.capitalize()} Precision-Recall Curve')
    plt.legend(loc="lower left")
    plt.grid(True, alpha=0.3)
    p = os.path.join(output_dir, f"{prefix}_pr_curve.png")
    plt.savefig(p, bbox_inches='tight', dpi=100)
    plt.close()
    paths['pr_curve'] = f"{prefix}_pr_curve.png"

    # 3. Calibration Curve
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10)
    plt.figure(figsize=(6, 5))
    plt.plot(prob_pred, prob_true, marker='o', linewidth=2, label='Model')
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfectly calibrated')
    plt.xlabel('Mean predicted probability')
    plt.ylabel('Fraction of positives')
    plt.title(f'{prefix.capitalize()} Calibration Curve')
    plt.legend(loc="best")
    plt.grid(True, alpha=0.3)
    p = os.path.join(output_dir, f"{prefix}_calibration_curve.png")
    plt.savefig(p, bbox_inches='tight', dpi=100)
    plt.close()
    paths['calibration_curve'] = f"{prefix}_calibration_curve.png"

    # 4. Probability Histogram
    plt.figure(figsize=(6, 5))
    plt.hist(y_prob[y_true == 0], bins=50, alpha=0.5, label='Class 0', density=True)
    plt.hist(y_prob[y_true == 1], bins=50, alpha=0.5, label='Class 1', density=True)
    plt.xlabel('Predicted Probability (Class 1)')
    plt.ylabel('Density')
    plt.title(f'{prefix.capitalize()} Probability Histogram')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    p = os.path.join(output_dir, f"{prefix}_prob_histogram.png")
    plt.savefig(p, bbox_inches='tight', dpi=100)
    plt.close()
    paths['prob_histogram'] = f"{prefix}_prob_histogram.png"

    # 5. Logit Histogram
    if logits is not None and len(logits.shape) > 1 and logits.shape[1] >= 2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        ax1.hist(logits[y_true == 0, 0], bins=50, alpha=0.5, label='Actual 0', density=True)
        ax1.hist(logits[y_true == 1, 0], bins=50, alpha=0.5, label='Actual 1', density=True)
        ax1.set_title('Logits - Neuron 0')
        ax1.set_xlabel('Logit Value')
        ax1.set_ylabel('Density')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.hist(logits[y_true == 0, 1], bins=50, alpha=0.5, label='Actual 0', density=True)
        ax2.hist(logits[y_true == 1, 1], bins=50, alpha=0.5, label='Actual 1', density=True)
        ax2.set_title('Logits - Neuron 1')
        ax2.set_xlabel('Logit Value')
        ax2.set_ylabel('Density')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        p = os.path.join(output_dir, f"{prefix}_logit_histogram.png")
        plt.savefig(p, bbox_inches='tight', dpi=100)
        plt.close()
        paths['logit_histogram'] = f"{prefix}_logit_histogram.png"

    # 6. Metrics vs Threshold
    thresholds = np.linspace(0, 1, 100)
    accs, f1s, precs, recs = [], [], [], []
    for t in thresholds:
        preds = (y_prob >= t).astype(int)
        accs.append(accuracy_score(y_true, preds))
        f1s.append(f1_score(y_true, preds, zero_division=0))
        precs.append(precision_score(y_true, preds, zero_division=0))
        recs.append(recall_score(y_true, preds, zero_division=0))
        
    plt.figure(figsize=(8, 6))
    plt.plot(thresholds, accs, label='Accuracy', lw=2)
    plt.plot(thresholds, f1s, label='F1 Score', lw=2)
    plt.plot(thresholds, precs, label='Precision', lw=2)
    plt.plot(thresholds, recs, label='Recall', lw=2)
    plt.xlabel('Threshold')
    plt.ylabel('Score')
    plt.title(f'{prefix.capitalize()} Metrics vs Threshold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    p = os.path.join(output_dir, f"{prefix}_metrics_vs_threshold.png")
    plt.savefig(p, bbox_inches='tight', dpi=100)
    plt.close()
    paths['metrics_vs_threshold'] = f"{prefix}_metrics_vs_threshold.png"

    return paths


def generate_regression_evaluation_plots(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    output_dir: str,
    prefix: str = "val"
) -> dict:
    """
    Generate diagnostic evaluation plots for regression tasks.
    Args:
        y_true: Ground truth target values
        y_pred: Model prediction values
        output_dir: Directory to save plots
        prefix: Prefix for filenames ('val' or 'test')
    Returns:
        dict mapping plot names to filenames.
    """
    os.makedirs(output_dir, exist_ok=True)
    paths = {}
    
    y_t = y_true.squeeze()
    y_p = y_pred.squeeze()

    # 1. Prediction vs Actual Scatter Plot
    plt.figure(figsize=(6, 5))
    plt.scatter(y_t, y_p, alpha=0.3, color='blue', edgecolors='none', s=15)
    min_val = min(np.min(y_t), np.min(y_p))
    max_val = max(np.max(y_t), np.max(y_p))
    plt.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--', label='1:1 Line')
    plt.xlabel('Actual Target')
    plt.ylabel('Predicted Target')
    plt.title(f'{prefix.capitalize()} Predicted vs Actual')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    p = os.path.join(output_dir, f"{prefix}_pred_vs_actual.png")
    plt.savefig(p, bbox_inches='tight', dpi=100)
    plt.close()
    paths['pred_vs_actual'] = f"{prefix}_pred_vs_actual.png"

    # 2. Residual Distribution Histogram
    residuals = y_t - y_p
    plt.figure(figsize=(6, 5))
    plt.hist(residuals, bins=50, color='teal', alpha=0.7, edgecolor='black')
    plt.axvline(0, color='red', linestyle='--', label='Zero Error')
    plt.xlabel('Residual (Actual - Predicted)')
    plt.ylabel('Frequency')
    plt.title(f'{prefix.capitalize()} Residual Distribution')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    p = os.path.join(output_dir, f"{prefix}_residual_histogram.png")
    plt.savefig(p, bbox_inches='tight', dpi=100)
    plt.close()
    paths['residual_histogram'] = f"{prefix}_residual_histogram.png"

    return paths

