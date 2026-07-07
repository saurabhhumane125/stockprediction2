from unittest.mock import MagicMock

from app.main import app
from app.database import get_db
from app.models import Stock


def override_db():

    db = MagicMock()

    yield db


def test_get_all_stocks(client):

    db = MagicMock()

    db.query.return_value.order_by.return_value.all.return_value = [
        Stock(
            id=1,
            symbol="RELIANCE",
            company_name="Reliance Industries",
            sector="Energy",
        )
    ]

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/stocks/")

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["symbol"] == "RELIANCE"


def test_get_stock_by_symbol(client):

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = Stock(
        id=1,
        symbol="RELIANCE",
        company_name="Reliance Industries",
        sector="Energy",
    )

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/stocks/RELIANCE")

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200

    assert response.json()["symbol"] == "RELIANCE"


def test_get_unknown_stock(client):

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/stocks/UNKNOWN")

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Stock not found."
    }