# 🔄 Sistema de Backups Automáticos

## 📋 Descripción

Sistema automático de backups para ISO 27001 Evaluator con rotación, verificación y programación automática.

---

## 🚀 Características

- ✅ **Backup automático** de base de datos, uploads y configuración
- ✅ **Rotación inteligente** (por días y cantidad máxima)
- ✅ **Verificación** de integridad de backups
- ✅ **Programación automática** (Windows Task Scheduler / Linux Cron)
- ✅ **Múltiples formatos** (SQLite, PostgreSQL, archivos)
- ✅ **Compresión ZIP** para ahorrar espacio
- ✅ **Logs detallados** del proceso

---

## 📦 Scripts Disponibles

### 1. auto_backup.py - Backup Automático

Realiza backup completo del sistema.

**Uso:**
```bash
python scripts/auto_backup.py
```

**Qué respalda:**
- Base de datos (SQLite o PostgreSQL)
- Archivos subidos (uploads/)
- Configuración (.env, docker-compose.yml)

**Proceso:**
1. Crea directorio temporal
2. Copia archivos fuente
3. Crea ZIP comprimido
4. Verifica integridad
5. Limpia backups antiguos
6. Muestra resumen

---

### 2. schedule_backup.py - Programar Backups

Programa backups automáticos.

**Uso:**
```bash
python scripts/schedule_backup.py
```

**Opciones:**
- Programación en Windows (Task Scheduler)
- Programación en Linux/Mac (Cron)
- Instrucciones manuales

---

## 🔧 Configuración

### Variables en `auto_backup.py`

```python
BACKUP_DIR = Path("backups/auto")    # Directorio de backups
RETENTION_DAYS = 7                    # Días de retención
MAX_BACKUPS = 10                      # Máximo de backups a conservar
```

### Personalizar

1. **Cambiar directorio:**
   ```python
   BACKUP_DIR = Path("/ruta/a/tus/backups")
   ```

2. **Cambiar retención:**
   ```python
   RETENTION_DAYS = 30  # 30 días
   ```

3. **Cambiar máximo:**
   ```python
   MAX_BACKUPS = 20  # Máximo 20 backups
   ```

---

## 📅 Programación

### Windows

**Opción 1: Usando el script**
```bash
python scripts/schedule_backup.py
# Selecciona opción 1 (Windows)
# Ingresa hora y minuto
```

**Opción 2: Manual (PowerShell Admin)**
```powershell
schtasks /Create /TN "ISO27001_Backup" /TR "python C:\ruta\scripts\auto_backup.py" /SC DAILY /AT 02:00
```

**Opción 3: GUI**
1. Abre "Task Scheduler"
2. Click "Create Basic Task"
3. Nombre: "ISO27001 Backup"
4. Trigger: Daily, 2:00 AM
5. Action: Start a program
6. Program: `python`
7. Arguments: `C:\ruta\scripts\auto_backup.py`

---

### Linux/Mac

**Opción 1: Usando script**
```bash
python scripts/schedule_backup.py
# Selecciona opción 2 (Linux)
```

**Opción 2: Cron manual**
```bash
crontab -e

# Agregar línea:
0 2 * * * cd /ruta/iso27001 && python3 scripts/auto_backup.py >> logs/backup.log 2>&1
```

**Opción 3: Systemd timer (Linux)**
```ini
# /etc/systemd/system/iso27001-backup.timer
[Unit]
Description=Run ISO27001 backup daily

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

---

## 📊 Estructura de Backups

```
backups/
├── auto/
│   ├── backup_20260330_140530.zip
│   ├── backup_20260329_140530.zip
│   └── backup_20260328_140530.zip
└── manual/
    └── ...
```

**Contenido del ZIP:**
```
backup_20260330_140530/
├── iso27001.db           # Base de datos
├── uploads/              # Archivos subidos
│   ├── control1/
│   └── control2/
└── config/
    ├── .env
    └── docker-compose.yml
