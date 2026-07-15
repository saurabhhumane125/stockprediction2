"""
ml_engine/data/universe/manager.py
─────────────────────────────────────────────────────────────────────────────
Manages retrieval and resolution of dataset universes.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
from typing import List

from ml_engine.data.universe.config import UniverseConfig

logger = logging.getLogger(__name__)


class UniverseManager:
    """
    Manages configured trading universes for dataset expansion.
    """
    
    @classmethod
    def get_universe(cls, name: str) -> List[str]:
        """
        Retrieve a list of tickers for a given universe name.
        """
        name_upper = name.upper()
        if name_upper not in UniverseConfig.UNIVERSES:
            raise ValueError(f"Universe '{name}' not found. Available: {list(UniverseConfig.UNIVERSES.keys())}")
            
        tickers = UniverseConfig.UNIVERSES[name_upper]
        # Ensure uniqueness and sorted order
        tickers = sorted(list(set(tickers)))
        
        logger.info(f"[UniverseManager] Loaded universe '{name_upper}' with {len(tickers)} tickers.")
        return tickers
