import numpy as np

from app.core.model_loader import artifacts
from app.utils.preprocessing import preprocessor


class PredictionService:

    def predict(self, stock: str, feature_rows):

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