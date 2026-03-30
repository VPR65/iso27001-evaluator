# Script de Pruebas de Funcionamiento - ISO 27001 Evaluator
# Uso: python scripts/qa_test.py

import sys
from datetime import datetime


def print_header(text):
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")


def print_test(name, passed, details=""):
    status = "[OK]" if passed else "[FAIL]"
    color_status = "\033[92m" if passed else "\033[91m"
    print(f"{color_status}{status}\033[0m {name}")
    if details:
        print(f"       \033[93m{details}\033[0m")


def test_01_requisitos():
    print_header("PRUEBA 1: Requisitos")
    try:
        import fastapi, sqlmodel, uvicorn

        print_test("FastAPI", True, fastapi.__version__)
        print_test("SQLModel", True, sqlmodel.__version__)
        print_test("Uvicorn", True, uvicorn.__version__)
        return True
    except Exception as e:
        print_test("Error", False, str(e))
        return False


def test_02_ollama():
    print_header("PRUEBA 2: Ollama (IA)")
    try:
        import httpx

        r = httpx.get("http://localhost:11434/api/tags", timeout=3.0)
        if r.status_code == 200:
            models = r.json().get("models", [])
            print_test("Ollama OK", True, f"{len(models)} modelos")
            return True
        return False
    except:
        print_test("Ollama no disponible", False, "No es obligatorio")
        return True  # No falla


def test_03_db():
    print_header("PRUEBA 3: Base de Datos")
    try:
        from app.database import engine
        from sqlmodel import SQLModel

        with engine.connect() as conn:
            print_test("Conexion BD", True)
            return True
    except Exception as e:
        print_test("Error BD", False, str(e))
        return False


def test_04_endpoints():
    print_header("PRUEBA 4: Endpoints")
    try:
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        r = client.get("/health")
        print_test("GET /health", r.status_code == 200, str(r.status_code))

        r = client.get("/login")
        print_test("GET /login", r.status_code == 200, str(r.status_code))

        return True
    except Exception as e:
        print_test("Error", False, str(e))
        return False


def test_05_config():
    print_header("PRUEBA 5: Configuracion")
    try:
        from app.config import AI_MODE, AI_LOCAL_MODEL

        print_test("AI_MODE", True, AI_MODE)
        print_test("AI_LOCAL_MODEL", True, AI_LOCAL_MODEL)
        return True
    except Exception as e:
        print_test("Error", False, str(e))
        return False


def main():
    print(
        f"\nPruebas de Funcionamiento - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    )

    tests = [
        test_01_requisitos,
        test_02_ollama,
        test_03_db,
        test_04_endpoints,
        test_05_config,
    ]

    results = [test() for test in tests]
    passed = sum(results)
    total = len(results)

    print_header("RESUMEN")
    print(f"Total: {total} | OK: {passed} | Fail: {total - passed}")
    print(f"Porcentaje: {passed / total * 100:.1f}%\n")

    if passed == total:
        print("*** TODAS LAS PRUEBAS APROBADAS ***\n")
    else:
        print("[WARN] ALGUNAS PRUEBAS FALLARON\n")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
