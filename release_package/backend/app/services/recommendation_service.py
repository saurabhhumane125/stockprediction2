class RecommendationService:

    STRONG_CONFIDENCE = 0.85
    MODERATE_CONFIDENCE = 0.70
    MIN_CONFIDENCE = 0.60

    def generate(
        self,
        fusion_result: dict,
    ):

        prediction = fusion_result["prediction"]

        confidence = float(
            fusion_result["confidence"]
        )

        sentiment = fusion_result["sentiment"]

        sentiment_score = float(
            fusion_result["sentiment_score"]
        )

        technical_signal = fusion_result[
            "technical_signal"
        ]

        news_signal = fusion_result[
            "news_signal"
        ]

        final_reason = fusion_result[
            "final_reason"
        ]

        probability_buy = fusion_result.get(
            "probability_buy"
        )

        probability_sell = fusion_result.get(
            "probability_sell"
        )

        class_id = fusion_result.get(
            "class_id"
        )

        action = "HOLD"
        strength = "WEAK"

        if confidence < self.MIN_CONFIDENCE:

            action = "HOLD"
            strength = "WEAK"

        else:

            if prediction == "BUY":

                if sentiment == "NEGATIVE":

                    action = "HOLD"
                    strength = "MODERATE"

                elif confidence >= self.STRONG_CONFIDENCE:

                    action = "STRONG_BUY"
                    strength = "VERY_STRONG"

                elif confidence >= self.MODERATE_CONFIDENCE:

                    action = "BUY"
                    strength = "STRONG"

                else:

                    action = "BUY"
                    strength = "MODERATE"

            else:

                if sentiment == "POSITIVE":

                    action = "HOLD"
                    strength = "MODERATE"

                elif confidence >= self.STRONG_CONFIDENCE:

                    action = "STRONG_SELL"
                    strength = "VERY_STRONG"

                elif confidence >= self.MODERATE_CONFIDENCE:

                    action = "SELL"
                    strength = "STRONG"

                else:

                    action = "SELL"
                    strength = "MODERATE"

        summary = (
            f"{action.replace('_', ' ')} recommendation "
            f"generated using GRU prediction and "
            f"news sentiment."
        )

        return {

            "action": action,

            "strength": strength,

            "confidence": round(
                confidence,
                4,
            ),

            "prediction": prediction,

            "sentiment": sentiment,

            "sentiment_score": round(
                sentiment_score,
                4,
            ),

            "class_id": class_id,

            "probability_buy": probability_buy,

            "probability_sell": probability_sell,

            "technical_signal": technical_signal,

            "news_signal": news_signal,

            "reason": final_reason,

            "summary": summary,
        }


recommendation_service = RecommendationService()