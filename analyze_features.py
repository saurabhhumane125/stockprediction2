import numpy as np
import torch
import scipy.stats as stats

tensor_path = 'ml_engine/data/tensors/NIFTY50/v3.0/test.pt'
X, y = torch.load(tensor_path)
X = X.numpy()
y = y.numpy()

# X shape is (N, seq_len, 38)
# We'll take the last step of the sequence for correlation: X[:, -1, :]
X_last = X[:, -1, :]

feature_names = [
    "open", "high", "low", "close", "volume", "dividends", "stock_splits", 
    "daily_return", "ema_short", "ema_long", "rsi", "macd_line", "macd_signal", 
    "macd_histogram", "bb_upper", "bb_lower", "bb_width", "atr", "adx", "roc", 
    "momentum", "volatility", "volume_change", "return_lag_1", "return_lag_2", 
    "return_lag_3", "return_lag_5", "rolling_return_5", "rolling_return_10", 
    "rolling_volatility_5", "rolling_volatility_10", "obv", "cmf", 
    "rolling_vwap_20", "nifty_return", "nifty_ema20", "nifty_rsi14", "india_vix_close"
]

print("--- FEATURE CORRELATION WITH TARGET ---")
correlations = []
for i in range(X_last.shape[1]):
    corr, _ = stats.pearsonr(X_last[:, i], y)
    correlations.append((feature_names[i], corr))

correlations.sort(key=lambda x: abs(x[1]), reverse=True)
for name, corr in correlations:
    print(f"{name}: {corr:.4f}")
