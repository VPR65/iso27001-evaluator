#!/usr/bin/env python3
"""
Scripts de gestion de backups para ISO27001 Evaluator
Uso: python scripts/backup.py [comando]
Comandos:
  backup       - Crea backup completo (DB + uploads)
  backup --db  - Solo base de datos
  restore FILE - Restaura desde archivo ZIP
  list         - Lista backups disponibles
  clean        - Limpia backups antiguos
"""

import os, sys, zipfile, shutil, sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
DB_FILE = os.path.join(BASE_DIR, "iso27001.db")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
KEEP_AUTO = 10
KEEP_DEPLOY = 10
KEEP_DAILY = 30


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup_name(prefix="backup"):
    return f"{prefix}_{timestamp()}.zip"


def create_backup(items: list, prefix: str) -> str:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    filepath = os.path.join(BACKUP_DIR, backup_name(prefix))
    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
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
    print(f"Backup creado: {filepath}")
    return filepath


def backup_all():
    items = []
    if os.path.exists(DB_FILE):
        items.append((DB_FILE, "iso27001.db"))
    if os.path.exists(UPLOADS_DIR):
        items.append((UPLOADS_DIR, "uploads"))
    return create_backup(items, "backup_full")


def backup_db():
    return create_backup([(DB_FILE, "iso27001.db")], "backup_db")


def backup_uploads():
    return create_backup([(UPLOADS_DIR, "uploads")], "backup_uploads")


def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print("No hay backups.")
        return
    for root, dirs, files in os.walk(BACKUP_DIR):
        for f in sorted(files):
            if f.endswith(".zip"):
                full = os.path.join(root, f)
                size = os.path.getsize(full) / 1024
                mtime = datetime.fromtimestamp(os.path.getmtime(full))
                rel = os.path.relpath(full, BACKUP_DIR)
                print(f"  {rel}  {size:.1f} KB  {mtime.strftime('%Y-%m-%d %H:%M')}")


def restore_backup(filepath: str):
    if not os.path.exists(filepath):
        print(f"ERROR: Backup no encontrado: {filepath}")
        return False

    print(f"Restaurando desde: {filepath}")
    with zipfile.ZipFile(filepath, "r") as zf:
        zf.extractall(BASE_DIR)
    print("Restauracion completada.")
    return True


def clean_old_backups():
    if not os.path.exists(BACKUP_DIR):
        return
    for subdir in ["auto", "deploy"]:
        subdir_path = os.path.join(BACKUP_DIR, subdir)
        if not os.path.exists(subdir_path):
            continue
        files = sorted(
            [f for f in os.listdir(subdir_path) if f.endswith(".zip")],
            key=lambda x: os.path.getmtime(os.path.join(subdir_path, x)),
            reverse=True,
        )
        keep = KEEP_AUTO if subdir == "auto" else KEEP_DEPLOY
        for f in files[keep:]:
            os.remove(os.path.join(subdir_path, f))
            print(f"Eliminado: {f}")


def auto_backup():
    os.makedirs(os.path.join(BACKUP_DIR, "auto"), exist_ok=True)
    filepath = os.path.join(BACKUP_DIR, "auto", backup_name("auto"))
    items = [(DB_FILE, "iso27001.db")]
    if os.path.exists(UPLOADS_DIR):
        items.append((UPLOADS_DIR, "uploads"))
    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
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
    print(f"Auto-backup: {filepath}")
    clean_old_backups()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "backup"

    if cmd == "backup":
        backup_all()
    elif cmd == "backup-db":
        backup_db()
    elif cmd == "backup-uploads":
        backup_uploads()
    elif cmd == "restore" and len(sys.argv) >= 3:
        restore_backup(sys.argv[2])
    elif cmd == "list":
        list_backups()
    elif cmd == "clean":
        clean_old_backups()
    elif cmd == "auto":
        auto_backup()
    else:
        print(__doc__)
