#!/usr/bin/env python
"""
Sistema de Monitoreo - ISO 27001 & ITIL Evaluator
Monitorea salud del sistema: uptime, espacio en disco, estado de backups, servicios

Uso: python scripts/monitor.py
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import shutil

# Agregar el path base para imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "monitor.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitor del sistema"""

    def __init__(self):
        self.base_dir = BASE_DIR
        self.start_time = datetime.now()
        self.alerts: List[Dict[str, Any]] = []

    def check_uptime(self) -> Dict[str, Any]:
        """Verificar tiempo de uptime"""
        uptime = datetime.now() - self.start_time
        return {
            "status": "OK",
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split(".")[0],
            "start_time": self.start_time.isoformat(),
        }

    def check_disk_space(self, threshold_percent: float = 90.0) -> Dict[str, Any]:
        """Verificar espacio en disco"""
        try:
            # Obtener estadisticas del disco
            if sys.platform == "win32":
                # Windows
                import ctypes

                free_bytes = ctypes.c_ulonglong()
                total_bytes = ctypes.c_ulonglong()
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(str(self.base_dir)),
                    None,
                    ctypes.pointer(total_bytes),
                    ctypes.pointer(free_bytes),
                )
                total = total_bytes.value
                free = free_bytes.value
            else:
                # Linux/Mac
                stat = shutil.disk_usage(str(self.base_dir))
                total = stat.total
                free = stat.free

            used = total - free
            percent_used = (used / total) * 100 if total > 0 else 0

            status = "CRITICAL" if percent_used >= threshold_percent else "OK"

            if status == "CRITICAL":
                self.alerts.append(
                    {
                        "type": "DISK_SPACE",
                        "severity": "CRITICAL",
                        "message": f"Espacio en disco: {percent_used:.1f}% usado (umbral: {threshold_percent}%)",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            return {
                "status": status,
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "percent_used": round(percent_used, 2),
                "threshold_percent": threshold_percent,
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def check_backup_status(self) -> Dict[str, Any]:
        """Verificar estado de backups"""
        backup_dir = self.base_dir / "backups" / "auto"
        backup_old_dir = self.base_dir / "backups"

        # Buscar backups
        backups = []

        for directory in [backup_dir, backup_old_dir]:
            if directory.exists():
                for f in directory.iterdir():
                    if f.is_file() and (
                        f.suffix == ".zip" or "backup" in f.name.lower()
                    ):
                        try:
                            stat = f.stat()
                            backups.append(
                                {
                                    "path": str(f),
                                    "name": f.name,
                                    "size_bytes": stat.st_size,
                                    "created": datetime.fromtimestamp(stat.st_ctime),
                                    "modified": datetime.fromtimestamp(stat.st_mtime),
                                }
                            )
                        except Exception:
                            pass

        # Ordenar por fecha (mas reciente primero)
        backups.sort(key=lambda x: x["modified"], reverse=True)

        # Verificar si hay backup reciente (ultimas 24 horas)
        now = datetime.now()
        recent_backup = None
        for b in backups:
            if (now - b["modified"]).total_seconds() < 86400:  # 24 horas
                recent_backup = b
                break

        status = "OK" if recent_backup else "WARNING"

        if status == "WARNING":
            self.alerts.append(
                {
                    "type": "BACKUP",
                    "severity": "WARNING",
                    "message": "No hay backup en las ultimas 24 horas",
                    "timestamp": now.isoformat(),
                }
            )

        return {
            "status": status,
            "total_backups": len(backups),
            "latest_backup": {
                "name": backups[0]["name"] if backups else None,
                "created": backups[0]["modified"].isoformat() if backups else None,
                "size_mb": round(backups[0]["size_bytes"] / (1024**2), 2)
                if backups
                else None,
            }
            if backups
            else None,
            "backups_last_24h": sum(
                1 for b in backups if (now - b["modified"]).total_seconds() < 86400
            ),
            "backups_last_7d": sum(
                1 for b in backups if (now - b["modified"]).total_seconds() < 604800
            ),
        }

    def check_database(self) -> Dict[str, Any]:
        """Verificar conexion a base de datos"""
        try:
            from app.database import engine
            from sqlmodel import text

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            return {"status": "OK", "connection": "success"}
        except Exception as e:
            self.alerts.append(
                {
                    "type": "DATABASE",
                    "severity": "CRITICAL",
                    "message": f"Error deconexion a BD: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return {"status": "ERROR", "error": str(e)}

    def check_ollama(self) -> Dict[str, Any]:
        """Verificar disponibilidad de Ollama"""
        try:
            import requests

            response = requests.get("http://localhost:11434/api/tags", timeout=5)

            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return {
                    "status": "OK",
                    "available": True,
                    "models_count": len(models),
                    "models": [m["name"] for m in models[:5]],  # Primeros 5
                }
        except Exception:
            pass

        return {
            "status": "WARNING",
            "available": False,
            "message": "Ollama no disponible",
        }

    def check_app_health(self) -> Dict[str, Any]:
        """Verificar salud de la aplicacion"""
        try:
            import requests

            # Asumir que la app corre en puerto 8000
            response = requests.get("http://localhost:8000/health", timeout=5)

            if response.status_code == 200:
                return {
                    "status": "OK",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                }
        except Exception:
            pass

        return {"status": "WARNING", "message": "App no responde en puerto 8000"}

    def get_full_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        self.alerts = []  # Resetear alerts

        return {
            "timestamp": datetime.now().isoformat(),
            "uptime": self.check_uptime(),
            "disk_space": self.check_disk_space(),
            "backups": self.check_backup_status(),
            "database": self.check_database(),
            "ollama": self.check_ollama(),
            "app_health": self.check_app_health(),
            "alerts": self.alerts,
            "overall_status": "CRITICAL"
            if any(a["severity"] == "CRITICAL" for a in self.alerts)
            else "WARNING"
            if any(a["severity"] == "WARNING" for a in self.alerts)
            else "OK",
        }

    def print_status(self, status: Dict[str, Any]) -> None:
        """Imprimir estado en formato legible"""
        print("\n" + "=" * 60)
        print("  SISTEMA - ISO 27001 & ITIL Evaluator".center(60))
        print("=" * 60)
        print(f"Timestamp: {status['timestamp']}")
        print(f"Estado General: {status['overall_status']}")
        print()

        # Uptime
        uptime = status.get("uptime", {})
        print(f"Uptime: {uptime.get('uptime_formatted', 'N/A')}")

        # Disco
        disk = status.get("disk_space", {})
        if disk.get("status") == "OK":
            print(
                f"Disco: {disk.get('percent_used', 0):.1f}% usado ({disk.get('free_gb', 0):.1f} GB libres)"
            )
        else:
            print(f"Disco: {disk.get('status')} - {disk.get('error', 'Error')}")

        # Backups
        backups = status.get("backups", {})
        print(
            f"Backups: {backups.get('total_backups', 0)} total, "
            f"{backups.get('backups_last_7d', 0)} en 7 dias"
        )
        if backups.get("latest_backup"):
            print(
                f"  Ultimo: {backups['latest_backup']['name']} "
                f"({backups['latest_backup']['size_mb']} MB)"
            )

        # Base de datos
        db = status.get("database", {})
        print(f"Base de Datos: {db.get('status', 'ERROR')}")

        # Ollama
        ollama = status.get("ollama", {})
        if ollama.get("available"):
            print(f"Ollama: OK ({ollama.get('models_count', 0)} modelos)")
        else:
            print(f"Ollama: No disponible")

        # App
        app = status.get("app_health", {})
        if app.get("status") == "OK":
            print(f"App: OK ({app.get('response_time_ms', 0):.0f}ms)")
        else:
            print(f"App: {app.get('status', 'ERROR')}")

        # Alertas
        alerts = status.get("alerts", [])
        if alerts:
            print("\nALERTAS:")
            for alert in alerts:
                severity = alert.get("severity", "INFO")
                color_code = "\033[91m" if severity == "CRITICAL" else "\033[93m"
                reset_code = "\033[0m"
                print(f"  [{severity}] {alert.get('message', '')}")

        print("=" * 60)


def main():
    """Funcion principal"""
    monitor = SystemMonitor()
    status = monitor.get_full_status()
    monitor.print_status(status)

    # Guardar estado en archivo JSON (opcional)
    status_file = BASE_DIR / "logs" / "last_status.json"
    try:
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, default=str)
        logger.info(f"Estado guardado en {status_file}")
    except Exception as e:
        logger.error(f"Error guardando estado: {e}")

    # Retornar codigo de exito/fracaso
    return 0 if status["overall_status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
