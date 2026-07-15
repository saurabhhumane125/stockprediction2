from datetime import datetime
from unittest.mock import MagicMock

from app.main import app
from app.database import get_db
from app.models import User


def test_register_success(client):

    db = MagicMock()

    user = User(
        id=1,
        full_name="Test User",
        email="test@example.com",
        is_active=1,
        created_at=datetime.utcnow(),
    )

    from app.services.user_service import user_service

    original = user_service.create_user

    user_service.create_user = MagicMock(
        return_value=user
    )

    app.dependency_overrides[get_db] = (
        lambda: db
    )

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123",
        },
    )

    user_service.create_user = original

    app.dependency_overrides.pop(
        get_db,
        None,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["full_name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["is_active"] == 1
    assert "created_at" in data


def test_login_invalid_credentials(client):

    db = MagicMock()

    from app.services.user_service import user_service

    original = user_service.authenticate

    user_service.authenticate = MagicMock(
        return_value=None
    )

    app.dependency_overrides[get_db] = (
        lambda: db
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "x@test.com",
            "password": "Password123",
        },
    )

    user_service.authenticate = original

    app.dependency_overrides.pop(
        get_db,
        None,
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Invalid email or password."
    }