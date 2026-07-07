from datetime import datetime
from unittest.mock import MagicMock

from app.main import app
from app.database import get_db
from app.models import PredictionHistory, Stock


def test_get_history(client):

    db = MagicMock()

    history = PredictionHistory(
        id=1,
        stock_id=1,
        prediction="BUY",
        confidence=0.91,
        probability_buy=0.91,
        probability_sell=0.09,
        created_at=datetime.utcnow(),
    )

    stock = Stock(
        id=1,
        symbol="RELIANCE",
        company_name="Reliance Industries",
        sector="Energy",
    )

    db.query.return_value.join.return_value.order_by.return_value.all.return_value = [
        (history, stock)
    ]

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/history/")

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["symbol"] == "RELIANCE"
    assert data[0]["prediction"] == "BUY"


def test_get_stock_history(client):

    db = MagicMock()

    history = PredictionHistory(
        id=1,
        stock_id=1,
        prediction="BUY",
        confidence=0.91,
        probability_buy=0.91,
        probability_sell=0.09,
        created_at=datetime.utcnow(),
    )

    (
        db.query.return_value
        .join.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = [history]

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/history/RELIANCE")

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_latest_prediction(client):

    db = MagicMock()

    history = PredictionHistory(
        id=1,
        stock_id=1,
        prediction="BUY",
        confidence=0.91,
        probability_buy=0.91,
        probability_sell=0.09,
        created_at=datetime.utcnow(),
    )

    (
        db.query.return_value
        .join.return_value
        .filter.return_value
        .order_by.return_value
        .first.return_value
    ) = history

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/history/latest/RELIANCE")

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json()["prediction"] == "BUY"