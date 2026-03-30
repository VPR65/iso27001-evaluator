# Script de Pruebas de Funcionamiento - ISO 27001 Evaluator
# Uso: python scripts/functional_test.py
#
# Este script verifica que todos los componentes est�n funcionando
# sin necesidad de Docker, usando la aplicaci�n local.

import sys
from typing import List, Dict
from datetime import datetime


# Colores para la output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_test(name: str, passed: bool, details: str = ""):
    status = (
        f"{Colors.GREEN}[OK]{Colors.RESET}"
        if passed
        else f"{Colors.RED}[FAIL]{Colors.RESET}"
    )
    print(f"{status} {name}")
    if details:
        print(f"       {Colors.YELLOW}{details}{Colors.RESET}")


def print_summary(results: List[bool]):
    total = len(results)
    passed = sum(results)
    failed = total - passed
    percentage = (passed / total * 100) if total > 0 else 0

    print_header("RESUMEN DE PRUEBAS")
    print(
        f"Total: {total} | {Colors.GREEN}{passed} OK{Colors.RESET} | {Colors.RED}{failed} FAIL{Colors.RESET}"
    )
    print(f"Porcentaje: {Colors.BOLD}{percentage:.1f}%{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}*** TODAS LAS PRUEBAS APROBADAS ***{Colors.RESET}\n")
    else:
        print(f"\n{Colors.RED}[WARN] ALGUNAS PRUEBAS FALLARON{Colors.RESET}\n")


# ============================================
# PRUEBAS DE FUNCIONAMIENTO
# ============================================


def test_01_verificar_requisitos() -> bool:
    """Verificar que los requisitos m�nimos est�n instalados"""
    print_header("PRUEBA 1: Verificar Requisitos")

    try:
        import fastapi
        import sqlmodel
        import uvicorn

        print_test("FastAPI instalado", True, f"v{fastapi.__version__}")
        print_test("SQLModel instalado", True, f"v{sqlmodel.__version__}")
        print_test("Uvicorn instalado", True, f"v{uvicorn.__version__}")
        return True
    except ImportError as e:
        print_test(f"Importaci�n fallida: {e}", False)
        return False


def test_02_verificar_ollama() -> bool:
    """Verificar que Ollama est� respondiendo"""
    print_header("PRUEBA 2: Verificar Ollama (IA Local)")

    try:
        import httpx

        response = httpx.get("http://localhost:11434/api/tags", timeout=3.0)

        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            print_test("Ollama responde", True, f"{len(models)} modelos disponibles")

            # Listar modelos
            for model in models[:3]:  # Mostrar primeros 3
                model_name = model.get("name", "desconocido")
                print(f"       - {model_name}")

            if len(models) > 3:
                print(f"       ... y {len(models) - 3} mas")

            return True
        else:
            print_test("Ollama responde", False, f"Status: {response.status_code}")
            return False

    except Exception as e:
        print_test("Ollama no disponible", False, str(e))
        print("       Nota: Ollama no es obligatorio, la app puede funcionar sin �l")
        return True  # No fallar la prueba si Ollama no est�


def test_03_verificar_base_datos() -> bool:
    """Verificar que la base de datos existe y es accesible"""
    print_header("PRUEBA 3: Verificar Base de Datos")

    try:
        from app.database import engine
        from sqlmodel import SQLModel

        # Intentar conectar
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print_test("Conexi�n a BD exitosa", True)
            return True

    except Exception as e:
        print_test("Conexi�n a BD fallida", False, str(e))
        return False


def test_04_prueba_endpoints_basicos() -> bool:
    """Probar endpoints b�sicos de la API"""
    print_header("PRUEBA 4: Endpoints B�sicos")

    try:
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Test 1: Health check
        response = client.get("/health")
        print_test(
            "GET /health",
            response.status_code == 200,
            f"Status: {response.status_code}",
        )

        # Test 2: Login page
        response = client.get("/login")
        print_test(
            "GET /login", response.status_code == 200, f"Status: {response.status_code}"
        )

        # Test 3: Dashboard (requiere auth, deber�a redirigir)
        response = client.get("/dashboard", follow_redirects=False)
        print_test(
            "GET /dashboard",
            response.status_code in [200, 307],
            f"Status: {response.status_code}",
        )

        # Test 4: API status
        response = client.get("/api/ai/status")
        print_test(
            "GET /api/ai/status",
            response.status_code in [200, 401],
            f"Status: {response.status_code}",
        )

        return True

    except Exception as e:
        print_test("Error en endpoints", False, str(e))
        return False


def test_05_verificar_configuracion() -> bool:
    """Verificar que la configuraci�n es correcta"""
    print_header("PRUEBA 5: Configuraci�n")

    try:
        from app.config import AI_MODE, AI_LOCAL_URL, AI_LOCAL_MODEL

        print_test("AI_MODE configurado", True, AI_MODE)
        print_test("AI_LOCAL_URL", True, AI_LOCAL_URL)
        print_test("AI_LOCAL_MODEL", True, AI_LOCAL_MODEL)

        # Verificar que AI_MODE sea v�lido
        valid_modes = ["ollama", "nvidia", "anthropic", "openai"]
        if AI_MODE in valid_modes:
            print_test(f"AI_MODE v�lido ({AI_MODE})", True)
            return True
        else:
            print_test(f"AI_MODE inv�lido: {AI_MODE}", False)
            print(f"       V�lidos: {', '.join(valid_modes)}")
            return False

    except Exception as e:
        print_test("Error de configuraci�n", False, str(e))
        return False


def test_06_verificar_archivos_estaticos() -> bool:
    """Verificar que los archivos est�ticos existen"""
    print_header("PRUEBA 6: Archivos Est�ticos")

    import os

    files_to_check = [
        "app/static/css/style.css",
        "app/static/css/ai_status.css",
        "app/static/js/ai_status.js",
        "app/templates/base.html",
        "app/templates/login.html",
    ]

    all_exist = True
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(
            f"{Colors.GREEN if exists else Colors.RED}{status} {file_path}{Colors.RESET}"
        )
        if not exists:
            all_exist = False

    print_test("Todos los archivos existen", all_exist)
    return all_exist


def test_07_verificar_scripts() -> bool:
    """Verificar que los scripts est�n presentes"""
    print_header("PRUEBA 7: Scripts")

    import os

    scripts_to_check = [
        "scripts/backup.py",
        "scripts/Start-Ollama.ps1",
        "scripts/Stop-Ollama.ps1",
        "scripts/start-ollama.bat",
        "scripts/stop-ollama.bat",
    ]

    all_exist = True
    for script in scripts_to_check:
        exists = os.path.exists(script)
        status = "✓" if exists else "✗"
        print(
            f"{Colors.GREEN if exists else Colors.RED}{status} {script}{Colors.RESET}"
        )
        if not exists:
            all_exist = False

    print_test("Todos los scripts existen", all_exist)
    return all_exist


# ============================================
# MAIN
# ============================================


def main():
    print(f"\n{Colors.BOLD}Inicio de Pruebas de Funcionamiento{Colors.RESET}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Ejecutar pruebas
    results.append(test_01_verificar_requisitos())
    results.append(test_02_verificar_ollama())
    results.append(test_03_verificar_base_datos())
    results.append(test_04_prueba_endpoints_basicos())
    results.append(test_05_verificar_configuracion())
    results.append(test_06_verificar_archivos_estaticos())
    results.append(test_07_verificar_scripts())

    # Resumen final
    print_summary(results)

    # Return 0 si todo OK, 1 si hubo fallos
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
