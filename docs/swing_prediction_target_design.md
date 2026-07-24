# Milestone M12: Swing Prediction Target Design

## 1. Current Swing Prediction Pipeline Analysis
Based on a strict audit of the repository (`ml_engine/data/tensors/utils.py` and `ml_engine/config/training_config.py`), the current pipeline operates as a **1-Day Binary Direction Predictor**.
*   **What it predicts today**: Whether the next day's closing price will be strictly greater than today's closing price.
*   **Formulation**: `target = 1 if (Close[t+1] / Close[t] - 1) > 0.0 else 0`.
*   **Horizon**: Exactly 1 trading day.
*   **Weakness**: As established in M11, predicting 1-day direction at a 0.0 threshold suffers from insurmountable label noise (micro-fluctuations are forced into deterministic classes).

---

## 2 & 3. Prediction Target Comparison

### A. Future Closing Price
*   **Mathematical formulation**: $y = Close_{t+h}$
*   **Advantages**: Highly intuitive; directly translates to asset value.
*   **Disadvantages**: Non-stationary. Models trained on absolute prices fail catastrophically when an asset's price enters a new regime (e.g., a stock splitting or rallying 200%).
*   **Training/Inference Impact**: High risk of exploding gradients; requires intense scaling.
*   **Evaluation metrics**: RMSE, MAE, MAPE.
*   **Suitability**: **Very Low**. Non-stationary targets violate core ML assumptions.

### B. Future Percentage Return
*   **Mathematical formulation**: $y = (Close_{t+h} - Close_t) / Close_t$
*   **Advantages**: Stationary; scale-invariant across different stocks.
*   **Disadvantages**: Asymmetric (bounded at -100% but unbounded upwards), susceptible to extreme outlier days (fat tails) which skew MSE loss.
*   **Training/Inference Impact**: Standard regression framework.
*   **Evaluation metrics**: RMSE, MAE, R², Information Coefficient (IC).
*   **Suitability**: **Medium**.

### C. Future Log Return
*   **Mathematical formulation**: $y = \ln(Close_{t+h} / Close_t)$
*   **Advantages**: Time-additive; symmetric; mitigates the impact of extreme positive outliers compared to simple percentage returns.
*   **Disadvantages**: Slightly less intuitive for business logic/frontend consumption.
*   **Training/Inference Impact**: Smooth gradient descent due to symmetric bounded loss.
*   **Evaluation metrics**: RMSE, MAE, IC.
*   **Suitability**: **High**.

### D. 3-Day / 5-Day / 10-Day Forecast
*   **Mathematical formulation**: $y_h = \ln(Close_{t+h} / Close_t)$ for $h \in \{3, 5, 10\}$
*   **Advantages**: Filters out 1-day intraday market noise. Strongly aligns with real-world swing trading (holding periods of a few days to two weeks).
*   **Disadvantages**: Overlapping observations cause serial correlation (autocorrelation) in the loss, which can cause overfitting if not addressed via purged cross-validation.
*   **Training/Inference Impact**: Requires modifying the forecast horizon variable.
*   **Evaluation metrics**: RMSE, IC, Directional Accuracy.
*   **Suitability**: **Very High** (specifically 5-day, which aligns with 1 trading week).

### E. Multi-Horizon Forecasting
*   **Mathematical formulation**: $Y = [y_1, y_3, y_5, y_{10}]$ (Vector output)
*   **Advantages**: The model learns the entire trajectory of the swing, rather than a single point in time, heavily improving regularization.
*   **Disadvantages**: Complex architecture. The loss function must weight different horizons.
*   **Training/Inference Impact**: Requires multi-head output layer or Seq2Seq architecture.
*   **Evaluation metrics**: Horizon-weighted RMSE, Horizon-specific IC.
*   **Suitability**: **Medium**. Excellent, but too complex for an immediate iteration.

### F. Prediction Intervals (Expected High/Low Range)
*   **Mathematical formulation**: Predict $y_{upper}, y_{lower}$ using Quantile Regression (e.g., 90th and 10th percentiles).
*   **Advantages**: Provides explicit risk/reward boundaries for setting stop-losses and take-profits.
*   **Disadvantages**: Does not directly predict "where" the price will go, only the bounds of volatility.
*   **Training/Inference Impact**: Requires Quantile Loss (Pinball Loss).
*   **Evaluation metrics**: Coverage Ratio, Mean Interval Width.
*   **Suitability**: **Low** as a primary target, but great as an auxiliary target.

