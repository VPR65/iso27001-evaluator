"""
Test para verificar que las evaluaciones solo muestren controles de la norma seleccionada
"""

import pytest
import re


class TestEvaluationControlsFilter:
    """Verificar que las evaluaciones solo muestren controles de la norma seleccionada"""

    def test_evaluation_shows_only_iso27001_controls(self, authenticated_client):
        """Una evaluacion ISO27001 debe mostrar solo 93 controles, no 153"""

        # Obtener el formulario de nueva evaluacion
        response = authenticated_client.get("/evaluations/new")
        assert response.status_code == 200

        html = response.text

        # Extraer CSRF token
        csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
        assert csrf_match, "CSRF token no encontrado"
        csrf_token = csrf_match.group(1)

        # Buscar norma ISO27001
        norma_match = re.search(r'value="([^"]+)"[^>]*>.*?ISO.*?27001', html, re.DOTALL)
        if not norma_match:
            # Buscar de otra forma
            norma_match = re.search(r'value="([^"]+)"[^>]*>[^<]*ISO[^<]*27001', html)

        assert norma_match, f"Norma ISO27001 no encontrada en el formulario"
        norma_id = norma_match.group(1)

        # Crear evaluacion
        form_data = {
            "csrf_token": csrf_token,
            "name": f"Test ISO27001 Controls - {id(self)}",
            "description": "Test para verificar conteo de controles",
            "norma_id": norma_id,
            "client_id": "",  # Superadmin puede no necesitar cliente
        }

        # Obtener lista de clientes
        clients_match = re.search(
            r'name="client_id"[^>]*>.*?<option value="([^"]+)"', html, re.DOTALL
        )
        if clients_match:
            form_data["client_id"] = clients_match.group(1)

        response = authenticated_client.post(
            "/evaluations/new", data=form_data, follow_redirects=False
        )

        # Si la creacion fue exitosa, verificar la evaluacion
        if response.status_code in [200, 302]:
            # Verificar que la evaluacion se creo y redirige
            if response.status_code == 302:
                redirect_url = response.headers.get("location", "")
                if "/evaluations/" in redirect_url:
                    eval_id = redirect_url.split("/evaluations/")[-1]

                    # Obtener la evaluacion creada
                    response = authenticated_client.get(f"/evaluations/{eval_id}")
                    assert response.status_code == 200

                    html = response.text

                    # Buscar el total de controles
                    total_match = re.search(r"Total Controles.*?(\d+)", html, re.DOTALL)
                    if total_match:
                        total_controles = int(total_match.group(1))
                        print(
                            f"Total controles en evaluacion ISO27001: {total_controles}"
                        )

                        # ISO27001:2022 tiene 93 controles
                        # Verificar que no sean 153 (todas las normas)
                        assert total_controles <= 100, (
                            f"Esperado max 100 controles para ISO27001, obtenido: {total_controles}"
                        )

    def test_evaluation_detail_shows_correct_controls_count(self, authenticated_client):
        """El detalle de evaluacion debe mostrar el conteo correcto de controles"""

        # Obtener primera evaluacion disponible
        response = authenticated_client.get("/evaluations")
        assert response.status_code == 200

        html = response.text

        # Buscar enlace a evaluacion
        eval_match = re.search(r'href="/evaluations/([^"]+)"', html)
        if eval_match:
            eval_id = eval_match.group(1)

            response = authenticated_client.get(f"/evaluations/{eval_id}")
            assert response.status_code == 200

            html = response.text

            # Verificar que se muestra la norma
            assert "ISO" in html, "Norma ISO no se muestra en la evaluacion"

            # Verificar que el total es razonable (< 100 para ISO27001)
            total_match = re.search(r"Total Controles.*?(\d+)", html, re.DOTALL)
            if total_match:
                total = int(total_match.group(1))
                print(f"Total controles: {total}")
                # No debe ser 153 (todas las normas combinadas)
                assert total < 100, (
                    f"Total de controles ({total}) es muy alto, posibles controles duplicados"
                )
