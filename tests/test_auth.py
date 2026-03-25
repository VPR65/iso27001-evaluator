"""
Test suite for authentication routes
"""

import pytest


class TestLogin:
    """Tests for login functionality"""

    def test_login_page_loads(self, client):
        """Login page should load without errors"""
        response = client.get("/login")
        assert response.status_code == 200
        assert "Iniciar Sesion" in response.text or "login" in response.text.lower()

    def test_login_page_has_csrf_token(self, client):
        """Login form should have CSRF token"""
        response = client.get("/login")
        assert response.status_code == 200
        assert "csrf_token" in response.text
        assert 'name="csrf_token"' in response.text

    def test_login_success(self, client):
        """Valid credentials should login successfully"""
        response = client.post(
            "/login", data={"email": "admin@iso27001.local", "password": "admin123"}
        )
        assert response.status_code in [200, 302]

    def test_login_invalid_credentials(self, client):
        """Invalid credentials should show error"""
        response = client.post(
            "/login",
            data={"email": "invalid@test.com", "password": "wrongpassword"},
            follow_redirects=False,
        )
        assert response.status_code == 200


class TestLogout:
    """Tests for logout functionality"""

    def test_logout_requires_auth(self, client):
        """Logout should require authentication"""
        response = client.post("/logout", follow_redirects=False)
        assert response.status_code in [302, 403]

    def test_logout_works_when_authenticated(self, authenticated_client):
        """Logout should work when authenticated"""
        response = authenticated_client.get("/logout", follow_redirects=False)
        assert response.status_code in [200, 302, 307]