```

---

## 🔍 Verificación

### Verificar último backup

```bash
# PowerShell
Get-ChildItem backups/auto -Filter "backup_*.zip" | Select-Object -First 1

# Linux/Mac
ls -lt backups/auto/backup_*.zip | head -1
```

### Verificar integridad

```bash
python -c "
import zipfile
from pathlib import Path

backup = Path('backups/auto/backup_20260330_140530.zip')
with zipfile.ZipFile(backup, 'r') as z:
    bad = z.testzip()
    if bad:
        print(f'ERROR: Archivo corrupto: {bad}')
    else:
        print('OK: Backup íntegro')
"
```

---

## 🗓️ Rotación Automática

El sistema automáticamente:

1. **Mantiene backups de los últimos N días** (default: 7)
2. **Mantiene máximo N backups** (default: 10)
3. **Elimina los más antiguos** cuando excede límites

**Ejemplo:**
- Hoy: 2026-03-30
- Retención: 7 días
- Backups que elimina: Todos los anteriores a 2026-03-23

---

## 📈 Logs y Monitoreo

### Ver logs (Windows Task Scheduler)

1. Abre "Task Scheduler"
2. Busca "ISO27001_Backup"
3. Click "View" → "View All Logs"

### Ver logs (Linux Cron)

```bash
# Si configuraste log
cat /var/log/iso27001_backup.log

# Ver último backup
tail -20 /var/log/iso27001_backup.log
```

### Monitoreo con script

```bash
# Verificar último backup
python -c "
from pathlib import Path
from datetime import datetime

backups = sorted(Path('backups/auto').glob('backup_*.zip'), reverse=True)
if backups:
    last = backups[0]
    mtime = datetime.fromtimestamp(last.stat().st_mtime)
    age = datetime.now() - mtime
    print(f'Último backup: {last.name}')
    print(f'Fecha: {mtime}')
    print(f'Antigüedad: {age.days} días')
else:
    print('No hay backups')
"
```

---

## 🔧 Solución de Problemas

### Problema: "No se encuentra el módulo"

**Causa:** Python no encuentra los módulos

**Solución:**
```bash
# Agregar al PATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python scripts/auto_backup.py
```

### Problema: "Permiso denegado"

**Causa:** Falta de permisos

**Solución:**
```bash
# Linux/Mac
sudo python scripts/auto_backup.py

# Windows (como admin)
python scripts/auto_backup.py
```

### Problema: "Backup muy grande"

**Causa:** Muchos archivos en uploads

**Solución:**
```python
# Excluir directorios grandes
EXCLUDE_DIRS = ['uploads/temp', 'uploads/cache']
```

---

## 📊 Buenas Prácticas

### 1. **Programar en horas bajas**
- 2:00 AM - 4:00 AM (madrugada)
- Evitar horas laborales

### 2. **Retención adecuada**
- Desarrollo: 7 días
- QA: 14 días
- Producción: 30+ días

### 3. **Monitorear espacio**
```bash
# Ver espacio usado
du -sh backups/auto/*

# Ver total
du -sh backups/
```

### 4. **Backups externos**
- Copiar backups a otro servidor
- Usar cloud storage (S3, Azure Blob)
- Al menos 1 copia offsite

---

## 📞 Comandos Rápidos

```bash
# Backup manual
python scripts/auto_backup.py

# Programar backup
python scripts/schedule_backup.py

# Ver últimos backups
ls -lt backups/auto/

# Verificar backup
python -c "import zipfile; zipfile.ZipFile('backups/auto/backup_*.zip').testzip()"

# Eliminar backup específico
rm backups/auto/backup_20260330_*.zip
```

---

## 📚 Documentación Relacionada

- `DOCKER.md` - Docker Compose
- `AUTOMATION.md` - Scripts de automatización
- `OLLAMA_START_STOP.md` - Gestión de Ollama

---

**Última actualización:** 2026-03-30  
**Versión:** v1.8.2  
**Estado:** ✅ Producción
