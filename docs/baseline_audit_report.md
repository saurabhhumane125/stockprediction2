# Production Baseline Audit Report

## Section 1: Dataset Audit
Based on analysis of `datasets/final_training_dataset.csv`:
* **Total Rows:** 20,440
* **Unique Stocks:** 10
* **Ticker List:** `BHARTIARTL`, `HDFCBANK`, `HINDUNILVR`, `ICICIBANK`, `INFY`, `ITC`, `LT`, `RELIANCE`, `SBIN`, `TCS`
* **Rows per Stock:** Exactly 2,044 rows each
* **Earliest Date:** 2018-03-14
* **Latest Date:** 2026-06-22
* **Missing Dates:** No missing dates within the uniform 2,044 observations (enforced by `_handle_missing_values` in `cleaner.py`).
* **Trading Calendar:** Unspecified / standard market days (the data reflects ~252 trading days/year over ~8 years).
* **Current Interval:** Daily (1d). 
  * *Proof:* The date ranges cover ~8 years yielding ~2,000 observations per stock. Additionally, `cleaner.py` standardizes timezones and `generator.py` calculates annualized volatility using `np.sqrt(252)`, which explicitly hardcodes the assumption of 252 daily trading sessions per year.

## Section 2: Feature Audit
Found inside `ml_engine/data/features/generator.py`. All features are `float64`.
Total Engineered Features: 16 (excluding OHLCV and Target).

1. **daily_return**: Percentage change from previous close (Any range).
2. **ema_short**: Exponential Moving Average, period=20 (Positive).
3. **ema_long**: Exponential Moving Average, period=50 (Positive).
4. **rsi**: Relative Strength Index, period=14 ([0, 100]).
5. **macd_line**: MACD Line (Any range).
6. **macd_signal**: MACD Signal Line (Any range).
7. **macd_histogram**: MACD Histogram (Any range).
8. **bb_upper**: Bollinger Band Upper, period=20 (Positive).
9. **bb_lower**: Bollinger Band Lower, period=20 (Positive).
10. **bb_width**: Bollinger Band Width Normalized (Positive).
11. **atr**: Average True Range, period=14 (Positive).
12. **adx**: Average Directional Index, period=14 ([0, 100]).
13. **roc**: Rate of Change, period=10 (Any range).
14. **momentum**: Absolute Momentum, period=10 (Any range).
15. **volatility**: Annualized Historical Volatility, period=20 (Positive).
16. **volume_change**: Daily Volume Percentage Change (Any range).

## Section 3: Target Audit
* **What does the model predict?** Binary movement (Next close).
* **Proof:** Found in `ml_engine/data/tensors/utils.py` and `training_config.py`.
```python
future_return = df["close"].pct_change(periods=training_config.FORECAST_HORIZON).shift(-training_config.FORECAST_HORIZON)
df["target"] = (df["future_return"] > (training_config.RETURN_THRESHOLD_BPS / 10000.0)).astype(int)
```
* With `FORECAST_HORIZON = 1` and `RETURN_THRESHOLD_BPS = 0.0`, the target evaluates to `1` (Buy/Up) if the next period's closing price is strictly greater than the current close, and `0` otherwise. It is a binary classification predicting a positive return for the next step.

## Section 4: Model Audit
Found inside `ml_engine/models/model_factory.py`.
The following models are registered and implemented as `BaseTimeSeriesClassifier`s:

1. **GRU (GRUClassifier)**: Implemented. Production, Training, and Inference ready.
2. **BiGRU (BiGRUClassifier)**: Implemented. Production, Training, and Inference ready.
3. **LSTM (LSTMClassifier)**: Implemented. Production, Training, and Inference ready.
4. **Transformer (TransformerClassifier)**: Implemented. Production, Training, and Inference ready.

## Section 5: Training Config
Found inside `ml_engine/config/training_config.py`.
* **Sequence length:** 48
* **Batch size:** 64
* **Learning rate:** 1e-3 (0.001)
* **Optimizer:** Adam
* **Epoch count:** 100
* **Early stopping:** Patience of 15, monitoring `val_loss`
* **Scheduler:** ReduceLROnPlateau (Patience: 5, Factor: 0.5, Min LR: 1e-6)
* **Mixed precision:** False
* **Gradient clipping:** 1.0 (max-norm)

## Section 6: Current Model Quality
* **Metrics:** Unavailable.
* **Why:** The system is currently staged at the end of the engineering phase. The first true production GPU training lifecycle has not been executed yet. The current model artifacts inside `artifacts/candidates/CORE/` contain dummy metadata placeholders.

## Section 7: Dataset Limitations
* **Current Stock Universe:** 10 stocks. 
  * *Proof:* The python script analyzed `final_training_dataset.csv` and found exactly 10 tickers.
* **Historical Data Amount:** ~8 years (2,044 daily rows) per stock = 20,440 total rows.
* **Estimated Expansion:**
  * **NIFTY 50:** 50 stocks * 2,044 rows = ~102,200 rows.
  * **NIFTY 100:** 100 stocks * 2,044 rows = ~204,400 rows.

## Section 8: Intraday Readiness
The current architecture **does NOT support** intraday (5m, 15m, 30m, 1h) predictions out of the box. 

**What exactly must change:**
1. **Time Indexing:** `cleaner.py` and downstream pipelines must handle explicit granular timestamps (e.g., `pd.DatetimeIndex` with minute frequencies) instead of timezone-naive dates. The dataset currently uses simple `Date`.
2. **Annualization Constants:** `generator.py` hardcodes `np.sqrt(252)` for historical volatility. This must be refactored to be dynamically aware of the interval (e.g., 252 * 375 minutes for a 5-minute Indian trading session).
3. **Missing Values/Gaps:** `_handle_missing_values` assumes overnight gaps are natural. Intraday data requires complex gap filling for non-trading hours, weekends, and holidays.
4. **Config Values:** `FORECAST_HORIZON` (currently 1) works agnostically, but `SEQUENCE_LENGTH` of 48 for 5m intraday data only covers 4 hours, which loses macro-context. 

## Section 9: Production Gap Analysis
Compared to the final objective (Production-grade intraday trading prediction, >60% confidence, high-quality probability calibration).

1. **Intraday Data Infrastructure (High Priority):** Pipeline hardcodes daily constants and dates. Needs dynamic frequency handling.
2. **Dataset Scale (High Priority):** 10 stocks are insufficient to generalize macro-market regimes. Need NIFTY 50/100 scale.
3. **Hyperparameter Tuning (Medium Priority):** Sequences, batch sizes, and model depths are static defaults. Needs optimization.
4. **Model Calibration (Medium Priority):** Binary targets with Cross-Entropy loss require post-training probability calibration (e.g., Platt Scaling/Isotonic) to ensure predictions represent true probabilities.
5. **Class Imbalance Handling (Medium Priority):** Binary market returns naturally drift. The target generation lacks threshold dynamics to maintain balance.

## Section 10: Roadmap
1. **Current**
2. **Run 1 (Baseline Training Execution)**
3. **Dataset Expansion (NIFTY 50/100)**
4. **Intraday System (5m/15m adaptation, Timezone/Gap fixes)**
5. **Architecture Comparison (GRU vs Transformer on Intraday)**
6. **Hyperparameter Optimization (Sequence length, thresholds)**
7. **Calibration (Probability mapping)**
8. **Production Promotion**
