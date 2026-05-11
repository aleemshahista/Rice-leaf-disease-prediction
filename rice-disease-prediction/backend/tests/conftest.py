"""
Test fixtures and configuration for pytest.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

# Override settings before importing app
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["STORAGE_TYPE"] = "local"
os.environ["MODEL_PATH"] = "./ml/model/nonexistent.pth"  # Force demo mode

from app.core.database import Base, get_db
from app.main import app

# Test engine
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    # Clean up test DB file
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a test user and return auth headers."""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_headers(client):
    """Register a second test user."""
    response = client.post("/api/auth/register", json={
        "email": "user2@example.com",
        "password": "testpass456",
        "name": "Second User",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