### G. Confidence Estimation
*   **Mathematical formulation**: Predicts a categorical probability distribution or regression variance.
*   **Advantages**: Highly actionable. The Decision Engine only trades when confidence is > 80%.
*   **Disadvantages**: Deep learning models are notoriously overconfident (poorly calibrated) unless heavily regularized or explicitly calibrated (e.g., Platt scaling).
*   **Training/Inference Impact**: Requires post-training calibration pipelines (which are present in the current codebase).
*   **Evaluation metrics**: Brier Score, Expected Calibration Error (ECE).
*   **Suitability**: **High** as an activation layer over the primary target.

---

## 4. Final Recommendation: The 5-Day Log Return Regression Architecture

I recommend shifting the Swing Prediction model from a 1-day binary classifier to a **5-Day Log Return Regression Model**.

*   **What the model predicts**: The continuous log return over the next 5 trading days (1 full week).
*   **Forecast Horizons**: $h = 5$.
*   **Required Labels**: $y = \ln(Close_{t+5} / Close_t)$.
*   **Required Evaluation Metrics**: 
    *   **Primary**: Information Coefficient (Rank Correlation between prediction and actual).
    *   **Secondary**: RMSE, MAE.
    *   **Business**: Hit Rate (Sign accuracy) and Expected Return per Trade.
*   **Expected API Response**: 
    ```json
    {
      "prediction_horizon": "5d",
      "expected_log_return": 0.025,
      "expected_percentage": 2.53,
      "signal": "STRONG_BUY" 
    }
    ```
*   **How the Decision Engine will consume predictions**: The backend Decision Engine will apply thresholding dynamically. For example, if `expected_percentage > 2.0%`, trigger `STRONG_BUY`. If between `-1%` and `1%`, trigger `HOLD`. This separates the **prediction** (machine learning) from the **action** (business logic), entirely removing label noise at training time while allowing the business logic to adjust to volatility.

---

## 5. Phased Implementation Roadmap

### Phase 1: Data Engineering
*   Update `training_config.py`: Set `FORECAST_HORIZON = 5`.
*   Update `ml_engine/data/tensors/utils.py`:
    *   Calculate future log returns: `np.log(df["close"].shift(-5) / df["close"])`
    *   Remove binary threshold logic. The target is now a float (`float32`).
*   Verify `TensorBuilder` gracefully handles continuous floats instead of binary integers.

### Phase 2: Architecture & Training
*   Update PyTorch `ModelFactory`: Change final linear layer to `out_features=1` (without Sigmoid activation).
*   Update `ProductionTrainingRunner`: Swap `BCELoss` for `MSELoss` or `HuberLoss`.
*   Replace classification metrics (Accuracy, ROC-AUC, F1) with regression metrics (RMSE, MAE, R², Spearman Rank Correlation) in the `MetricsTracker`.
*   Generate new dataset and train regression baseline.

### Phase 3: Inference & API Migration
*   Update `InferenceEngine`: Remove `calibrator` and probability extraction (as regression outputs raw values).
*   Update `VisionPredictionResponse` schema in the backend to accept numeric return forecasts alongside a discrete `signal`.
*   Implement `prediction_controller.py` business logic: map continuous return forecasts to `BUY/HOLD/SELL` based on hardcoded or ATR-based thresholds before returning to the frontend.

---
### Architecture Diagram (Text)

```text
[ Raw OHLCV ] -> (Feature Generator) -> [ Engineered Features ]
                                               |
                                               v
[ 5-Day Log Return (Float) ] <------- (Tensor Builder) -------> [ Sequence Windows (48d) ]
                                                                      |
                                                                      v
                                                              [ GRU / LSTM Core ]
                                                                      |
                                                                      v
                                                            [ Linear(out_features=1) ]
                                                                      |
                                                                      v
                                                      [ Expected 5-Day Log Return (e.g. +0.032) ]
                                                                      |
                                                                      v
                                                      [ Backend Decision Engine (Thresholds) ]
                                                                      |
                                                                      v
                                                    [ Frontend: "BUY (+3.2% Expected)" ]
```
