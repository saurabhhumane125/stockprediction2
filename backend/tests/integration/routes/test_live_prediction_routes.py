from unittest.mock import MagicMock

from app.services.live_prediction_service import (
    live_prediction_service,
)


def test_live_prediction_success(client):

    original = live_prediction_service.predict

    live_prediction_service.predict = MagicMock(
        return_value={
            "prediction": "BUY",
            "confidence": 0.95,
        }
    )

    response = client.post(
        "/predict/live/RELIANCE"
    )

    live_prediction_service.predict = original

    assert response.status_code == 200
    assert response.json()["prediction"] == "BUY"