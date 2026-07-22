# Production Dataset Timeline Audit

This document contains a diagnostic audit of the current production dataset based on the downloaded `.parquet` files for the NIFTY50 universe.

## Global Dataset Summary
- **Number of unique stocks:** 50
- **Global earliest date:** 2018-02-06
- **Global latest date:** 2026-06-18
- **Latest market data included?**: **No**. The latest date in the dataset is 2026-06-18, which is over a month behind the current date.
- **Yahoo Finance Interval:** `1d` (Daily)
- **Adjusted Prices:** Yes. (`auto_adjust=True` is explicitly passed in `YFinanceDownloader.download`).
- **Dividends & Splits:** Yes. (`actions=True` is explicitly passed in `YFinanceDownloader.download` and mapped to `dividends` and `stock_splits` columns).

## Timeline Consistency and Gaps
- **Identical Date Ranges:** **No**. While 47 out of 50 stocks begin on `2018-02-06`, three recently listed stocks begin later (`JIOFIN.NS`, `MAXHEALTH.NS`, `ETERNAL.NS`). All stocks end on the identical date of `2026-06-18`.
- **Missing Periods:** The dataset contains roughly 2066 trading days over an 8-year span, which correctly corresponds to ~250 trading days per year. `INDIGO.NS` has 2065 trading days, suggesting a single missing/suspended day compared to the others.
- **Insufficient History:** **None**. The minimum history is `JIOFIN.NS` at 674 days, which is well above the 48-step sequence generation threshold.

## Stock Timeline Summary Table

| Stock | Start | End | Trading Days |
| :--- | :--- | :--- | :--- |
| ADANIENT.NS | 2018-02-06 | 2026-06-18 | 2066 |
| ADANIPORTS.NS | 2018-02-06 | 2026-06-18 | 2066 |
| APOLLOHOSP.NS | 2018-02-06 | 2026-06-18 | 2066 |
| ASIANPAINT.NS | 2018-02-06 | 2026-06-18 | 2066 |
| AXISBANK.NS | 2018-02-06 | 2026-06-18 | 2066 |
| BAJAJ-AUTO.NS | 2018-02-06 | 2026-06-18 | 2066 |
| BAJAJFINSV.NS | 2018-02-06 | 2026-06-18 | 2066 |
| BAJFINANCE.NS | 2018-02-06 | 2026-06-18 | 2066 |
| BEL.NS | 2018-02-06 | 2026-06-18 | 2066 |
| BHARTIARTL.NS | 2018-02-06 | 2026-06-18 | 2066 |
| CIPLA.NS | 2018-02-06 | 2026-06-18 | 2066 |
| COALINDIA.NS | 2018-02-06 | 2026-06-18 | 2066 |
| DRREDDY.NS | 2018-02-06 | 2026-06-18 | 2066 |
| EICHERMOT.NS | 2018-02-06 | 2026-06-18 | 2066 |
| ETERNAL.NS | 2021-08-30 | 2026-06-18 | 1188 |
| GRASIM.NS | 2018-02-06 | 2026-06-18 | 2066 |
| HCLTECH.NS | 2018-02-06 | 2026-06-18 | 2066 |
| HDFCBANK.NS | 2018-02-06 | 2026-06-18 | 2066 |
| HDFCLIFE.NS | 2018-02-06 | 2026-06-18 | 2066 |
| HINDALCO.NS | 2018-02-06 | 2026-06-18 | 2066 |
| HINDUNILVR.NS | 2018-02-06 | 2026-06-18 | 2066 |
| ICICIBANK.NS | 2018-02-06 | 2026-06-18 | 2066 |
| INDIGO.NS | 2018-02-06 | 2026-06-18 | 2065 |
| INFY.NS | 2018-02-06 | 2026-06-18 | 2066 |
| ITC.NS | 2018-02-06 | 2026-06-18 | 2066 |
| JIOFIN.NS | 2023-09-26 | 2026-06-18 | 674 |
| JSWSTEEL.NS | 2018-02-06 | 2026-06-18 | 2066 |
| KOTAKBANK.NS | 2018-02-06 | 2026-06-18 | 2066 |
| LT.NS | 2018-02-06 | 2026-06-18 | 2066 |
| M&M.NS | 2018-02-06 | 2026-06-18 | 2066 |
| MARUTI.NS | 2018-02-06 | 2026-06-18 | 2066 |
| MAXHEALTH.NS | 2020-09-27 | 2026-06-18 | 1418 |
| NESTLEIND.NS | 2018-02-06 | 2026-06-18 | 2066 |
| NTPC.NS | 2018-02-06 | 2026-06-18 | 2066 |
| ONGC.NS | 2018-02-06 | 2026-06-18 | 2066 |
| POWERGRID.NS | 2018-02-06 | 2026-06-18 | 2066 |
| RELIANCE.NS | 2018-02-06 | 2026-06-18 | 2066 |
| SBILIFE.NS | 2018-02-06 | 2026-06-18 | 2066 |
| SBIN.NS | 2018-02-06 | 2026-06-18 | 2066 |
| SHRIRAMFIN.NS | 2018-02-06 | 2026-06-18 | 2066 |
| SUNPHARMA.NS | 2018-02-06 | 2026-06-18 | 2066 |
| TATACONSUM.NS | 2018-02-06 | 2026-06-18 | 2066 |
| TATASTEEL.NS | 2018-02-06 | 2026-06-18 | 2066 |
| TCS.NS | 2018-02-06 | 2026-06-18 | 2066 |
| TECHM.NS | 2018-02-06 | 2026-06-18 | 2066 |
| TITAN.NS | 2018-02-06 | 2026-06-18 | 2066 |
| TMPV.NS | 2018-02-06 | 2026-06-18 | 2066 |
| TRENT.NS | 2018-02-06 | 2026-06-18 | 2066 |
| ULTRACEMCO.NS | 2018-02-06 | 2026-06-18 | 2066 |
| WIPRO.NS | 2018-02-06 | 2026-06-18 | 2066 |
