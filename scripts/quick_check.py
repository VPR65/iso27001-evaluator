#!/usr/bin/env python
"""
Verificacion Rapida del Sistema - ISO 27001 & ITIL Evaluator
Script unico para verificar todo el sistema rapidamente

Uso: python scripts/quick_check.py [--full] [--json]
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Agregar el path base para imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def check_python_path():
    """Verificar PYTHONPATH"""
    try:
        import app.config

        return True, "PYTHONPATH OK"
    except ImportError as e:
        return False, f"PYTHONPATH ERROR: {e}"


def check_dependencies():
    """Verificar dependencias"""
    try:
        import fastapi
        import sqlmodel
        import uvicorn

        return True, f"FastAPI {fastapi.__version__}, SQLModel {sqlmodel.__version__}"
    except ImportError as e:
        return False, f"Dependencias ERROR: {e}"


def check_database():
    """Verificar base de datos"""
    try:
        from app.database import engine
        from sqlmodel import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "BD Conectada"
    except Exception as e:
        return False, f"BD ERROR: {e}"


def check_ollama():
    """Verificar Ollama"""
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            return True, f"Ollama OK ({len(models)} modelos)"
        return False, "Ollama responde pero sin modelos"
    except Exception:
        return False, "Ollama no disponible (opcional)"


def check_app_health():
    """Verificar aplicacion"""
    try:
        import requests

        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            return True, f"App OK ({response.elapsed.total_seconds() * 1000:.0f}ms)"
        return False, f"App ERROR {response.status_code}"
    except Exception:
        return False, "App no responde (puede estar apagada)"


def check_backups():
    """Verificar backups"""
    backup_dir = BASE_DIR / "backups" / "auto"
    if not backup_dir.exists():
        backup_dir = BASE_DIR / "backups"

    if not backup_dir.exists():
        return False, "Directorio backups no existe"

    now = datetime.now()
    backups_7d = 0

    for f in backup_dir.iterdir():
        if f.is_file() and f.suffix == ".zip":
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if (now - mtime).total_seconds() < 604800:
                    backups_7d += 1
            except Exception:
                pass

    if backups_7d > 0:
        return True, f"{backups_7d} backups en 7 dias"
    return False, "Sin backups recientes (7 dias)"


def check_disk_space(threshold=90):
    """Verificar espacio en disco"""
    try:
        import shutil

        stat = shutil.disk_usage(str(BASE_DIR))
        percent_used = (stat.total - stat.free) / stat.total * 100
        if percent_used >= threshold:
            return False, f"Disco {percent_used:.1f}% (critico)"
        return True, f"Disco {percent_used:.1f}% OK"
    except Exception as e:
        return False, f"Disco ERROR: {e}"


def run_quick_check(full=False, as_json=False):
    """Ejecutar verificacion rapida"""
    checks = [
        ("PYTHONPATH", check_python_path),
        ("Dependencias", check_dependencies),
        ("Base de Datos", check_database),
        ("Ollama (IA)", check_ollama),
        ("Aplicacion", check_app_health),
        ("Backups", check_backups),
        ("Disco", check_disk_space),
    ]

    results = []
    all_ok = True

    for name, check_func in checks:
        try:
            ok, message = check_func()
            results.append({"name": name, "ok": ok, "message": message})
            if not ok and name not in ["Ollama (IA)", "Aplicacion"]:
                all_ok = False
        except Exception as e:
            results.append({"name": name, "ok": False, "message": f"ERROR: {e}"})
            all_ok = False

    if as_json:
        print(
            json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "all_ok": all_ok,
                    "checks": results,
                },
                indent=2,
            )
        )
    else:
        print("")
        print("=" * 60)
        print("  VERIFICACION RAPIDA - ISO 27001 Evaluator".center(60))
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("")

        for result in results:
            status = "[OK]" if result["ok"] else "[FAIL]"
            color = "\033[92m" if result["ok"] else "\033[91m"
            reset = "\033[0m"
            print(f"{color}{status}{reset} {result['name']:15} - {result['message']}")

        print("")
        overall = "TODO OK" if all_ok else "REVISAR"
        print(f"Estado: {overall}")
        print("=" * 60)

    return 0 if all_ok else 1


def main():
    parser = argparse.ArgumentParser(description="Verificacion rapida del sistema")
    parser.add_argument("--full", action="store_true", help="Verificacion completa")
    parser.add_argument("--json", action="store_true", help="Salida en JSON")
    args = parser.parse_args()

    return run_quick_check(full=args.full, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
