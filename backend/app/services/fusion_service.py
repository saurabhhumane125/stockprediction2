class FusionService:

    def fuse(
        self,
        prediction: dict,
        sentiment: dict,
    ):

        prediction_label = prediction["prediction"]

        confidence = float(
            prediction["confidence"]
        )

        sentiment_label = sentiment[
            "sentiment"
        ].value

        sentiment_score = float(
            sentiment["score"]
        )

        technical_signal = (
            f"GRU model predicts {prediction_label}"
        )

        if sentiment_label == "POSITIVE":

            news_signal = (
                "Recent news sentiment is positive."
            )

            confidence += (
                sentiment_score * 0.05
            )

        elif sentiment_label == "NEGATIVE":

            news_signal = (
                "Recent news sentiment is negative."
            )

            confidence -= (
                sentiment_score * 0.05
            )

        else:

            news_signal = (
                "Recent news sentiment is neutral."
            )

        confidence = max(
            0.0,
            min(
                confidence,
                1.0,
            ),
        )

        final_reason = (
            f"{technical_signal} "
            f"{news_signal}"
        )

        return {

            "prediction": prediction_label,

            "confidence": round(
                confidence,
                4,
            ),

            "sentiment": sentiment_label,

            "sentiment_score": round(
                sentiment_score,
                4,
            ),

            "technical_signal": technical_signal,

            "news_signal": news_signal,

            "final_reason": final_reason,

            "class_id": prediction["class_id"],

            "probability_buy": prediction["probability_buy"],

            "probability_sell": prediction["probability_sell"],
        }


fusion_service = FusionService()