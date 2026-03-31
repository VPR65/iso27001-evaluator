#!/usr/bin/env python
"""
Gestor de Alertas - ISO 27001 & ITIL Evaluator
Gestiona alertas del sistema: logging, notificaciones, historial

Uso: python scripts/alert_manager.py [status|history|clear]
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

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
        logging.FileHandler(LOG_DIR / "alerts.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Niveles de severidad de alertas"""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Tipos de alertas"""

    SYSTEM = "SYSTEM"
    BACKUP = "BACKUP"
    DATABASE = "DATABASE"
    SECURITY = "SECURITY"
    APPLICATION = "APPLICATION"
    DISK_SPACE = "DISK_SPACE"
    SERVICE = "SERVICE"


class AlertManager:
    """Gestor de alertas del sistema"""

    def __init__(self):
        self.alerts_file = LOG_DIR / "alerts_history.json"
        self.alerts: List[Dict[str, Any]] = []
        self.load_alerts()

    def load_alerts(self) -> None:
        """Cargar alertas desde archivo"""
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.alerts = data.get("alerts", [])
            except Exception as e:
                logger.error(f"Error cargando alertas: {e}")
                self.alerts = []

    def save_alerts(self) -> None:
        """Guardar alertas en archivo"""
        try:
            with open(self.alerts_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"alerts": self.alerts, "last_updated": datetime.now().isoformat()},
                    f,
                    indent=2,
                    default=str,
                )
        except Exception as e:
            logger.error(f"Error guardando alertas: {e}")

    def create_alert(
        self,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        alert_type: AlertType = AlertType.SYSTEM,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Crear una nueva alerta"""
        alert = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S_%f"),
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "severity": severity.value,
            "type": alert_type.value,
            "details": details or {},
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None,
            "resolved": False,
            "resolved_at": None,
            "resolved_by": None,
        }

        self.alerts.append(alert)
        self.save_alerts()

        # Loggear segun severidad
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }.get(severity, logging.INFO)

        logger.log(log_level, f"[{alert_type.value}] {message}")

        return alert

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Reconocer una alerta"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_by"] = acknowledged_by
                alert["acknowledged_at"] = datetime.now().isoformat()
                self.save_alerts()
                logger.info(f"Alerta {alert_id} reconocida por {acknowledged_by}")
                return True
        return False

    def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolver una alerta"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["resolved"] = True
                alert["resolved_at"] = datetime.now().isoformat()
                alert["resolved_by"] = resolved_by
                self.save_alerts()
                logger.info(f"Alerta {alert_id} resuelta por {resolved_by}")
                return True
        return False

    def get_unresolved_alerts(self) -> List[Dict[str, Any]]:
        """Obtener alertas no resueltas"""
        return [a for a in self.alerts if not a["resolved"]]

    def get_alerts_by_severity(
        self, severity: AlertSeverity, include_resolved: bool = False
    ) -> List[Dict[str, Any]]:
        """Obtener alertas por severidad"""
        alerts = self.alerts
        if not include_resolved:
            alerts = [a for a in alerts if not a["resolved"]]
        return [a for a in alerts if a["severity"] == severity.value]

    def get_alerts_by_type(
        self, alert_type: AlertType, include_resolved: bool = False
    ) -> List[Dict[str, Any]]:
        """Obtener alertas por tipo"""
        alerts = self.alerts
        if not include_resolved:
            alerts = [a for a in alerts if not a["resolved"]]
        return [a for a in alerts if a["type"] == alert_type.value]

    def clear_old_alerts(self, days: int = 30, only_resolved: bool = True) -> int:
        """Eliminar alertas antiguas"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        initial_count = len(self.alerts)

        if only_resolved:
            self.alerts = [
                a
                for a in self.alerts
                if not a["resolved"]
                or datetime.fromisoformat(a["timestamp"]).timestamp() > cutoff
            ]
        else:
            self.alerts = [
                a
                for a in self.alerts
                if datetime.fromisoformat(a["timestamp"]).timestamp() > cutoff
            ]

        self.save_alerts()
        removed = initial_count - len(self.alerts)
        logger.info(f"Eliminadas {removed} alertas antiguas")
        return removed

    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de alertas"""
        unresolved = self.get_unresolved_alerts()
        critical = self.get_alerts_by_severity(
            AlertSeverity.CRITICAL, include_resolved=False
        )
        warning = self.get_alerts_by_severity(
            AlertSeverity.WARNING, include_resolved=False
        )

        return {
            "total_alerts": len(self.alerts),
            "unresolved_count": len(unresolved),
            "critical_count": len(critical),
            "warning_count": len(warning),
            "info_count": len(
                self.get_alerts_by_severity(AlertSeverity.INFO, include_resolved=False)
            ),
            "last_alert": self.alerts[-1]["timestamp"] if self.alerts else None,
        }

    def print_summary(self) -> None:
        """Imprimir resumen de alertas"""
        summary = self.get_summary()

        print("\n" + "=" * 50)
        print("  RESUMEN DE ALERTAS".center(50))
        print("=" * 50)
        print(f"Total Alertas: {summary['total_alerts']}")
        print(f"No Resueltas: {summary['unresolved_count']}")
        print(f"  - Criticas: {summary['critical_count']}")
        print(f"  - Advertencias: {summary['warning_count']}")
        print(f"  - Informacion: {summary['info_count']}")
        print(f"Ultima Alerta: {summary['last_alert'] or 'N/A'}")
        print("=" * 50)

        # Mostrar ultimas 5 alertas no resueltas
        unresolved = self.get_unresolved_alerts()[-5:]
        if unresolved:
            print("\nUltimas Alertas No Resueltas:")
            for alert in reversed(unresolved):
                print(f"  [{alert['severity']}] {alert['message']}")

        print()


def check_and_alert():
    """Verificar sistema y generar alertas automaticamente"""
    from monitor import SystemMonitor

    monitor = SystemMonitor()
    status = monitor.get_full_status()

    alert_mgr = AlertManager()
    alerts_generated = 0

    # Verificar cada componente y generar alertas
    for alert in status.get("alerts", []):
        severity = AlertSeverity[alert["severity"]]
        alert_type = AlertType.get(alert["type"], AlertType.SYSTEM)

        alert_mgr.create_alert(
            message=alert["message"], severity=severity, alert_type=alert_type
        )
        alerts_generated += 1

    logger.info(f"Verificacion completada: {alerts_generated} alertas generadas")
    return alerts_generated


def main():
    """Funcion principal"""
    alert_mgr = AlertManager()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "status":
            alert_mgr.print_summary()

        elif command == "history":
            # Mostrar historial
            for alert in alert_mgr.alerts[-10:]:  # Ultimas 10
                status = "RESOLVED" if alert["resolved"] else "OPEN"
                print(f"[{alert['severity']}] [{status}] {alert['message']}")

        elif command == "clear":
            # Limpiar alertas resueltas
            count = alert_mgr.clear_old_alerts(days=30, only_resolved=True)
            print(f"Eliminadas {count} alertas antiguas")

        elif command == "check":
            # Verificar sistema
            check_and_alert()
            alert_mgr.print_summary()

        else:
            print("Comandos disponibles: status, history, clear, check")
    else:
        # Por defecto: mostrar resumen y verificar sistema
        check_and_alert()
        alert_mgr.print_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())
