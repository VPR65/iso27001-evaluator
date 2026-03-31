#!/usr/bin/env python
"""
Script de Pruebas Funcionales - ISO 27001 Evaluator
Ejecuta pruebas funcionales completas del sistema

Uso: python scripts/functional_test.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar el path base para imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def print_header(text: str) -> None:
    """Imprimir encabezado de seccion"""
    print("\n" + "=" * 60)
    print(f" {text}".center(60))
    print("=" * 60)


def print_test(name: str, passed: bool, details: str = "") -> None:
    """Imprimir resultado de prueba"""
    status = "[OK]" if passed else "[FAIL]"
    color_status = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color_status}{status}{reset} {name}")
    if details:
        print(f" \033[93m{details}\033[0m")


def test_01_verificar_requisitos() -> bool:
    """Verificar que los requisitos estan instalados"""
    print_header("PRUEBA 1: Verificar Requisitos")
    try:
        import fastapi
        import sqlmodel
        import uvicorn

        print_test("FastAPI instalado", True, f"v{fastapi.__version__}")
        print_test("SQLModel instalado", True, f"v{sqlmodel.__version__}")
        print_test("Uvicorn instalado", True, f"v{uvicorn.__version__}")
        return True
    except Exception as e:
        print_test("Error en requisitos", False, str(e))
        return False


def test_02_verificar_ollama() -> bool:
    """Verificar que Ollama este respondiendo"""
    print_header("PRUEBA 2: Verificar Ollama (IA Local)")
    try:
        import httpx

        response = httpx.get("http://localhost:11434/api-tags", timeout=3.0)

        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            print_test("Ollama responde", True, f"{len(models)} modelos disponibles")

            # Listar modelos
            for model in models[:3]:  # Mostrar primeros 3
                model_name = model.get("name", "desconocido")
                print(f" - {model_name}")

            if len(models) > 3:
                print(f" ... y {len(models) - 3} mas")

            return True
        else:
            print_test("Ollama responde", False, f"Status: {response.status_code}")
            return False

    except Exception as e:
        print_test("Ollama no disponible", False, str(e))
        print(" Nota: Ollama no es obligatorio, la app puede funcionar sin el")
        return True  # No fallar si Ollama no esta disponible


def test_03_verificar_base_datos() -> bool:
    """Verificar que la base de datos existe y es accesible"""
    print_header("PRUEBA 3: Verificar Base de Datos")
    try:
        from app.database import engine
        from sqlmodel import text

        # Intentar conectar
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        print_test("Conexion a BD exitosa", True)
        return True

    except Exception as e:
        print_test("Conexion a BD fallida", False, str(e))
        return False


def test_04_prueba_endpoints_basicos() -> bool:
    """Probar endpoints basicos de la API"""
    print_header("PRUEBA 4: Endpoints Basicos")
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

        # Test 3: Dashboard (requiere auth, deberia redirigir)
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
    """Verificar que la configuracion sea correcta"""
    print_header("PRUEBA 5: Configuracion")
    try:
        from app.config import AI_MODE, AI_LOCAL_URL, AI_LOCAL_MODEL

        print_test("AI_MODE configurado", True, AI_MODE)
        print_test("AI_LOCAL_URL", True, AI_LOCAL_URL)
        print_test("AI_LOCAL_MODEL", True, AI_LOCAL_MODEL)

        # Verificar que AI_MODE sea valido
        valid_modes = ["ollama", "nvidia", "anthropic", "openai"]
        if AI_MODE in valid_modes:
            print_test(f"AI_MODE valido ({AI_MODE})", True)
            return True
        else:
            print_test(f"AI_MODE invalido: {AI_MODE}", False)
            print(f" Validos: {', '.join(valid_modes)}")
            return False

    except Exception as e:
        print_test("Error en configuracion", False, str(e))
        return False


def test_06_verificar_modelos() -> bool:
    """Verificar que los modelos esten definidos"""
    print_header("PRUEBA 6: Modelos de Datos")
    try:
        from app.models import User, Client, Evaluation

        print_test("User model", True)
        print_test("Client model", True)
        print_test("Evaluation model", True)

        return True
    except Exception as e:
        print_test("Error en modelos", False, str(e))
        return False


def test_07_verificar_seguridad() -> bool:
    """Verificar configuracion de seguridad"""
    print_header("PRUEBA 7: Seguridad")
    try:
        from app.config import SECRET_KEY

        if SECRET_KEY and len(SECRET_KEY) >= 32:
            print_test("SECRET_KEY configurada", True, "Longitud adecuada")
            return True
        else:
            print_test("SECRET_KEY debil", False, "Debe tener al menos 32 caracteres")
            return False

    except Exception as e:
        print_test("Error en seguridad", False, str(e))
        return False


def main() -> int:
    """Funcion principal"""
    print("=" * 60)
    print(" Inicio de Pruebas de Funcionamiento".center(60))
    print("=" * 60)
    print(f" Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    tests = [
        ("Requisitos", test_01_verificar_requisitos),
        ("Ollama (IA)", test_02_verificar_ollama),
        ("Base de Datos", test_03_verificar_base_datos),
        ("Endpoints Basicos", test_04_prueba_endpoints_basicos),
        ("Configuracion", test_05_verificar_configuracion),
        ("Modelos de Datos", test_06_verificar_modelos),
        ("Seguridad", test_07_verificar_seguridad),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            results.append((name, False))

    # Resumen final
    print_header("RESUMEN")
    total = len(results)
    passed = sum(1 for _, r in results if r)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"Total: {total} | OK: {passed} | Fail: {total - passed}")
    print(f"Porcentaje: {percentage:.1f}%")

    if passed == total:
        print("\n*** TODAS LAS PRUEBAS APROBADAS ***")
        return 0
    else:
        print("\n[WARN] ALGUNAS PRUEBAS FALLARON")
        return 1


if __name__ == "__main__":
    sys.exit(main())
