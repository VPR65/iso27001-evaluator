# ISO 27001 Evaluator - Backup Automático Avanzado
# Uso: python scripts/auto_backup.py
# Descripción: Sistema de backups automáticos con rotación y verificación

import os
import sys
import zipfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import json

# Configuración
BACKUP_DIR = Path("backups/auto")
RETENTION_DAYS = 7
MAX_BACKUPS = 10
BACKUP_SOURCES = [
    "iso27001.db",  # SQLite DB
    "uploads/",  # Evidencias
    ".env",  # Configuración
    "docker-compose.yml",  # Docker config
]


def print_status(message: str, status: str = "INFO"):
    """Imprime mensaje con estado"""
    colors = {
        "INFO": "\033[94m",
        "OK": "\033[92m",
        "WARN": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m",
    }
    print(f"{colors.get(status, '')}[{status}]{colors['RESET']} {message}")


def create_backup_directory() -> Path:
    """Crea directorio de backups si no existe"""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print_status(f"Directorio creado: {BACKUP_DIR}", "OK")
    return BACKUP_DIR


def backup_database(backup_path: Path) -> bool:
    """Realiza backup de la base de datos"""
    try:
        # SQLite
        if os.path.exists("iso27001.db"):
            shutil.copy2("iso27001.db", backup_path / "iso27001.db")
            print_status("SQLite DB respaldada", "OK")
            return True

        # PostgreSQL (Docker)
        if os.path.exists("docker-compose.yml"):
            os.system(
                "docker-compose exec -T db pg_dump -U iso27001 iso27001 > backup.sql 2>/dev/null"
            )
            if os.path.exists("backup.sql"):
                shutil.move("backup.sql", backup_path / "database.sql")
                print_status("PostgreSQL DB respaldada", "OK")
                return True

        print_status("No se encontró base de datos", "WARN")
        return False
    except Exception as e:
        print_status(f"Error backup DB: {e}", "ERROR")
        return False


def backup_uploads(backup_path: Path) -> bool:
    """Realiza backup de uploads"""
    try:
        if os.path.exists("uploads"):
            shutil.copytree("uploads", backup_path / "uploads", dirs_exist_ok=True)
            file_count = sum(1 for _ in backup_path.glob("uploads/**/*") if _.is_file())
            print_status(f"Uploads respaldados ({file_count} archivos)", "OK")
            return True
        else:
            print_status("No hay directorio uploads", "WARN")
            return True  # No es error crítico
    except Exception as e:
        print_status(f"Error backup uploads: {e}", "ERROR")
        return False


def backup_config(backup_path: Path) -> bool:
    """Realiza backup de configuración"""
    try:
        config_dir = backup_path / "config"
        config_dir.mkdir(exist_ok=True)

        config_files = [".env", "docker-compose.yml", ".env.docker"]
        copied = 0

        for file in config_files:
            if os.path.exists(file):
                shutil.copy2(file, config_dir / file)
                copied += 1

        print_status(f"Configuración respaldada ({copied} archivos)", "OK")
        return True
    except Exception as e:
        print_status(f"Error backup config: {e}", "ERROR")
        return False


def create_backup_archive(backup_path: Path, timestamp: str) -> Path:
    """Crea archivo ZIP con el backup"""
    try:
        zip_file = backup_path.parent / f"backup_{timestamp}.zip"

        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in backup_path.iterdir():
                if item.is_dir():
                    for file in item.rglob("*"):
                        arcname = file.relative_to(backup_path.parent)
                        zipf.write(file, arcname)
                else:
                    zipf.write(item, item.name)

        # Eliminar directorio temporal
        shutil.rmtree(backup_path)

        size_mb = zip_file.stat().st_size / (1024 * 1024)
        print_status(f"Backup creado: {zip_file.name} ({size_mb:.2f} MB)", "OK")
        return zip_file
    except Exception as e:
        print_status(f"Error creando ZIP: {e}", "ERROR")
        return None


def cleanup_old_backups() -> Dict:
    """Limpia backups antiguos según retención"""
    stats = {"deleted": 0, "kept": 0}

    try:
        cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
        backups = sorted(BACKUP_DIR.parent.glob("backup_*.zip"))

        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for i, backup in enumerate(backups):
            # Mantener al menos MAX_BACKUPS recientes
            if i < MAX_BACKUPS:
                stats["kept"] += 1
                continue

            # Eliminar por antigüedad
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            if mtime < cutoff_date:
                backup.unlink()
                stats["deleted"] += 1
                print_status(f"Eliminado backup antiguo: {backup.name}", "INFO")

        # Respetar máximo de backups
        if len(backups) > MAX_BACKUPS:
            for backup in backups[MAX_BACKUPS:]:
                backup.unlink()
                stats["deleted"] += 1

        print_status(
            f"Limpieza: {stats['deleted']} eliminados, {stats['kept']} conservados",
            "OK",
        )
        return stats
    except Exception as e:
        print_status(f"Error en limpieza: {e}", "ERROR")
        return stats


def verify_backup(backup_path: Path) -> bool:
    """Verifica integridad del backup"""
    try:
        if not backup_path.exists():
            return False

        with zipfile.ZipFile(backup_path, "r") as zipf:
            # Verificar que no esté corrupto
            bad_file = zipf.testzip()
            if bad_file:
                print_status(f"Backup corrupto: {bad_file}", "ERROR")
                return False

        print_status("Backup verificado (íntegro)", "OK")
        return True
    except Exception as e:
        print_status(f"Error verificando backup: {e}", "ERROR")
        return False


def run_auto_backup() -> Dict:
    """Ejecuta backup automático completo"""
    print_status("=" * 50, "INFO")
    print_status("ISO 27001 - Backup Automático", "INFO")
    print_status("=" * 50, "INFO")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = create_backup_directory() / f"backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)

    results = {
        "timestamp": timestamp,
        "database": False,
        "uploads": False,
        "config": False,
        "zip_file": None,
        "verified": False,
    }

    # Realizar backups
    results["database"] = backup_database(backup_path)
    results["uploads"] = backup_uploads(backup_path)
    results["config"] = backup_config(backup_path)

    # Crear archivo ZIP
    if any([results["database"], results["uploads"], results["config"]]):
        zip_file = create_backup_archive(backup_path, timestamp)
        if zip_file:
            results["zip_file"] = str(zip_file)
            results["verified"] = verify_backup(zip_file)

    # Limpieza
    cleanup_old_backups()

    # Resumen
    print_status("=" * 50, "INFO")
    print_status("Resumen del Backup", "INFO")
    print_status("=" * 50, "INFO")
    print_status(
        f"Database: {'OK' if results['database'] else 'FAIL'}",
        "OK" if results["database"] else "ERROR",
    )
    print_status(
        f"Uploads: {'OK' if results['uploads'] else 'SKIP'}",
        "OK" if results["uploads"] else "WARN",
    )
    print_status(
        f"Config: {'OK' if results['config'] else 'SKIP'}",
        "OK" if results["config"] else "WARN",
    )
    print_status(
        f"Verificado: {'SI' if results['verified'] else 'NO'}",
        "OK" if results["verified"] else "WARN",
    )

    if results["zip_file"]:
        print_status(f"Archivo: {results['zip_file']}", "INFO")

    return results


if __name__ == "__main__":
    try:
        results = run_auto_backup()
        sys.exit(0 if results["verified"] else 1)
    except KeyboardInterrupt:
        print_status("\nCancelado por usuario", "WARN")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error crítico: {e}", "ERROR")
        sys.exit(1)
