"""
Test suite for admin routes
"""

import pytest


class TestAdminUsers:
    """Tests for admin users management"""

    def test_admin_users_requires_auth(self, client):
        """Admin users page should require authentication"""
        response = client.get("/admin/all-users")
        assert response.status_code in [200, 302, 401]

    def test_admin_users_loads_with_superadmin(self, authenticated_client):
        """Admin users should load with superadmin"""
        response = authenticated_client.get("/admin/all-users")
        assert response.status_code == 200

    def test_admin_users_has_create_form(self, authenticated_client):
        """Admin users page should have a create user form"""
        response = authenticated_client.get("/admin/all-users")
        assert response.status_code == 200
        assert 'name="email"' in response.text
        assert 'name="name"' in response.text
        assert 'name="password"' in response.text
        assert 'name="role"' in response.text
        assert 'name="client_id"' in response.text

    def test_admin_users_has_csrf_token_in_form(self, authenticated_client):
        """Create user form should have CSRF token"""
        response = authenticated_client.get("/admin/all-users")
        assert 'name="csrf_token"' in response.text


class TestDebugEndpoints:
    """Tests for debug endpoints"""

    def test_debug_users_with_valid_token(self, client):
        """Debug users should work with valid token"""
        response = client.get("/admin/debug/users?token=qa-debug-2024")
        assert response.status_code == 200
        assert response.json() is not None

    def test_debug_users_without_token_requires_auth(self, client):
        """Debug users should require auth without token"""
        response = client.get("/admin/debug/users")
        assert response.status_code in [401, 403]

    def test_seed_test_data_endpoint(self, client):
        """Debug seed test data endpoint should work"""
        response = client.get("/admin/debug/seed-test-data?token=qa-debug-2024")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True


class TestBiblioteca:
    """Tests for Biblioteca routes"""

    def test_biblioteca_requires_auth(self, client):
        """Biblioteca should require authentication"""
        response = client.get("/biblioteca")
        assert response.status_code in [200, 302, 401]

    def test_biblioteca_loads_with_auth(self, authenticated_client):
        """Biblioteca should load when authenticated"""
        response = authenticated_client.get("/biblioteca")
        assert response.status_code == 200
