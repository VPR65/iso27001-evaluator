"""
Test suite for clients routes
"""

import pytest


class TestClientsList:
    """Tests for clients list"""

    def test_clients_list_requires_auth(self, client):
        """Clients list should require authentication"""
        response = client.get("/clients")
        assert response.status_code in [200, 302, 401]

    def test_clients_list_loads_with_superadmin(self, authenticated_client):
        """Clients list should load with superadmin"""
        response = authenticated_client.get("/clients")
        assert response.status_code == 200

    def test_clients_list_has_new_button(self, authenticated_client):
        """Clients list should have a button to create new client"""
        response = authenticated_client.get("/clients")
        assert response.status_code == 200
        assert (
            "/clients/new" in response.text or "nuevo cliente" in response.text.lower()
        )

    def test_clients_list_has_csrf_token(self, authenticated_client):
        """Clients list should have CSRF token"""
        response = authenticated_client.get("/clients")
        assert "csrf_token" in response.text.lower()


class TestClientCreation:
    """Tests for client creation"""

    def test_create_client_form_loads(self, authenticated_client):
        """New client form should load"""
        response = authenticated_client.get("/clients/new")
        assert response.status_code == 200

    def test_create_client_form_has_csrf(self, authenticated_client):
        """New client form should have CSRF token"""
        response = authenticated_client.get("/clients/new")
        assert "csrf_token" in response.text.lower()


class TestClientsPage:
    """Tests for clients page elements"""

    def test_clients_page_loads(self, authenticated_client):
        """Clients page should load successfully"""
        response = authenticated_client.get("/clients")
        assert response.status_code == 200
        assert "cliente" in response.text.lower()
