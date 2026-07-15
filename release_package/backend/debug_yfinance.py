import sys
from pathlib import Path

# Add backend directory to path so we can import ml_engine
root_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(root_dir))

from ml_engine.data.download.yfinance_downloader import YFinanceDownloader

def run_debug():
    print("="*50)
    print("YFINANCE DOWNLOADER DEBUG SCRIPT")
    print("="*50)
    
    downloader = YFinanceDownloader()
    
    # EXACT parameters from the failed log
    ticker = "RELIANCE.NS"
    start_date = "2026-07-04"
    end_date = "2026-07-13"
    interval = "15m"
    
    print("EXACT yfinance.download() arguments:")
    print(f"ticker: {ticker}")
    print(f"start: {start_date}")
    print(f"end: {end_date}")
    print(f"interval: {interval}")
    print(f"auto_adjust: True (forced by downloader)")
    print(f"actions: True (forced by downloader)")
    print(f"timeout: {downloader.timeout}")
    print("-" * 50)
    
    try:
        df = downloader.download(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        if df.empty:
            print("1) Does it return data? NO")
            print("2) Dataframe shape: (0, 0)")
        else:
            print("1) Does it return data? YES")
            print(f"2) Dataframe shape: {df.shape}")
            print("Columns:", list(df.columns))
            print(df.head())
    except Exception as e:
        print("1) Does it return data? NO")
        print("Exception:", str(e))
        
    print("="*50)
    import yfinance as yf
    print("Direct YFinance Test:")
    try:
        t = yf.Ticker(ticker)
        print("Checking recent 15m data without date limits:")
        recent = t.history(period="5d", interval="15m")
        print(f"Recent data shape: {recent.shape}")
        if not recent.empty:
            print(f"Earliest date in recent: {recent.index.min()}")
            print(f"Latest date in recent: {recent.index.max()}")
    except Exception as e:
        print("Direct test exception:", e)

if __name__ == "__main__":
    run_debug()
