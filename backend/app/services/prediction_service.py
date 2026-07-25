import numpy as np

from app.core.model_loader import artifacts, ml_adapter
from app.utils.preprocessing import preprocessor


class PredictionService:

    def predict(self, stock: str, feature_rows=None, raw_df=None, market_data=None):
        from app.core.logger import logger
        
        latest_features = None
        
        # PROXY: Use ML Engine if available
        if ml_adapter.is_available and ml_adapter.inference_engine is not None:
            engine = ml_adapter.inference_engine
            
            # Determine active version for logging
            version = "unknown"
            if hasattr(engine, 'manifest') and engine.manifest:
                version = engine.manifest.get('version', version)
            elif hasattr(engine, 'version'):
                version = engine.version
            
            logger.info("[PredictionService]")
            logger.info("Routing inference to ProductionInferenceEngine")
            logger.info(f"Active Model: {version}")
            logger.info("Registry State: production")
            
            # Handle Live Feature Preprocessing via ML Engine pipeline
            if raw_df is not None:
                try:
                    from ml_engine.inference.preprocessor import LiveFeaturePipeline
                    pipeline = LiveFeaturePipeline(engine.manifest)
                    feature_array, latest_features = pipeline.process(raw_df, market_data)
                except Exception as e:
                    logger.error(f"LiveFeaturePipeline failed: {e}. Falling back to legacy.")
                    raise RuntimeError(f"Live feature preprocessing failed: {e}")
            elif feature_rows is not None:
                feature_array = np.asarray(feature_rows, dtype=np.float32)
            else:
                raise ValueError("Must provide either feature_rows or raw_df.")
            
            try:
                results = engine.predict(feature_array)
                latest_result = results[-1]
                if "predicted_class" in latest_result:
                    pred_class = latest_result["predicted_class"]
                    confidence = latest_result.get("probability", 0.0)
                    calibrated_prob = latest_result.get("probability", 0.0)
                elif "predicted_value" in latest_result:
                    pred_val = latest_result["predicted_value"]
                    pred_class = 1 if pred_val > 0 else 0
                    confidence = 0.5 + min(abs(pred_val), 0.5)
                    calibrated_prob = confidence
                else:
                    pred_class = 0
                    confidence = 0.0
                    calibrated_prob = 0.0
                    
                prediction_label = "BUY" if pred_class == 1 else "SELL"
                
                # Translate latest_features to API schema expected by Frontend
                translated_features = {
                    "Open": latest_features.get("open", 0.0),
                    "High": latest_features.get("high", 0.0),
                    "Low": latest_features.get("low", 0.0),
                    "Close": latest_features.get("close", 0.0),
                    "Volume": latest_features.get("volume", 0.0),
                    "RSI": latest_features.get("rsi", 0.0),
                    "MACD": latest_features.get("macd_line", 0.0),
                    "EMA20": latest_features.get("ema_short", 0.0),
                    "EMA50": latest_features.get("ema_long", 0.0),
                    "ATR": latest_features.get("atr", 0.0),
                    "ADX": latest_features.get("adx", 0.0),
                    "BB_UPPER": latest_features.get("bb_upper", 0.0),
                    "BB_LOWER": latest_features.get("bb_lower", 0.0),
                    "BB_WIDTH": latest_features.get("bb_width", 0.0),
                    "ROC": latest_features.get("roc", 0.0),
                    "MOMENTUM": latest_features.get("momentum", 0.0),
                    "DAILY_RETURN": latest_features.get("daily_return", 0.0),
                    "VOLATILITY": latest_features.get("volatility", 0.0),
                    "VOLUME_CHANGE": latest_features.get("volume_change", 0.0)
                } if latest_features else None
                
                logger.info("Request completed successfully through ML Engine")
                
                return {
                    "prediction": prediction_label,
                    "confidence": float(confidence),
                    "probability_buy": float(calibrated_prob),
                    "probability_sell": float(1.0 - calibrated_prob),
                    "class_id": int(pred_class),
                    "latest_features": translated_features
                }
            except Exception as e:
                logger.error(f"ML Engine proxy failed: {e}. Falling back to Legacy.")
                logger.info("ML Engine failed")
                logger.info("Falling back to Legacy TensorFlow")

        else:
            logger.info("ML Engine unavailable")
            logger.info("Falling back to Legacy TensorFlow")

        if feature_rows is None:
            raise ValueError("Legacy fallback requires preprocessed feature_rows. live_data_service no longer generates them.")

        processed = preprocessor.transform(
            stock=stock,
            feature_rows=feature_rows,
        )

        model = artifacts.model

        if model is None:
            raise RuntimeError(
                "ML model has not been loaded."
            )

        # Sigmoid output -> probability of BUY
        probability_buy = float(
            model.predict(
                processed,
                verbose=0,
            )[0][0]
        )

        probability_sell = 1.0 - probability_buy

        if probability_buy >= 0.5:
            prediction = "BUY"
            class_id = 1
            confidence = probability_buy
        else:
            prediction = "SELL"
            class_id = 0
            confidence = probability_sell

        return {
            "prediction": prediction,
            "class_id": class_id,
            "confidence": round(
                confidence,
                4,
            ),
            "probability_buy": round(
                probability_buy,
                4,
            ),
            "probability_sell": round(
                probability_sell,
                4,
            ),
            "latest_features": None
        }


prediction_service = PredictionService()