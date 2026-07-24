import logging
import hashlib
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np

from app.schemas import VisionSession, VisionFeatureSet, FeatureProvenance
from app.services.vision.provider_registry import provider_registry
from ml_engine.data.features.generator import FeatureGenerator
from ml_engine.config.training_config import training_config

logger = logging.getLogger(__name__)

class VisionFeaturePipeline:
    def __init__(self):
        self.feature_generator = FeatureGenerator()
        self.sequence_length = training_config.SEQUENCE_LENGTH
        # Dynamically calculate lookback to ensure sequence length and max moving averages are covered
        self.lookback_days = self.sequence_length + 102
        
    def _calculate_hash(self, array: np.ndarray) -> str:
        return hashlib.sha256(array.tobytes()).hexdigest()

    def process(self, session: VisionSession) -> VisionFeatureSet:
        if not session.resolved_ohlc:
            return VisionFeatureSet(
                session_id=session.request_id,
                features=[],
                feature_names=[],
                feature_hash="",
                provenance=[],
                is_valid=False,
                warnings=["Cannot process feature pipeline: VisionSession has no resolved_ohlc."]
            )

        from app.services.vision.date_resolver import vision_date_resolver
        
        provider_name = session.provider_used or provider_registry.get_default_provider_name()
        provider = provider_registry.get_provider(provider_name)

        raw_target_dt = pd.to_datetime(session.resolved_ohlc.timestamp).to_pydatetime()
        if raw_target_dt.tzinfo is None:
            raw_target_dt = raw_target_dt.replace(tzinfo=timezone.utc)
            
        interval = session.ocr_metadata.timeframe.value if session.ocr_metadata.timeframe and session.ocr_metadata.timeframe.value else "1d"
        
        # Use single source of truth for date resolution
        date_window = vision_date_resolver.resolve(raw_target_dt, interval)
        target_dt = date_window.target_dt.replace(tzinfo=None)

        try:
            df = provider.download(
                session.ocr_metadata.symbol.value, 
                start_date=date_window.start_date, 
                end_date=date_window.end_date, 
                interval=date_window.interval
            )
            
            # Fetch benchmark market data using identical date resolution
            market_data = {}
            for benchmark in ["^NSEI", "^INDIAVIX"]:
                market_data[benchmark] = provider.download(
                    benchmark,
                    start_date=date_window.start_date,
                    end_date=date_window.end_date,
                    interval=date_window.interval
                )
        except Exception as e:
            logger.error(f"Provider failure during feature generation: {e}")
            return VisionFeatureSet(
                session_id=session.request_id,
                features=[],
                feature_names=[],
                feature_hash="",
                provenance=[],
                is_valid=False,
                warnings=[f"Provider failure: {e}"]
            )

        if df.empty or market_data["^NSEI"].empty or market_data["^INDIAVIX"].empty:
            return VisionFeatureSet(
                session_id=session.request_id,
                features=[],
                feature_names=[],
                feature_hash="",
                provenance=[],
                is_valid=False,
                warnings=["Provider returned empty dataset for the requested window or benchmark."]
            )

        # Truncate at exact target_dt to simulate what the model would see at that exact moment
        df = df[df.index <= target_dt]
        market_data["^NSEI"] = market_data["^NSEI"][market_data["^NSEI"].index <= target_dt]
        market_data["^INDIAVIX"] = market_data["^INDIAVIX"][market_data["^INDIAVIX"].index <= target_dt]

        # Generate all features using the single source of truth
        df_features = self.feature_generator.generate_all_features(df, market_data=market_data)
        
        # Ensure target_dt actually exists in the truncated dataframe
        if target_dt not in df_features.index:
            return VisionFeatureSet(
                session_id=session.request_id,
                features=[],
                feature_names=[],
                feature_hash="",
                provenance=[],
                is_valid=False,
                warnings=[f"Target timestamp {target_dt} was lost after feature generation lookbacks (needs more history)."]
            )
            
        # We need EXACTLY `SEQUENCE_LENGTH + 1` rows to produce a sequence of length `SEQUENCE_LENGTH` via SequenceBuilder 
        required_rows = self.sequence_length + 1
        if len(df_features) < required_rows:
            return VisionFeatureSet(
                session_id=session.request_id,
                features=[],
                feature_names=[],
                feature_hash="",
                provenance=[],
                is_valid=False,
                warnings=[f"Insufficient rows for sequence. Need {required_rows}, got {len(df_features)}."]
            )
            
        # Extract the last `required_rows`
        df_final = df_features.iloc[-required_rows:]
        
        # We exclude 'target' and 'ticker' because 'ticker' is a string which breaks np.isnan
        feature_cols = [c for c in df_final.columns if c not in ["target", "ticker"]]
        feature_matrix = df_final[feature_cols].astype(float).values
        
        # NaN check
        if np.isnan(feature_matrix).any():
            return VisionFeatureSet(
                session_id=session.request_id,
                features=[],
                feature_names=feature_cols,
                feature_hash="",
                provenance=[],
                is_valid=False,
                warnings=["NaNs detected in the final feature matrix."]
            )

        feature_hash = self._calculate_hash(feature_matrix)
        
        provenance = []
        gen_time = datetime.utcnow().isoformat()
        
        for meta in self.feature_generator.metadata:
            if meta["feature_name"] in feature_cols:
                provenance.append(FeatureProvenance(
                    feature_name=meta["feature_name"],
                    origin="ml_engine.FeatureGenerator",
                    calculation_version="v1",
                    lookback_window=self.lookback_days,
                    provider=provider_name,
                    generation_timestamp=gen_time,
                    validation_status="Valid"
                ))
        
        # Attach pipeline metadata to the first provenance record if available
        if provenance:
            provenance[0].origin = f"{provenance[0].origin} (Pipeline v1, SeqBuilder v1, Hash SHA-256)"

        # Also add provenance for base OHLCV if desired, but we'll stick to generated features per instructions
        # Or we can just let it be.
        
        return VisionFeatureSet(
            session_id=session.request_id,
            features=feature_matrix.tolist(),
            feature_names=feature_cols,
            feature_hash=feature_hash,
            provenance=provenance,
            is_valid=True,
            warnings=[]
        )

feature_pipeline = VisionFeaturePipeline()
