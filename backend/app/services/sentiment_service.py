from transformers import pipeline

from app.models import SentimentType


class SentimentService:

    def __init__(self):

        self.model = pipeline(
            task="text-classification",
            model="ProsusAI/finbert",
        )

    def analyze(
        self,
        text: str,
    ):

        result = self.model(
            text[:512]
        )[0]

        label = result["label"].upper()

        score = float(
            result["score"]
        )

        return {
            "sentiment": SentimentType[label],
            "score": score,
        }


sentiment_service = SentimentService()