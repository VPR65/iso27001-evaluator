"""
Test de integracion: Crear una evaluacion completa
"""

import pytest
import re


class TestCreateEvaluationIntegration:
    """Test de integracion para crear una evaluacion"""

    def test_full_evaluation_creation_flow(self, authenticated_client):
        """Flujo completo: ver formulario -> obtener datos -> crear evaluacion"""

        # Paso 1: Obtener formulario
        response = authenticated_client.get("/evaluations/new")
        assert response.status_code == 200, (
            f"Formulario no cargo: {response.status_code}"
        )

        html = response.text

        # Paso 2: Extraer CSRF token
        csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
        assert csrf_match, "CSRF token no encontrado"
        csrf_token = csrf_match.group(1)

        # Paso 3: Extraer primera norma disponible
        norma_match = re.search(
            r'<select[^>]*id="norma_id"[^>]*>.*?<option value="([^"]+)"',
            html,
            re.DOTALL,
        )
        if not norma_match:
            norma_match = re.search(
                r'name="norma_id"[^>]*>.*?<option value="([^"]+)"', html, re.DOTALL
            )
        assert norma_match, (
            f"Norma no encontrada en el HTML. HTML snippet: {html[html.find('norma') : html.find('norma') + 500]}"
        )
        norma_id = norma_match.group(1)

        # Paso 4: Extraer primer cliente disponible
        client_match = re.search(
            r'name="client_id"[^>]*>.*?<option value="([^"]+)"', html, re.DOTALL
        )
        if not client_match:
            client_match = re.search(
                r'id="client_id"[^>]*>.*?<option value="([^"]+)"', html, re.DOTALL
            )
        assert client_match, (
            f"Cliente no encontrado en el HTML. HTML snippet: {html[html.find('client') : html.find('client') + 500]}"
        )
        client_id = client_match.group(1)

        # Paso 5: Crear evaluacion
        form_data = {
            "csrf_token": csrf_token,
            "name": f"Test Evaluation - QA {id(self)}",
            "description": "Evaluacion de prueba automatizada",
            "norma_id": norma_id,
            "client_id": client_id,
        }

        response = authenticated_client.post(
            "/evaluations/new", data=form_data, follow_redirects=False
        )

        # Verificar que no hay error 500
        assert response.status_code in [200, 302], (
            f"Error al crear evaluacion: {response.status_code}\n{response.text[:500]}"
        )

        # Si hay redirect, verificar que es a la pagina de detalle
        if response.status_code == 302:
            assert "/evaluations/" in response.headers.get("location", ""), (
                f"Redirect incorrecto: {response.headers.get('location')}"
            )
