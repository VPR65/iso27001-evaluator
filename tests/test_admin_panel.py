"""
Test suite para el Panel de Administracion
"""

import pytest
import re


class TestAdminClientsPanel:
    """Tests para el panel de clientes admin"""

    def test_admin_clients_page_loads(self, authenticated_client):
        """El panel de clientes debe cargar"""
        response = authenticated_client.get("/admin/clients")
        assert response.status_code == 200
        assert "Clientes" in response.text or "cliente" in response.text.lower()

    def test_admin_clients_has_csrf_token(self, authenticated_client):
        """El panel de clientes debe tener CSRF token"""
        response = authenticated_client.get("/admin/clients")
        assert 'name="csrf_token"' in response.text

    def test_admin_clients_has_create_form(self, authenticated_client):
        """Debe tener formulario para crear cliente"""
        response = authenticated_client.get("/admin/clients")
        assert 'name="name"' in response.text or 'id="name"' in response.text

    def test_admin_clients_has_delete_buttons(self, authenticated_client):
        """Debe tener botones de eliminar"""
        response = authenticated_client.get("/admin/clients")
        assert "trash" in response.text.lower() or "eliminar" in response.text.lower()


class TestAdminUsersPanel:
    """Tests para el panel de usuarios admin"""

    def test_admin_users_page_loads(self, authenticated_client):
        """El panel de usuarios debe cargar"""
        response = authenticated_client.get("/admin/all-users")
        assert response.status_code == 200
        assert "Usuarios" in response.text or "usuarios" in response.text.lower()

    def test_admin_users_has_csrf_token(self, authenticated_client):
        """El panel de usuarios debe tener CSRF token"""
        response = authenticated_client.get("/admin/all-users")
        assert 'name="csrf_token"' in response.text

    def test_admin_users_has_create_form(self, authenticated_client):
        """Debe tener formulario para crear usuario"""
        response = authenticated_client.get("/admin/all-users")
        assert 'name="email"' in response.text
        assert 'name="password"' in response.text

    def test_admin_users_has_delete_buttons(self, authenticated_client):
        """Debe tener botones de eliminar"""
        response = authenticated_client.get("/admin/all-users")
        assert "trash" in response.text.lower() or "eliminar" in response.text.lower()


class TestAdminEvaluationsPanel:
    """Tests para el panel de evaluaciones admin"""

    def test_admin_evaluations_page_loads(self, authenticated_client):
        """El panel de evaluaciones debe cargar"""
        response = authenticated_client.get("/admin/evaluations")
        assert response.status_code == 200
        assert "Evaluacion" in response.text or "evaluacion" in response.text.lower()

    def test_admin_evaluations_has_delete_buttons(self, authenticated_client):
        """Debe tener botones de eliminar"""
        response = authenticated_client.get("/admin/evaluations")
        assert "trash" in response.text.lower() or "eliminar" in response.text.lower()


class TestITIL4Norma:
    """Tests para ITIL v4"""

    def test_itil4_in_nomas_selector(self, authenticated_client):
        """ITIL v4 debe aparecer en el selector de normas"""
        response = authenticated_client.get("/evaluations/new")
        assert response.status_code == 200
        assert "ITIL" in response.text

    def test_itil4_form_has_norma_options(self, authenticated_client):
        """El formulario de evaluacion debe tener opciones de norma"""
        response = authenticated_client.get("/evaluations/new")
        html = response.text
        norma_options = re.findall(r'<option[^>]*value="([^"]+)"[^>]*>[^<]*ITIL', html)
        assert len(norma_options) >= 1, "ITIL v4 debe estar disponible como norma"


class TestAdminNavigation:
    """Tests para la navegacion del admin"""

    def test_sidebar_has_clients_link(self, authenticated_client):
        """El sidebar debe tener enlace a clientes"""
        response = authenticated_client.get("/dashboard")
        assert "/admin/clients" in response.text or "cliente" in response.text.lower()

    def test_sidebar_has_evaluations_link(self, authenticated_client):
        """El sidebar debe tener enlace a evaluaciones admin"""
        response = authenticated_client.get("/dashboard")
        assert (
            "/admin/evaluations" in response.text
            or "evaluacion" in response.text.lower()
        )

    def test_sidebar_has_users_link(self, authenticated_client):
        """El sidebar debe tener enlace a usuarios"""
        response = authenticated_client.get("/dashboard")
        assert "/admin/all-users" in response.text or "usuario" in response.text.lower()
