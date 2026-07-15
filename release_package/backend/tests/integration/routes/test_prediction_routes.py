from unittest.mock import MagicMock

from app.services.prediction_service import prediction_service


def test_prediction_success(client):

    original = prediction_service.predict

    prediction_service.predict = MagicMock(
        return_value={
            "prediction": "BUY",
            "class_id": 1,
            "confidence": 0.91,
            "probability_buy": 0.91,
            "probability_sell": 0.09,
            "stock": "RELIANCE",
        }
    )

    features = [[1.0] * 19 for _ in range(48)]

    response = client.post(
        "/predict",
        json={
            "stock": "RELIANCE",
            "features": features,
        },
    )

    prediction_service.predict = original

    assert response.status_code == 200
    assert response.json()["prediction"] == "BUY"