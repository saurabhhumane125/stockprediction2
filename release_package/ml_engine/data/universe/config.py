"""
ml_engine/data/universe/config.py
─────────────────────────────────────────────────────────────────────────────
Configuration-driven dataset universe definitions.
─────────────────────────────────────────────────────────────────────────────
"""
from typing import Dict, List


class UniverseConfig:
    """
    Defines versioned ticker universes for dataset expansion.
    Using .NS suffix for NSE India stocks.
    """
    
    UNIVERSES: Dict[str, List[str]] = {
        "CORE": [
            "RELIANCE.NS",
            "TCS.NS",
            "HDFCBANK.NS",
            "INFY.NS",
            "ICICIBANK.NS"
        ],
        "NIFTY50": [
            "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
            "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
            "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
            "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
            "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
            "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
            "LTIM.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
            "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS",
            "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS",
            "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "WIPRO.NS"
        ]
        # Extensible to NIFTY100, NIFTY200, NIFTY500
    }
