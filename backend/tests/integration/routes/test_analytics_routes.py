from unittest.mock import MagicMock

from app.main import app
from app.database import get_db

from app.services.analytics_service import analytics_service
from app.services.evaluation_service import evaluation_service


def test_overview(client):

    db = MagicMock()

    original = analytics_service.get_overview

    analytics_service.get_overview = MagicMock(
        return_value={
            "total_predictions": 100,
            "accuracy": 72.5,
        }
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/analytics/overview")

    analytics_service.get_overview = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200


def test_recent(client):

    db = MagicMock()

    original = analytics_service.get_recent_predictions

    analytics_service.get_recent_predictions = MagicMock(
        return_value=[]
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/analytics/recent")

    analytics_service.get_recent_predictions = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200


def test_distribution(client):

    db = MagicMock()

    original = analytics_service.get_prediction_distribution

    analytics_service.get_prediction_distribution = MagicMock(
        return_value={}
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/analytics/distribution")

    analytics_service.get_prediction_distribution = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200


def test_confidence(client):

    db = MagicMock()

    original = analytics_service.get_confidence_statistics

    analytics_service.get_confidence_statistics = MagicMock(
        return_value={}
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/analytics/confidence")

    analytics_service.get_confidence_statistics = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200


def test_accuracy(client):

    db = MagicMock()

    original = evaluation_service.evaluate

    evaluation_service.evaluate = MagicMock(
        return_value={
            "accuracy": 80.0,
        }
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/analytics/accuracy/RELIANCE")

    evaluation_service.evaluate = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200