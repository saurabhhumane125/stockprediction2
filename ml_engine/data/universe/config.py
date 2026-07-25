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
    
    UNIVERSE_METADATA: Dict[str, List[Dict[str, str]]] = {
        "CORE": [
            {"symbol": "RELIANCE", "exchange": "NSE", "company_name": "Reliance Industries Ltd", "sector": "Energy"},
            {"symbol": "TCS", "exchange": "NSE", "company_name": "Tata Consultancy Services", "sector": "Technology"},
            {"symbol": "HDFCBANK", "exchange": "NSE", "company_name": "HDFC Bank Ltd", "sector": "Financial Services"},
            {"symbol": "INFY", "exchange": "NSE", "company_name": "Infosys Limited", "sector": "Technology"},
            {"symbol": "ICICIBANK", "exchange": "NSE", "company_name": "ICICI Bank Ltd.", "sector": "Financial Services"}
        ],
        "NIFTY50": [
            {"symbol": "ADANIENT", "exchange": "NSE", "company_name": "ADANI ENTERPRISES LIMITED", "sector": "Energy"},
            {"symbol": "ADANIPORTS", "exchange": "NSE", "company_name": "ADANI PORT & SEZ LTD", "sector": "Industrials"},
            {"symbol": "APOLLOHOSP", "exchange": "NSE", "company_name": "APOLLO HOSPITALS ENTER. L", "sector": "Healthcare"},
            {"symbol": "ASIANPAINT", "exchange": "NSE", "company_name": "ASIAN PAINTS LIMITED", "sector": "Basic Materials"},
            {"symbol": "AXISBANK", "exchange": "NSE", "company_name": "AXIS BANK LIMITED", "sector": "Financial Services"},
            {"symbol": "BAJAJ-AUTO", "exchange": "NSE", "company_name": "BAJAJ AUTO LIMITED", "sector": "Consumer Cyclical"},
            {"symbol": "BAJFINANCE", "exchange": "NSE", "company_name": "BAJAJ FINANCE LIMITED", "sector": "Financial Services"},
            {"symbol": "BAJAJFINSV", "exchange": "NSE", "company_name": "BAJAJ FINSERV LTD.", "sector": "Financial Services"},
            {"symbol": "BPCL", "exchange": "NSE", "company_name": "BHARAT PETROLEUM CORP  LT", "sector": "Energy"},
            {"symbol": "BHARTIARTL", "exchange": "NSE", "company_name": "BHARTI AIRTEL LIMITED", "sector": "Communication Services"},
            {"symbol": "BRITANNIA", "exchange": "NSE", "company_name": "BRITANNIA INDUSTRIES LTD", "sector": "Consumer Defensive"},
            {"symbol": "CIPLA", "exchange": "NSE", "company_name": "CIPLA LTD", "sector": "Healthcare"},
            {"symbol": "COALINDIA", "exchange": "NSE", "company_name": "COAL INDIA LTD", "sector": "Energy"},
            {"symbol": "DIVISLAB", "exchange": "NSE", "company_name": "DIVI S LABORATORIES LTD", "sector": "Healthcare"},
            {"symbol": "DRREDDY", "exchange": "NSE", "company_name": "DR. REDDY S LABORATORIES", "sector": "Healthcare"},
            {"symbol": "EICHERMOT", "exchange": "NSE", "company_name": "EICHER MOTORS LTD", "sector": "Consumer Cyclical"},
            {"symbol": "GRASIM", "exchange": "NSE", "company_name": "GRASIM INDUSTRIES LTD", "sector": "Basic Materials"},
            {"symbol": "HCLTECH", "exchange": "NSE", "company_name": "HCL TECHNOLOGIES LTD", "sector": "Technology"},
            {"symbol": "HDFCBANK", "exchange": "NSE", "company_name": "HDFC BANK LTD", "sector": "Financial Services"},
            {"symbol": "HDFCLIFE", "exchange": "NSE", "company_name": "HDFC LIFE INS CO LTD", "sector": "Financial Services"},
            {"symbol": "HEROMOTOCO", "exchange": "NSE", "company_name": "HERO MOTOCORP LIMITED", "sector": "Consumer Cyclical"},
            {"symbol": "HINDALCO", "exchange": "NSE", "company_name": "HINDALCO  INDUSTRIES  LTD", "sector": "Basic Materials"},
            {"symbol": "HINDUNILVR", "exchange": "NSE", "company_name": "HINDUSTAN UNILEVER LTD.", "sector": "Consumer Defensive"},
            {"symbol": "ICICIBANK", "exchange": "NSE", "company_name": "ICICI BANK LTD.", "sector": "Financial Services"},
            {"symbol": "ITC", "exchange": "NSE", "company_name": "ITC LTD", "sector": "Consumer Defensive"},
            {"symbol": "INDUSINDBK", "exchange": "NSE", "company_name": "INDUSIND BANK LIMITED", "sector": "Financial Services"},
            {"symbol": "INFY", "exchange": "NSE", "company_name": "INFOSYS LIMITED", "sector": "Technology"},
            {"symbol": "JSWSTEEL", "exchange": "NSE", "company_name": "JSW STEEL LIMITED", "sector": "Basic Materials"},
            {"symbol": "KOTAKBANK", "exchange": "NSE", "company_name": "KOTAK MAHINDRA BANK LTD", "sector": "Financial Services"},
            {"symbol": "LT", "exchange": "NSE", "company_name": "LARSEN & TOUBRO LTD.", "sector": "Industrials"},
            {"symbol": "LTIM", "exchange": "NSE", "company_name": "LTIMindtree Ltd", "sector": "Technology"},
            {"symbol": "M&M", "exchange": "NSE", "company_name": "MAHINDRA & MAHINDRA LTD", "sector": "Consumer Cyclical"},
            {"symbol": "MARUTI", "exchange": "NSE", "company_name": "MARUTI SUZUKI INDIA LTD.", "sector": "Consumer Cyclical"},
            {"symbol": "NTPC", "exchange": "NSE", "company_name": "NTPC LTD", "sector": "Utilities"},
            {"symbol": "NESTLEIND", "exchange": "NSE", "company_name": "NESTLE INDIA LIMITED", "sector": "Consumer Defensive"},
            {"symbol": "ONGC", "exchange": "NSE", "company_name": "OIL AND NATURAL GAS CORP.", "sector": "Energy"},
            {"symbol": "POWERGRID", "exchange": "NSE", "company_name": "POWER GRID CORP. LTD.", "sector": "Utilities"},
            {"symbol": "RELIANCE", "exchange": "NSE", "company_name": "RELIANCE INDUSTRIES LTD", "sector": "Energy"},
            {"symbol": "SBILIFE", "exchange": "NSE", "company_name": "SBI LIFE INSURANCE CO LTD", "sector": "Financial Services"},
            {"symbol": "SBIN", "exchange": "NSE", "company_name": "STATE BANK OF INDIA", "sector": "Financial Services"},
            {"symbol": "SUNPHARMA", "exchange": "NSE", "company_name": "SUN PHARMACEUTICAL IND L", "sector": "Healthcare"},
            {"symbol": "TCS", "exchange": "NSE", "company_name": "TATA CONSULTANCY SERV LT", "sector": "Technology"},
            {"symbol": "TATACONSUM", "exchange": "NSE", "company_name": "TATA CONSUMER PRODUCT LTD", "sector": "Consumer Defensive"},
            {"symbol": "TATAMOTORS", "exchange": "NSE", "company_name": "TATA MOTORS LIMITED", "sector": "Consumer Cyclical"},
            {"symbol": "TATASTEEL", "exchange": "NSE", "company_name": "TATA STEEL LIMITED", "sector": "Basic Materials"},
            {"symbol": "TECHM", "exchange": "NSE", "company_name": "TECH MAHINDRA LIMITED", "sector": "Technology"},
            {"symbol": "TITAN", "exchange": "NSE", "company_name": "TITAN COMPANY LIMITED", "sector": "Consumer Cyclical"},
            {"symbol": "UPL", "exchange": "NSE", "company_name": "UPL LIMITED", "sector": "Basic Materials"},
            {"symbol": "ULTRACEMCO", "exchange": "NSE", "company_name": "ULTRATECH CEMENT LIMITED", "sector": "Basic Materials"},
            {"symbol": "WIPRO", "exchange": "NSE", "company_name": "WIPRO LTD", "sector": "Technology"}
        ]
    }

    UNIVERSES: Dict[str, List[str]] = {
        name: [f"{stock['symbol']}.NS" for stock in meta]
        for name, meta in UNIVERSE_METADATA.items()
    }
