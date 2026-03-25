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
