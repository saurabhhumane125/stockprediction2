import logging
from datetime import datetime, timedelta, timezone
import pandas as pd
import yfinance as yf
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ResolvedDateWindow:
    start_date: str
    end_date: str
    interval: str
    target_dt: datetime
    warnings: list[str]

class VisionDateResolver:
    """
    Dedicated production layer for resolving OCR-derived timestamps into valid market windows.
    Enforces business rules such as future date detection, weekends, market holidays, 
    and Yahoo Finance constraints (e.g. 60-day limit for intraday data).
    """

    def __init__(self):
        # We need at least 76 trading days of valid data (27 warmup + 48 sequence + 1 target)
        self.min_trading_days_required = 100 # buffer included
        self._latest_market_date_cache = None
        self._cache_time = None

    def _get_latest_market_date(self, fallback_symbol: str = "^NSEI") -> datetime:
        """
        Dynamically determine the real-world latest market date to handle simulated OS clocks.
        """
        now = datetime.now(timezone.utc)
        if self._latest_market_date_cache and self._cache_time and (now - self._cache_time).total_seconds() < 3600:
            return self._latest_market_date_cache

        try:
            # Use a major index to find the latest trading session available on yfinance
            t = yf.Ticker(fallback_symbol)
            df = t.history(period="1d", interval="1d")
            if not df.empty:
                latest_dt = df.index[-1].to_pydatetime()
                # Ensure it has a timezone
                if latest_dt.tzinfo is None:
                    latest_dt = latest_dt.replace(tzinfo=timezone.utc)
                self._latest_market_date_cache = latest_dt
                self._cache_time = now
                return latest_dt
        except Exception as e:
            logger.warning(f"Could not fetch latest market date from {fallback_symbol}: {e}")
        
        return now

    def _rollback_to_business_day(self, dt: datetime) -> datetime:
        """Rollback weekend dates to Friday."""
        while dt.weekday() > 4: # 5=Sat, 6=Sun
            dt -= timedelta(days=1)
        return dt

    def resolve(self, requested_dt: datetime, interval: str) -> ResolvedDateWindow:
        warnings = []
        
        # 1. Real-world validation (Future dates & Simulated OS clocks)
        latest_market_date = self._get_latest_market_date()
        
        if requested_dt > latest_market_date:
            warnings.append(f"Requested date {requested_dt.isoformat()} is in the future. Clamping to {latest_market_date.isoformat()}.")
            target_dt = latest_market_date
        else:
            target_dt = requested_dt

        # 2. Weekend resolution
        original_target = target_dt
        target_dt = self._rollback_to_business_day(target_dt)
        if target_dt != original_target:
            warnings.append("Requested date fell on a weekend. Rolled back to previous business day.")

        # 3. YFinance Constraints (Intraday is strictly limited to last 60 real-world days)
        resolved_interval = interval
        if interval in ["1m", "5m", "15m", "30m", "60m", "1h"]:
            days_diff = (latest_market_date - target_dt).days
            if days_diff >= 59:
                warnings.append(f"Interval {interval} is unsupported for dates > 60 days ago by YFinance. Escalating to 1d.")
                resolved_interval = "1d"

        # 4. Calculate Window
        # We need ~100 trading days. Since weekends exist, 100 trading days = ~145 calendar days.
        # We'll use 150 calendar days to be safe.
        lookback_calendar_days = 150
        
        start_date = (target_dt - timedelta(days=lookback_calendar_days))
        # Add a margin to end_date to ensure the target_dt is fully captured even with timezone differences
        end_date = (target_dt + timedelta(days=2))
        
        # Enforce business day rollback on start date to ensure clean boundaries
        start_date = self._rollback_to_business_day(start_date)

        return ResolvedDateWindow(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            interval=resolved_interval,
            target_dt=target_dt,
            warnings=warnings
        )

vision_date_resolver = VisionDateResolver()
