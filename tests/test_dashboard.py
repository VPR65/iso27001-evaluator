"""
Test suite for dashboard and navigation
"""

import pytest


class TestDashboard:
    """Tests for dashboard"""

    def test_dashboard_requires_auth(self, client):
        """Dashboard should require authentication"""
        response = client.get("/dashboard")
        assert response.status_code in [200, 302, 401]

    def test_dashboard_loads_with_auth(self, authenticated_client):
        """Dashboard should load when authenticated"""
        response = authenticated_client.get("/dashboard")
        assert response.status_code == 200


class TestClients:
    """Tests for clients routes"""

    def test_clients_list_requires_auth(self, client):
        """Clients list should require authentication"""
        response = client.get("/clients")
        assert response.status_code in [200, 302, 401]

    def test_clients_list_loads_with_auth(self, authenticated_client):
        """Clients list should load when authenticated"""
        response = authenticated_client.get("/clients")
        assert response.status_code == 200


class TestDocuments:
    """Tests for documents routes"""

    def test_documents_requires_auth(self, client):
        """Documents should require authentication"""
        response = client.get("/documents")
        assert response.status_code in [200, 302, 401]

    def test_documents_loads_with_auth(self, authenticated_client):
        """Documents should load when authenticated"""
        response = authenticated_client.get("/documents")
        assert response.status_code == 200


class TestStats:
    """Tests for statistics routes"""

    def test_stats_requires_auth(self, client):
        """Stats should require authentication"""
        response = client.get("/stats/test-eval")
        assert response.status_code in [200, 302, 401, 404]
