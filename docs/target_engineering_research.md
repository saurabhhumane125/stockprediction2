# Milestone M11: Production Target Engineering Research

## 1. Current Target Generation Implementation

Based on a strict audit of the repository architecture, the current prediction target is generated as follows:

*   **Location**: `ml_engine/data/tensors/utils.py` -> `add_target_column()`
*   **Logic**: 
    ```python
    future_return = df["close"].pct_change(periods=1).shift(-1)
    df["target"] = (df["future_return"] > (training_config.RETURN_THRESHOLD_BPS / 10000.0)).astype(int)
    ```
*   **Formulation**: The model predicts the **next day's direction** (binary classification). It calculates the 1-day percentage return of the closing price.
*   **Threshold**: The `RETURN_THRESHOLD_BPS` is currently set to `0.0` in `training_config.py`.
*   **Target Classes**: 
    *   `1` ("UP") if the next day's close is strictly greater than today's close.
    *   `0` ("DOWN") if the next day's close is less than or equal to today's close.
*   **Hidden Preprocessing**: The only preprocessing applied to the target is the removal of the final row (`df.dropna(subset=["future_return"])`) since the future return cannot be calculated for the last available day.

---

## 2. Statistical Suitability of the Current Target

The current target (binary classification at a 0.0 threshold) is **statistically unsuitable** for robust financial machine learning.

*   **Label Noise**: At a threshold of exactly 0.0, a return of +0.01% is labeled as "UP" and -0.01% is labeled as "DOWN". In financial markets, such microscopic movements are statistically indistinguishable from zero (pure market noise/microstructure friction). The model is forced to find deterministic patterns in random noise, leading to catastrophic overfitting or random-guess convergence.
*   **Market Randomness**: The Efficient Market Hypothesis dictates that daily price returns are heavily dominated by a random walk. By forcing every single day into a strict UP/DOWN binary, the model is penalized for failing to predict the outcome of a coin flip on flat days.
*   **Class Separability**: Because +0.01% and -0.01% days share virtually identical feature profiles, the decision boundary runs straight through the densest, most inseparable cluster of data points.
*   **Expected Upper Bound**: Even institutional quantitative models rarely exceed 53-55% directional accuracy on daily equities. When transaction costs (slippage, commissions) are factored in, a 52% accurate binary model will still lose money.

---

## 3. Production Trading Targets Comparison

| Approach | Formulation | Advantages | Disadvantages | Production Complexity | Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Binary Direction** | `return > 0` | Simple loss function, easy to evaluate | Extreme label noise at origin | Low | Low (Current state) |
| **B. 3-Class (BUY/HOLD/SELL)** | `+1 (BUY)`, `0 (HOLD)`, `-1 (SELL)` | Ignores noisy flat days | Class imbalance (HOLD often dominates) | Medium (Softmax out) | **High** |
| **C. Regression** | Predict exact % return | Theoretically maximum information | MSE loss is highly sensitive to outliers (black swans) | Medium | Low (Hard to converge) |
| **D. Multi-Horizon** | Predict 1d, 3d, 5d returns | Smooths out daily noise | Requires multi-head architecture | High | Medium |
| **E. Threshold Class.** | `> +2%`, `[-2%, +2%]`, `< -2%` | Highly aligned with real trading goals | Static thresholds fail in changing volatility | Medium | Medium |
| **F. ATR-Adjusted** | `return / ATR > X` | Adapts to individual stock volatility | Requires ATR feature generation for targets | Medium | **High** |
| **G. Volatility-Adjusted** | `return / rolling_std` (Z-score) | Normalizes returns globally | Assumes normal distribution of returns | Medium | High |
| **H. Triple Barrier** | Profit-take, Stop-loss, Time limit | Mimics actual portfolio execution | Extremely complex event-driven labeling | Very High | Low (Overkill for Phase 1) |
| **I. Meta-labeling** | Model 1: Direction. Model 2: Size. | High precision, low false positives | Requires training two sequential models | High | Medium |

---

## 4. Project Objectives Analysis

Based on the existing repository architecture:
*   **Data Interval**: `interval="1d"` (Daily OHLCV).
*   **Pipeline Focus**: `FORECAST_HORIZON=1` (Next-day prediction).
*   **Frontend/Backend**: The architecture exposes a simplified, retail-friendly dashboard expecting discrete directional signals (`VisionPredictionResponse(prediction="UP" | "DOWN")`).

**Conclusion**: The project is designed as a **Swing Trading** / **Short-Term Tactical** platform. 
*   It cannot be intraday because it relies on End-of-Day (EOD) data.
*   It is not long-term investing because the forecast horizon is strictly 1 day, prioritizing short-term momentum and price action over fundamental valuation.

---

## 5. Recommendation: The 3-Class Threshold Target

I recommend migrating the project to a **3-Class Threshold-based Classification Target (BUY, HOLD, SELL)** with a configurable deadband (e.g., `RETURN_THRESHOLD_BPS = 50` which equates to 0.5%).

*   **Why**: It elegantly solves the label noise problem. Returns between -0.5% and +0.5% are mapped to "HOLD" (Class 1). Returns > +0.5% are "BUY" (Class 2), and < -0.5% are "SELL" (Class 0). The model is no longer penalized for failing to guess the direction of flat, noisy days.
*   **Expected Benefits**: Drastic improvement in precision for the BUY and SELL classes. The model will only signal when it detects high-probability momentum that exceeds transaction costs.
*   **Expected Risks**: Class imbalance. The "HOLD" class will likely encompass 50-60% of the dataset, requiring class weighting during training.
*   **Required Code Changes**:
    *   **Data**: `utils.py` needs to use `pd.cut` or `np.select` to map continuous returns to 3 bins.
    *   **Architecture**: Output layer of GRU/LSTM must change from `out_features=1` (Sigmoid) to `out_features=3` (Softmax). Loss function must change from `BCELoss` to `CrossEntropyLoss`.
    *   **Backend**: `prediction_controller` must map output logits to `["SELL", "HOLD", "BUY"]`.
    *   **Frontend**: The UI must be updated to render a neutral "HOLD" badge (e.g., gray or yellow) in `StockCard.tsx`.
*   **Retraining**: **Mandatory**. A new dataset version (e.g., `v3.0`) must be generated, and all models must be retrained from scratch.

---

## 6. Migration Plan Roadmap (No Code Execution)

### Phase 1: Data & Modeling Upgrades
1. Update `TrainingConfig` with `TARGET_CLASSES = 3` and `RETURN_THRESHOLD_BPS = 50` (0.5%).
2. Modify `add_target_column()` in `tensors/utils.py` to bucket future returns into 0 (SELL), 1 (HOLD), and 2 (BUY).
3. Update `TensorBuilder` to serialize 3-class targets.
4. Modify `ModelFactory` to dynamically adjust the final fully-connected layer to `out_features=3`.
5. Update `ProductionTrainingRunner` to utilize `nn.CrossEntropyLoss()` and compute multi-class metrics (Macro F1).

### Phase 2: Pipeline & Inference Integration
1. Generate dataset `NIFTY50/v3.0`.
2. Train new baseline models and save artifacts.
3. Update `InferenceEngine` to apply `softmax` instead of `sigmoid` and return the `argmax` class mapped to string literals (`SELL`, `HOLD`, `BUY`).

### Phase 3: Backend & Frontend API Updates
1. Update `VisionPredictionResponse` schema in the backend to accept `"HOLD"`.
2. Update the frontend TypeScript types in the UI repository.
3. Add a "HOLD" visual state (CSS/Tailwind) to the `StockCard` and Dashboard prediction history components.
