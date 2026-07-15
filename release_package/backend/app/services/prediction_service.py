import numpy as np

from app.core.model_loader import artifacts, ml_adapter
from app.utils.preprocessing import preprocessor


class PredictionService:

    def predict(self, stock: str, feature_rows):
        
        # PROXY: Use ML Engine if available
        if ml_adapter.is_available and ml_adapter.inference_engine is not None:
            engine = ml_adapter.inference_engine
            feature_array = np.asarray(feature_rows, dtype=np.float32)
            
            try:
                results = engine.predict(feature_array)
                latest_result = results[-1]
                
                pred_class = latest_result["Predicted Class"]
                prediction_label = "BUY" if pred_class == 1 else "SELL"
                confidence = latest_result["Confidence"]
                calibrated_prob = latest_result["Calibrated Probability"]
                
                return {
                    "prediction": prediction_label,
                    "class_id": pred_class,
                    "confidence": round(confidence, 4),
                    "probability_buy": round(calibrated_prob, 4),
                    "probability_sell": round(1.0 - calibrated_prob, 4),
                }
            except Exception as e:
                from app.core.logger import logger
                logger.error(f"ML Engine proxy failed: {e}. Falling back to Legacy.")

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
        }


prediction_service = PredictionService()