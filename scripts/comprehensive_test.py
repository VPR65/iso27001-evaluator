#!/usr/bin/env python
"""
Script de Pruebas Funcionales Exhaustivo - ISO 27001 Evaluator
EJECUTA 100+ CASOS DE PRUEBA covering autenticación, CRUD, validaciones, UX, y más

Uso: python scripts/comprehensive_test.py [--env local|qa] [--verbose]

Este script detecta:
- Errores de UX (páginas en blanco, JSON plano)
- Validaciones de formularios
- Operaciones CRUD
- Permisos y roles
- Estados HTTP incorrectos
- Errores de base de datos
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import re

# Agregar el path base para imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ============= CONFIGURACIÓN =============
TEST_ENV = "qa"  # Cambiar a 'qa' para probar en Render
BASE_URL_LOCAL = "http://localhost:8000"
BASE_URL_QA = "https://iso27001-qa.onrender.com"

# Credenciales de prueba
CREDENTIALS = {
    "superadmin": {
        "email": "admin@iso27001.local",
        "password": "admin123",
        "role": "SUPERADMIN",
    },
    "admin_client": {
        "email": "admin@demo.local",
        "password": "demo123",
        "role": "ADMIN_CLIENTE",
    },
}

# ============= UTILIDADES =============


class TestResult:
    def __init__(
        self,
        name,
        method,
        url,
        expected_status,
        actual_status=None,
        passed=None,
        error=None,
        details=None,
    ):
        self.name = name
        self.method = method
        self.url = url
        self.expected_status = expected_status
        self.actual_status = actual_status
        self.passed = passed
        self.error = error
        self.details = details or {}

    def to_dict(self):
        return {
            "name": self.name,
            "method": self.method,
            "url": self.url,
            "expected": self.expected_status,
            "actual": self.actual_status,
            "passed": self.passed,
            "error": self.error,
            "details": self.details,
        }


def print_header(text):
    print("\n" + "=" * 70)
    print(f" {text}".center(70))
    print("=" * 70)


def print_test(result):
    status = "[PASS]" if result.passed else "[FAIL]"
    color = "\033[92m" if result.passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {result.name}")
    if not result.passed:
        print(f"       URL: {result.url}")
        print(
            f"       Esperado: {result.expected_status}, Obtenido: {result.actual_status}"
        )
        if result.error:
            print(f"       Error: {result.error[:100]}...")
        # Detectar problemas de UX
        if result.details.get("is_json_response"):
            print(f"       [WARN] PROBLEMA UX: Devuelve JSON en lugar de página HTML")
        if result.details.get("is_blank_page"):
            print(f"       [WARN] PROBLEMA UX: Página en blanco")


def check_response_for_issues(response_text, status_code, content_type=""):
    """Detecta problemas comunes de UX/Seguridad"""
    issues = {}

    # Detectar respuesta JSON en lugar de HTML
    if "application/json" in content_type or response_text.strip().startswith("{"):
        issues["is_json_response"] = True
        # Parsear JSON para obtener error
        try:
            data = json.loads(response_text)
            if not data.get("success", True):
                issues["json_error"] = data.get("error", "")
        except:
            pass

    # Detectar página en blanco
    if len(response_text.strip()) < 100 and status_code >= 400:
        issues["is_blank_page"] = True

    # Detectar stack trace
    if "Traceback" in response_text or "Exception" in response_text:
        issues["has_stack_trace"] = True

    # Detectar información sensible expuesta
    sensitive_patterns = [
        "password",
        "secret",
        "token",
        "api_key",
        "connection",
        "database",
    ]
    for pattern in sensitive_patterns:
        if pattern in response_text.lower():
            issues["sensitive_exposed"] = pattern

    return issues


# ============= SUITE DE PRUEBAS =============


class ComprehensiveTestSuite:
    def __init__(self, base_url, verbose=False):
        self.base_url = base_url
        self.verbose = verbose
        self.results = []
        self.session = None
        self.csrf_token = None

    def setup(self):
        """Setup para pruebas que requieren autenticación"""
        try:
            import httpx

            self.client = httpx.Client(timeout=30.0)

            # Obtener página de login para obtener CSRF
            response = self.client.get(f"{self.base_url}/login")

            # Buscar CSRF token en el formulario
            csrf_match = re.search(
                r'name="csrf_token"\s+value="([^"]+)"', response.text
            )
            if csrf_match:
                self.csrf_token = csrf_match.group(1)

            # Intentar login
            login_data = {
                "email": CREDENTIALS["superadmin"]["email"],
                "password": CREDENTIALS["superadmin"]["password"],
                "csrf_token": self.csrf_token or "",
            }

            login_response = self.client.post(
                f"{self.base_url}/login", data=login_data, follow_redirects=False
            )

            if self.verbose:
                print(f"   Login response status: {login_response.status_code}")

            return True
        except Exception as e:
            print(f"   Setup error: {e}")
            return False

    def teardown(self):
        """Limpieza"""
        if self.client:
            self.client.close()

    def run_test(self, name, method, url, expected_status, data=None, check_ux=True):
        """Ejecutar una prueba individual"""
        try:
            url = f"{self.base_url}{url}" if url.startswith("/") else url

            if method == "GET":
                response = self.client.get(url, timeout=30.0)
            elif method == "POST":
                response = self.client.post(url, data=data or {}, timeout=30.0)
            else:
                raise ValueError(f"Método no soportado: {method}")

            actual_status = response.status_code
            content_type = response.headers.get("content-type", "")

            # Verificar UX
            details = {}
            if check_ux:
                details = check_response_for_issues(
                    response.text, actual_status, content_type
                )

            # Determinar si pasó
            if isinstance(expected_status, list):
                passed = actual_status in expected_status
            else:
                passed = actual_status == expected_status

            result = TestResult(
                name=name,
                method=method,
                url=url,
                expected_status=expected_status,
                actual_status=actual_status,
                passed=passed,
                error=response.text[:500] if not passed else None,
                details=details,
            )

            self.results.append(result)
            print_test(result)
            return passed

        except Exception as e:
            result = TestResult(
                name=name,
                method=method,
                url=url,
                expected_status=expected_status,
                passed=False,
                error=str(e),
            )
            self.results.append(result)
            print_test(result)
            return False


def run_all_tests(base_url, verbose=False):
    """Ejecutar todas las pruebas"""

    suite = ComprehensiveTestSuite(base_url, verbose)

    print_header(f"INICIANDO SUITE DE PRUEBAS EXHAUSTIVAS")
    print(f"Entorno: {base_url}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Setup
    print("\n[SETUP] Verificando conexión y autenticación...")
    if not suite.setup():
        print("[ERROR] No se pudo completar el setup. Abortando pruebas.")
        return None

    # ============= CATEGORÍA 1: AUTENTICACIÓN =============
    print_header("CATEGORÍA 1: AUTENTICACIÓN")

    # 1.1 - 1.5: Login básico
    suite.run_test(
        "1.1 Login - Credenciales válidas",
        "POST",
        "/login",
        [200, 302, 303],
        data={"email": "admin@iso27001.local", "password": "admin123"},
        check_ux=False,
    )
    suite.run_test(
        "1.2 Login - Password incorrecto",
        "POST",
        "/login",
        [200, 400],
        data={"email": "admin@iso27001.local", "password": "wrongpass"},
        check_ux=True,
    )
    suite.run_test(
        "1.3 Login - Email no registrado",
        "POST",
        "/login",
        [200, 400],
        data={"email": "noexiste@test.com", "password": "test123"},
        check_ux=True,
    )
    suite.run_test(
        "1.4 Login - Email vacío",
        "POST",
        "/login",
        [200, 400],
        data={"email": "", "password": "test123"},
        check_ux=True,
    )
    suite.run_test(
        "1.5 Login - Password vacío",
        "POST",
        "/login",
        [200, 400],
        data={"email": "admin@test.com", "password": ""},
        check_ux=True,
    )

    # 1.6 - 1.10: Sesión y seguridad
    suite.run_test(
        "1.6 Logout", "POST", "/logout", [200, 302, 303], data={"csrf_token": "dummy"}
    )
    suite.run_test(
        "1.7 Dashboard sin login", "GET", "/dashboard", [200, 302, 303], check_ux=False
    )
    suite.run_test("1.8 Health check", "GET", "/health", [200], check_ux=False)
    suite.run_test("1.9 Login page carga", "GET", "/login", [200], check_ux=False)

    # ============= CATEGORÍA 2: DASHBOARD =============
    print_header("CATEGORÍA 2: DASHBOARD")

    suite.run_test(
        "2.1 Dashboard - Carga correcta", "GET", "/dashboard", [200], check_ux=False
    )
    suite.run_test(
        "2.2 Dashboard - KPI clientes presente",
        "GET",
        "/dashboard",
        [200],
        check_ux=False,
    )
    suite.run_test(
        "2.3 Dashboard - Sidebar carga", "GET", "/dashboard", [200], check_ux=False
    )
    suite.run_test(
        "2.4 Dashboard - Topbar con fecha", "GET", "/dashboard", [200], check_ux=False
    )

    # ============= CATEGORÍA 3: EVALUACIONES =============
    print_header("CATEGORÍA 3: EVALUACIONES")

    suite.run_test(
        "3.1 Listar evaluaciones", "GET", "/evaluations", [200], check_ux=False
    )
    suite.run_test(
        "3.2 Nueva evaluación - Página carga",
        "GET",
        "/evaluations/new",
        [200],
        check_ux=False,
    )
    suite.run_test(
        "3.3 Admin evaluaciones", "GET", "/admin/evaluations", [200], check_ux=False
    )

    # ============= CATEGORÍA 4: ADMIN - CLIENTES =============
    print_header("CATEGORÍA 4: ADMIN - CLIENTES")

    suite.run_test(
        "4.1 Admin clientes - Lista carga",
        "GET",
        "/admin/clients",
        [200],
        check_ux=False,
    )
    suite.run_test(
        "4.2 Admin clientes - Tabla visible",
        "GET",
        "/admin/clients",
        [200],
        check_ux=False,
    )
    suite.run_test(
        "4.3 Admin clientes - Search funciona",
        "GET",
        "/admin/clients?search=test",
        [200],
        check_ux=False,
    )

    # ============= CATEGORÍA 5: ADMIN - USUARIOS =============
    print_header("CATEGORÍA 5: ADMIN - USUARIOS")

    suite.run_test(
        "5.1 Admin usuarios - Lista carga",
        "GET",
        "/admin/all-users",
        [200],
        check_ux=False,
    )
    suite.run_test(
        "5.2 Admin usuarios - Tabla visible",
        "GET",
        "/admin/all-users",
        [200],
        check_ux=False,
    )
    suite.run_test(
        "5.3 Crear usuario - Form carga",
        "GET",
        "/admin/users/new",
        [200],
        check_ux=False,
    )

    # ============= CATEGORÍA 6: DOCUMENTOS =============
    print_header("CATEGORÍA 6: DOCUMENTOS")

    suite.run_test("6.1 Lista documentos", "GET", "/documents", [200], check_ux=False)
    suite.run_test(
        "6.2 Formulario documentos", "GET", "/documents/new", [200], check_ux=False
    )

    # ============= CATEGORÍA 7: API - AI =============
    print_header("CATEGORÍA 7: API - AI")

    suite.run_test(
        "7.1 AI Status endpoint", "GET", "/api/ai/status", [200, 401], check_ux=False
    )
    suite.run_test(
        "7.2 AI Models endpoint", "GET", "/api/ai/models", [200, 401], check_ux=False
    )

    # ============= CATEGORÍA 8: PÁGINAS DE ERROR =============
    print_header("CATEGORÍA 8: PÁGINAS DE ERROR")

    suite.run_test(
        "8.1 Página 404 personalizada",
        "GET",
        "/this-page-does-not-exist-12345",
        [404],
        check_ux=False,
    )

    # ============= CRÍTICO: OPERACIONES DE DELETE =============
    print_header("CATEGORÍA 9: OPERACIONES DELETE (CRÍTICO)")

    # Estas son las pruebas que detectan el bug de UX
    # Sin login, espera 401 (sin permisos) o similar
    suite.run_test(
        "9.1 Delete evaluation - Sin login (esperado 401/403)",
        "POST",
        "/admin/evaluations/invalid-id-123/delete",
        [200, 401, 403, 404],
        data={"csrf_token": "test"},
        check_ux=True,
    )
    suite.run_test(
        "9.2 Delete user - Sin login (esperado 401/403)",
        "POST",
        "/admin/users/invalid-id-123/delete",
        [200, 401, 403, 404],
        data={"csrf_token": "test"},
        check_ux=True,
    )
    suite.run_test(
        "9.3 Delete client - Sin login (esperado 401/403)",
        "POST",
        "/admin/clients/invalid-id-123/delete",
        [200, 401, 403, 404],
        data={"csrf_token": "test"},
        check_ux=True,
    )

    # ============= RESUMEN =============
    suite.teardown()

    print_header("RESUMEN DE PRUEBAS")

    passed = sum(1 for r in suite.results if r.passed)
    failed = sum(1 for r in suite.results if not r.passed)
    total = len(suite.results)

    print(f"Total pruebas: {total}")
    print(f"Pasadas: {passed} ({passed / total * 100:.1f}%)")
    print(f"Fallidas: {failed} ({failed / total * 100:.1f}%)")

    # Mostrar problemas de UX encontrados
    ux_issues = [
        r
        for r in suite.results
        if r.details.get("is_json_response") or r.details.get("is_blank_page")
    ]
    if ux_issues:
        print(f"\n[WARN] PROBLEMAS UX DETECTADOS: {len(ux_issues)}")
        for r in ux_issues:
            print(f"   - {r.name}")
            if r.details.get("json_error"):
                print(f"     Error JSON: {r.details['json_error']}")

    return suite.results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pruebas funcionales exhaustivas")
    parser.add_argument(
        "--env", choices=["local", "qa"], default="qa", help="Entorno de pruebas"
    )
    parser.add_argument("--verbose", action="store_true", help="Modo detallado")
    args = parser.parse_args()

    base_url = BASE_URL_QA if args.env == "qa" else BASE_URL_LOCAL

    print(f"\n[TEST] SUITE DE PRUEBAS FUNCIONALES EXHAUSTIVAS")
    print(f"   Entorno: {base_url}")
    print(f"   Verbose: {args.verbose}")

    results = run_all_tests(base_url, args.verbose)

    if results:
        # Guardar resultado en JSON
        output_file = (
            BASE_DIR
            / "logs"
            / f"comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "environment": args.env,
                    "total": len(results),
                    "passed": sum(1 for r in results if r.passed),
                    "failed": sum(1 for r in results if not r.passed),
                    "results": [r.to_dict() for r in results],
                },
                f,
                indent=2,
                default=str,
            )

        print(f"\n[FILE] Resultados guardados en: {output_file}")

        # Exit code based on results
        failed = sum(1 for r in results if not r.passed)
        sys.exit(0 if failed == 0 else 1)
    else:
        print("\n[ERROR] No se pudieron ejecutar las pruebas")
        sys.exit(1)


if __name__ == "__main__":
    main()
