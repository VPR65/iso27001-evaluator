#!/usr/bin/env python3
"""
Rollback rapido del codigo.
Uso: python scripts/rollback.py [version]
Sin argumentos: rollback al tag anterior.
Con version: rollback a la version especificada (ej: v1.0.0)
"""

import os, sys, subprocess, zipfile, shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
DB_FILE = os.path.join(BASE_DIR, "iso27001.db")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")


def get_current_tag():
    try:
        tags = (
            subprocess.run(
                ["git", "tag", "--sort=-v:refname"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split("\n")
        )
        return tags[0] if tags and tags[0] else "none"
    except:
        return "none"


def get_previous_tag():
    try:
        tags = (
            subprocess.run(
                ["git", "tag", "--sort=-v:refname"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split("\n")
        )
        return tags[1] if len(tags) > 1 else None
    except:
        return None


def run(cmd, cwd=BASE_DIR):
    print(f"  > {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.strip())
    if r.returncode != 0 and r.stderr:
        print(r.stderr.strip())
    return r.returncode == 0


def rollback(target_tag: str = None):
    print("=" * 50)
    print("  ROLLBACK - ISO27001 Evaluator")
    print("=" * 50)

    if target_tag is None:
        target_tag = get_previous_tag()
        if not target_tag:
            print("ERROR: No hay tags anteriores para hacer rollback.")
            return

    current = get_current_tag()
    print(f"Rollback: {current} -> {target_tag}")

    confirm = input("Continuar? [s/N]: ").strip().lower()
    if confirm not in ("s", "si", "si"):
        print("Cancelado.")
        return

    print("\n[1/5] Creando backup pre-rollback...")
    os.makedirs(os.path.join(BACKUP_DIR, "deploy"), exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pre_backup = os.path.join(BACKUP_DIR, "deploy", f"pre_rollback_{timestamp}.zip")
    items = [(DB_FILE, "iso27001.db")]
    if os.path.exists(UPLOADS_DIR):
        items.append((UPLOADS_DIR, "uploads"))
    with zipfile.ZipFile(pre_backup, "w", zipfile.ZIP_DEFLATED) as zf:
        for item_path, arcname in items:
            if os.path.exists(item_path):
                if os.path.isdir(item_path):
                    for root, dirs, files in os.walk(item_path):
                        for file in files:
                            full = os.path.join(root, file)
                            rel = os.path.relpath(full, BASE_DIR)
                            zf.write(full, rel)
                else:
                    zf.write(item_path, os.path.relpath(item_path, BASE_DIR))
    print(f"  Backup pre-rollback: {pre_backup}")

    print("\n[2/5] Checkout a tag anterior...")
    run(f"git checkout {target_tag}")

    print("\n[3/5] Verificando archivo de base de datos...")
    db_ok = os.path.exists(DB_FILE)
    print(f"  DB existe: {db_ok}")

    print("\n[4/5] Verificando que uploads es accesible...")
    uploads_ok = os.path.exists(UPLOADS_DIR)
    print(f"  Uploads existe: {uploads_ok}")

    print("\n[5/5] Verificando salud del sistema...")
    try:
        import requests

        r = requests.get("http://localhost:8000/health", timeout=5)
        if r.status_code == 200:
            print("  Health check OK")
        else:
            print(f"  Health check: {r.status_code}")
    except:
        print("  (No se pudo verificar - asegurate de que la app este corriendo)")

    print("\n" + "=" * 50)
    print(f"  ROLLBACK COMPLETADO")
    print(f"  Version actual: {target_tag}")
    print(f"  Si la app no responde: uvicorn app.main:app --reload")
    print("=" * 50)


def list_tags():
    print("Tags disponibles:")
    try:
        tags = (
            subprocess.run(
                ["git", "tag", "--sort=-v:refname"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split("\n")
        )
        for t in tags:
            if t:
                print(f"  {t}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == "--list":
        list_tags()
    elif cmd and cmd.startswith("v"):
        rollback(cmd)
    else:
        rollback()
