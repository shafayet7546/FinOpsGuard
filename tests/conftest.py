# Shared pytest fixtures for API tests.
#
# Pytest auto-loads this file, so fixtures are available to all tests.
# We override the app DB dependency to use a separate test DB, keeping
# tests isolated, repeatable, and independent from local data.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db

# Dedicated SQLite database for tests
TEST_DATABASE_URL = "sqlite:///./test_finopsguard.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Yield a database session bound to the test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create tables before each test and drop them after each test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client():
    """Provide a FastAPI TestClient wired to the test DB dependency."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
