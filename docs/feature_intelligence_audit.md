# Production Feature Intelligence Audit

This document contains a comprehensive diagnostic audit of the feature engineering pipeline based on the `train.pt` dataset tensor (`NIFTY50/v2.0`).

## 1. Features Currently Engineered & Used
The pipeline currently generates and utilizes **23 features**:
`open`, `high`, `low`, `close`, `volume`, `dividends`, `stock_splits`, `daily_return`, `ema_short`, `ema_long`, `rsi`, `macd_line`, `macd_signal`, `macd_histogram`, `bb_upper`, `bb_lower`, `bb_width`, `atr`, `adx`, `roc`, `momentum`, `volatility`, `volume_change`.

## 2. Near-Zero Variance Features
**None.** All features pass the minimum variance threshold (`> 1e-4`) after standard scaling.

## 3. Highly Correlated Feature Pairs (Multicollinearity)
The dataset suffers from **extreme multicollinearity**. The following pairs exhibit absolute Pearson correlation `|r| > 0.90`:
- **Price components**: `close <-> high` (0.9999), `low <-> open` (0.9999), `close <-> low` (0.9999), `high <-> open` (0.9999).
- **Moving Averages & Price**: `ema_long <-> ema_short` (0.9992), `ema_short <-> open/high/low/close` (~0.9989).
- **Bollinger Bands**: `bb_upper <-> ema_short` (0.9991), `bb_lower <-> ema_short` (0.9988), `bb_lower <-> bb_upper` (0.9961).
- **MACD**: `macd_signal <-> macd_line` (0.9537).
- **Volatility**: `atr <-> bb_upper` (0.9076).

## 4. Features Likely Adding Noise
- **`dividends` and `stock_splits`**: Both have Mutual Information of `0.0000` and Permutation Importance of `~0.0000`. Because they are sparse (mostly zeros), they provide virtually zero predictive signal for next-day direction and only act as noise.
- **Redundant Price/MA Variables**: Passing `open`, `high`, `low`, `close`, `ema_short`, `ema_long`, `bb_upper`, and `bb_lower` simultaneously into the model injects highly redundant information. The model is forced to distribute weights across 8 nearly identical signals, leading to overfitting and gradient dilution.

## 5. Missing Technical/Market Features
To materially improve prediction accuracy, the following families of features are missing:
1. **Broader Market Context**: E.g., NIFTY50 Index daily return, India VIX (Volatility). Currently, the model has no awareness of macro market conditions.
2. **Volume-Price Indicators**: `VWAP` (Volume Weighted Average Price), `OBV` (On-Balance Volume), or `Chaikin Money Flow`. Current volume features are isolated from price direction.
3. **Advanced Momentum/Oscillators**: `Stochastic Oscillator` or `Williams %R` to capture overbought/oversold extremes better than raw RSI.
4. **Historical Lags**: Explicit lagged returns (e.g., `return_lag_1`, `return_lag_3`) to help the GRU capture immediate auto-regressive properties without relying purely on hidden state.

## 6. Ranked Feature Usefulness (Signal Strength)
Ranked from most to least useful based on a combination of **Permutation Importance** (Random Forest Baseline) and **Mutual Information (MI)** scores against the target.

| Rank | Feature | Permutation Importance | MI Score | Assessment |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `daily_return` | 0.0163 | 0.0057 | **Strong Signal**. Best direct predictor of subsequent direction. |
| 2 | `adx` | 0.0135 | 0.0000 | **Strong Signal**. Trend strength helps contextualize returns. |
| 3 | `volatility` | 0.0089 | 0.0047 | **Strong Signal**. Critical for normalized price action. |
| 4 | `volume_change` | 0.0109 | 0.0000 | **Moderate Signal**. Captures sudden institutional interest. |
| 5 | `atr` | 0.0112 | 0.0000 | **Moderate Signal**. Absolute volatility measure. |
| 6 | `volume` | 0.0099 | 0.0017 | **Moderate Signal**. |
| 7 | `bb_lower` | 0.0094 | 0.0024 | **Moderate Signal**. Captures oversold bounces. |
| 8 | `momentum` | 0.0092 | 0.0000 | **Moderate Signal**. |
| 9 | `bb_width` | 0.0087 | 0.0016 | **Moderate Signal**. Volatility squeeze proxy. |
| 10 | `macd_histogram` | 0.0050 | 0.0040 | **Moderate Signal**. Momentum derivative. |
| 11 | `open` | 0.0081 | 0.0000 | **Weak Signal**. Redundant with close/high/low. |
| 12 | `close` | 0.0069 | 0.0022 | **Weak Signal**. Redundant. |
| 13 | `rsi` | 0.0067 | 0.0001 | **Weak Signal**. Often stays pinned in trends. |
| 14 | `bb_upper` | 0.0065 | 0.0000 | **Weak Signal**. Redundant. |
| 15 | `ema_long` | 0.0061 | 0.0000 | **Weak Signal**. Redundant. |
| 16 | `ema_short` | 0.0057 | 0.0000 | **Weak Signal**. Redundant. |
| 17 | `macd_signal` | 0.0050 | 0.0000 | **Weak Signal**. |
| 18 | `roc` | 0.0049 | 0.0015 | **Weak Signal**. |
| 19 | `high` | 0.0045 | 0.0000 | **Weak Signal**. Redundant. |
| 20 | `low` | 0.0095 | 0.0000 | **Weak Signal**. Redundant. |
| 21 | `macd_line` | 0.0033 | 0.0000 | **Weak Signal**. |
| 22 | `dividends` | 0.0001 | 0.0000 | **Noise**. Too sparse. |
| 23 | `stock_splits` | 0.0000 | 0.0000 | **Noise**. Too sparse. |

## 7. Statistical Distribution (Last Timestep, Standard Scaled)
| Feature | mean | std | min | 50% (Median) | max |
| :--- | :--- | :--- | :--- | :--- | :--- |
| open | 0.0067 | 0.9980 | -0.7146 | -0.3062 | 6.5193 |
| close | 0.0067 | 0.9980 | -0.7148 | -0.3060 | 6.5142 |
| volume | 0.0101 | 1.0156 | -0.4778 | -0.2987 | 23.4455 |
| dividends | 0.0013 | 1.0243 | -0.0332 | -0.0332 | 108.8894 |
| daily_return | 0.0006 | 1.0106 | -12.4728 | -0.0249 | 12.1439 |
| rsi | 0.0137 | 1.0021 | -3.0174 | 0.0255 | 2.8072 |
*(Note: Full distributional data is available in the diagnostic logs. All features are roughly mean=0, std=1 as expected from StandardScaler, though long tails exist on volume and returns).*
