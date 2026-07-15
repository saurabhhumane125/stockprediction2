import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_user
from app.core.model_loader import artifacts


class MockUser:
    id = 1
    full_name = "Test User"
    email = "test@example.com"
    is_active = 1


@pytest.fixture(scope="session", autouse=True)
def load_ml_artifacts():

    if artifacts.model is None:
        artifacts.load_artifacts()

    yield


@pytest.fixture(scope="session")
def application(load_ml_artifacts):
    return app


@pytest.fixture(scope="session")
def client(application):
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def authenticated_user():
    return MockUser()


@pytest.fixture(autouse=True)
def override_dependencies(authenticated_user):

    app.dependency_overrides[get_current_user] = (
        lambda: authenticated_user
    )

    yield

    app.dependency_overrides.clear()