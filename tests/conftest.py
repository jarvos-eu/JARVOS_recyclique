"""Pytest fixtures — client FastAPI, DB, auth."""

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Use in-memory SQLite for tests when DATABASE_URL not set
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_recyclic.db")

from api.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)
