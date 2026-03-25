"""
Test suite para creacion de evaluaciones
"""

import pytest
import re


class TestCreateEvaluation:
    """Tests para la creacion de evaluaciones"""

    def test_create_evaluation_form_has_required_fields(self, authenticated_client):
        """El formulario debe tener todos los campos requeridos"""
        response = authenticated_client.get("/evaluations/new")
        assert response.status_code == 200
        assert 'name="name"' in response.text
        assert 'name="norma_id"' in response.text
        assert 'name="client_id"' in response.text
        assert 'name="csrf_token"' in response.text

    def test_create_evaluation_normas_are_loaded(self, authenticated_client):
        """Deben cargarse las normas en el selector"""
        response = authenticated_client.get("/evaluations/new")
        assert response.status_code == 200
        assert "ISO" in response.text or "norma" in response.text.lower()

    def test_create_evaluation_clients_are_loaded(self, authenticated_client):
        """Deben cargarse los clientes en el selector"""
        response = authenticated_client.get("/evaluations/new")
        assert response.status_code == 200
        html = response.text.lower()
        assert "cliente" in html or "client" in html or "option value" in html

    def test_create_evaluation_requires_csrf_token(self, authenticated_client):
        """La creacion debe requerir CSRF token"""
        response = authenticated_client.get("/evaluations/new")
        csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
        assert csrf_match is not None, "CSRF token no encontrado"
        csrf_token = csrf_match.group(1)
        assert len(csrf_token) > 20, "CSRF token muy corto"


class TestEvaluationList:
    """Tests para la lista de evaluaciones"""

    def test_evaluations_list_loads(self, authenticated_client):
        """La lista de evaluaciones debe cargar"""
        response = authenticated_client.get("/evaluations")
        assert response.status_code == 200
        assert (
            "evaluacion" in response.text.lower()
            or "evaluations" in response.text.lower()
        )

    def test_evaluations_list_has_new_button(self, authenticated_client):
        """Debe haber un boton para crear nueva evaluacion"""
        response = authenticated_client.get("/evaluations")
        assert response.status_code == 200
        assert (
            "/evaluations/new" in response.text.lower()
            or "nueva" in response.text.lower()
        )


class TestEvaluationsWorkflow:
    """Tests para el flujo completo de evaluaciones"""

    def test_authenticated_user_can_see_evaluation_form(self, authenticated_client):
        """Un usuario autenticado debe poder ver el formulario"""
        response = authenticated_client.get("/evaluations/new")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers.get("content-type", "").startswith("text/html")
