from unittest.mock import MagicMock

from app.main import app
from app.database import get_db

from app.services.backtesting_service import (
    backtesting_service,
)


def test_backtesting_success(client):

    db = MagicMock()

    original = backtesting_service.summary

    backtesting_service.summary = MagicMock(
        return_value={
            "accuracy": 78.0,
            "wins": 39,
            "losses": 11,
        }
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get(
        "/backtesting/RELIANCE"
    )

    backtesting_service.summary = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200


def test_backtesting_not_found(client):

    db = MagicMock()

    original = backtesting_service.summary

    backtesting_service.summary = MagicMock(
        return_value=None
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get(
        "/backtesting/UNKNOWN"
    )

    backtesting_service.summary = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404