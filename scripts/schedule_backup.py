# ISO 27001 Evaluator - Agendar Backup Automático
# Uso: python scripts/schedule_backup.py
# Descripción: Programa backups automáticos en Windows Task Scheduler o Linux Cron

import os
import sys
import subprocess
from pathlib import Path


def is_admin():
    """Verifica si se ejecuta como administrador"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes

        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False


def schedule_windows(task_name="ISO27001_Backup", hour=2, minute=0):
    """Programa backup en Windows Task Scheduler"""
    print(
        f"[INFO] Programando backup en Windows (diario a las {hour:02d}:{minute:02d})..."
    )

    script_path = Path(__file__).parent / "auto_backup.py"
    python_exe = sys.executable

    # Comando para la tarea
    command = f'python "{script_path}"'

    # Crear archivo XML para Task Scheduler
    xml_file = "iso27001_backup_task.xml"
    xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-03-30T{hour:02d}:{minute:02d}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <AllowStartIfOnBatteries>true</AllowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{script_path}"</Arguments>
    </Exec>
  </Actions>
</Task>
"""

    try:
        # Escribir XML
        with open(xml_file, "w", encoding="utf-16") as f:
            f.write(xml_content)

        print(f"[OK] Archivo XML creado: {xml_file}")
        print(f"[INFO] Para importar la tarea, ejecuta como administrador:")
        print(f'  schtasks /Create /TN "{task_name}" /XML "{xml_file}"')

    except Exception as e:
        print(f"[ERROR] Error creando tarea: {e}")


def schedule_linux(task_name="iso27001_backup", hour=2, minute=0):
    """Programa backup en Linux Cron"""
    print(
        f"[INFO] Programando backup en Linux (diario a las {hour:02d}:{minute:02d})..."
    )

    script_path = Path(__file__).parent / "auto_backup.py"

    cron_job = f"{minute} {hour} * * * cd {script_path.parent} && python3 {script_path} >> /var/log/iso27001_backup.log 2>&1\n"

    print(f"[INFO] Agrega esta línea a tu crontab (crontab -e):")
    print(cron_job)
    print("[INFO] O ejecuta:")
    print(f'echo "{cron_job.strip()}" | crontab -')


def main():
    print("\n" + "=" * 60)
    print("  ISO 27001 - Programar Backup Automático")
    print("=" * 60 + "\n")

    print("Opciones:")
    print("1. Programar backup diario (Windows)")
    print("2. Programar backup diario (Linux/Mac)")
    print("3. Mostrar instrucciones manuales")
    print("4. Salir\n")

    choice = input("Selecciona una opción (1-4): ").strip()

    hour = int(input("Hora del backup (0-23, default 2): ").strip() or "2")
    minute = int(input("Minuto (0-59, default 0): ").strip() or "0")

    if choice == "1":
        schedule_windows(hour=hour, minute=minute)
    elif choice == "2":
        schedule_linux(hour=hour, minute=minute)
    elif choice == "3":
        print("\n=== Instrucciones Manuales ===\n")
        print("Windows (PowerShell como Admin):")
        print(
            '  schtasks /Create /TN "ISO27001_Backup" /TR "python C:\\ruta\\scripts\\auto_backup.py" /SC DAILY /AT 02:00'
        )
        print("\nLinux (Cron):")
        print("  crontab -e")
        print("  0 2 * * * cd /ruta && python3 scripts/auto_backup.py")
        print("\nmacOS (launchd):")
        print("  Ver: https://launchd.info/")
    elif choice == "4":
        print("\nSaliendo...")
        return
    else:
        print("\n[ERROR] Opción inválida")
        return

    print("\n[OK] ¡Programación completada!")
    print("[INFO] El backup se ejecutará automáticamente.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelado por usuario")
        sys.exit(1)
