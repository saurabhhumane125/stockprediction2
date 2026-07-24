import os
import pytest

# Inject required environment variables for Pydantic Settings before any tests are collected
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_collection"
