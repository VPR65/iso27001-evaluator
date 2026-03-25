import pytest
import re
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, get_session
from app.models import SQLModel, Session as UserSession
from sqlalchemy import select


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables before all tests"""
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture(scope="function", autouse=True)
def clean_sessions():
    """Clean all user sessions before and after each test"""
    session_gen = get_session()
    session = next(session_gen)
    try:
        session.query(UserSession).delete()
        session.commit()
    finally:
        try:
            next(session_gen)
        except StopIteration:
            pass

    yield

    session_gen = get_session()
    session = next(session_gen)
    try:
        session.query(UserSession).delete()
        session.commit()
    finally:
        try:
            next(session_gen)
        except StopIteration:
            pass


@pytest.fixture(scope="function")
def client():
    """FastAPI test client with fresh session per test"""
    with TestClient(app) as c:
        yield c


def extract_csrf_token(html: str) -> str:
    """Extract CSRF token from HTML form"""
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    if match:
        return match.group(1)
    match = re.search(r'csrf_token["\s]+value=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    return ""


@pytest.fixture(scope="function")
def authenticated_client(client):
    """Client with superadmin session already authenticated"""
    response = client.get("/login")
    csrf_token = extract_csrf_token(response.text)

    response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "email": "admin@iso27001.local",
            "password": "admin123",
        },
    )
    assert response.status_code in [200, 302], f"Login failed: {response.status_code}"
    yield client


@pytest.fixture(scope="function")
def admin_client(client):
    """Client with demo admin session authenticated"""
    response = client.get("/login")
    csrf_token = extract_csrf_token(response.text)

    response = client.post(
        "/login",
        data={
            "csrf_token": csrf_token,
            "email": "admin@demo.local",
            "password": "demo123",
        },
    )
    assert response.status_code in [200, 302], f"Login failed: {response.status_code}"
    yield client
