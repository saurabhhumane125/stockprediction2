import json
import os
import logging
from typing import List, Dict, Any

from ml_engine.data.universe.config import UniverseConfig

logger = logging.getLogger(__name__)

class UniverseConfigAdapter:
    """
    Adapter to decouple the backend from ML Engine internal paths and data structures.
    Reads the active ML production model to determine the dataset universe (e.g. NIFTY50),
    and retrieves the canonical metadata (Company Name, Sector) for seeding the DB.
    """

    def __init__(self, registry_base_path: str = "../ml_data/registry"):
        self.registry_base_path = registry_base_path

    def get_active_universe_metadata(self) -> List[Dict[str, str]]:
        """
        1. Reads active_production.json
        2. Resolves manifest.json of the active run
        3. Extracts dataset_version (e.g. NIFTY50/v3.0)
        4. Returns UniverseConfig.UNIVERSE_METADATA["NIFTY50"]
        """
        active_prod_path = os.path.join(self.registry_base_path, "active_production.json")
        if not os.path.exists(active_prod_path):
            logger.warning(f"Active production registry not found at {active_prod_path}. Falling back to CORE.")
            return UniverseConfig.UNIVERSE_METADATA.get("CORE", [])

        try:
            with open(active_prod_path, 'r') as f:
                active_data = json.load(f)
            
            active_version = active_data.get("active_version")
            if not active_version:
                logger.warning("No active_version in active_production.json. Falling back to CORE.")
                return UniverseConfig.UNIVERSE_METADATA.get("CORE", [])
                
            manifest_path = os.path.join(self.registry_base_path, "production", active_version, "manifest.json")
            if not os.path.exists(manifest_path):
                logger.warning(f"Manifest not found at {manifest_path}. Falling back to CORE.")
                return UniverseConfig.UNIVERSE_METADATA.get("CORE", [])
                
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
                
            dataset_version = manifest_data.get("dataset_version", "")
            if not dataset_version:
                logger.warning("No dataset_version in manifest.json. Falling back to CORE.")
                return UniverseConfig.UNIVERSE_METADATA.get("CORE", [])
                
            # dataset_version is typically "NIFTY50/v3.0"
            universe_name = dataset_version.split("/")[0]
            
            metadata = UniverseConfig.UNIVERSE_METADATA.get(universe_name)
            if not metadata:
                logger.warning(f"Universe metadata for '{universe_name}' not found. Falling back to CORE.")
                return UniverseConfig.UNIVERSE_METADATA.get("CORE", [])
                
            logger.info(f"[UniverseAdapter] Successfully resolved active universe: {universe_name} ({len(metadata)} stocks)")
            return metadata
            
        except Exception as e:
            logger.error(f"Error reading universe metadata: {e}. Falling back to CORE.")
            return UniverseConfig.UNIVERSE_METADATA.get("CORE", [])

universe_adapter = UniverseConfigAdapter()
