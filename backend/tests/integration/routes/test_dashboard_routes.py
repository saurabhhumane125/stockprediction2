from unittest.mock import MagicMock

from app.main import app
from app.database import get_db
from app.services.dashboard_service import dashboard_service


def test_dashboard_success(client):

    db = MagicMock()

    original = dashboard_service.get_dashboard

    dashboard_service.get_dashboard = MagicMock(
        return_value={
            "stock": {
                "id": 1,
                "symbol": "RELIANCE",
                "company_name": "Reliance Industries",
                "sector": "Energy",
            },
            "latest_price": None,
            "latest_prediction": None,
            "recommendation": None,
        }
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/dashboard/RELIANCE")

    dashboard_service.get_dashboard = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json()["stock"]["symbol"] == "RELIANCE"


def test_dashboard_not_found(client):

    db = MagicMock()

    original = dashboard_service.get_dashboard

    dashboard_service.get_dashboard = MagicMock(
        return_value=None
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/dashboard/UNKNOWN")

    dashboard_service.get_dashboard = original

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404