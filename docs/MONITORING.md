# 📊 Sistema de Monitoreo y Alertas

**Versión:** v1.8.2  
**Fecha:** 2026-03-30  
**Estado:** ✅ Completado

---

## 📋 Descripción

El sistema de monitoreo proporciona vigilancia continua de:
- **Uptime** del sistema
- **Espacio en disco** con umbrales configurables
- **Estado de backups** (últimas 24h, 7 días)
- **Conexión a base de datos**
- **Disponibilidad de Ollama** (IA local)
- **Salud de la aplicación** (endpoint /health)

---

## 🚀 Uso Básico

### Monitoreo del Sistema

```bash
# Verificar estado completo del sistema
python scripts/monitor.py

# Salida esperada:
# ============================================================
#   SISTEMA - ISO 27001 & ITIL Evaluator
# ============================================================
# Timestamp: 2026-03-30T19:30:00
# Estado General: OK
# 
# Uptime: 0:05:30
# Disco: 45.2% usado (120.5 GB libres)
# Backups: 15 total, 3 en 7 dias
#   Ultimo: backup_20260330_191715.zip (25.3 MB)
# Base de Datos: OK
# Ollama: OK (5 modelos)
# App: OK (45ms)
# ============================================================
```

### Gestión de Alertas

```bash
# Ver resumen de alertas
python scripts/alert_manager.py status

# Ver historial completo
python scripts/alert_manager.py history

# Verificar sistema y generar alertas
python scripts/alert_manager.py check

# Limpiar alertas antiguas (>30 días)
python scripts/alert_manager.py clear
```

---

## 📁 Archivos del Sistema de Monitoreo

| Archivo | Descripción |
|---------|-------------|
| `scripts/monitor.py` | Script principal de monitoreo |
| `scripts/alert_manager.py` | Gestor de alertas |
| `logs/monitor.log` | Log del monitor |
| `logs/alerts.log` | Log de alertas |
| `logs/alerts_history.json` | Historial de alertas |
| `logs/last_status.json` | Último estado del sistema |

---

## 🔔 Tipos de Alertas

### Severidad
- **INFO**: Información general
- **WARNING**: Requiere atención (ej. backup ausente)
- **CRITICAL**: Acción inmediata requerida (ej. disco lleno)

### Tipos
- `SYSTEM`: Eventos del sistema
- `BACKUP`: Estado de backups
- `DATABASE`: Conexión a BD
- `SECURITY`: Eventos de seguridad
- `APPLICATION`: Salud de la app
- `DISK_SPACE`: Espacio en disco
- `SERVICE`: Servicios externos (Ollama, etc.)

---

## ⚙️ Configuración

### Umbrales de Alerta

```python
# En monitor.py, método check_disk_space()
threshold_percent = 90.0  # % de uso de disco para alerta crítica
```

### Frecuencia de Monitoreo

Recomendado:
- **Monitoreo continuo**: Cada 5 minutos
- **Verificación de backups**: Cada hora
- **Limpieza de logs**: Diaria

### Programar Monitoreo Automático

**Windows (Task Scheduler):**
```powershell
# Crear tarea para ejecutar cada 5 minutos
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "scripts/monitor.py" `
    -WorkingDirectory "C:\ruta\al\proyecto"

$trigger = New-ScheduledTaskTrigger -Once (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepeatIndefinitely

Register-ScheduledTask -TaskName "ISO27001_Monitor" `
    -Action $action -Trigger $trigger -Description "Monitoreo del sistema"
```

**Linux (cron):**
```bash
# Ejecutar cada 5 minutos
*/5 * * * * cd /ruta/proyecto && python scripts/monitor.py >> logs/monitor_cron.log 2>&1
```

---

## 📊 Métricas Monitoreadas

### 1. Uptime
- Tiempo desde el inicio del monitoreo
- Formato: `HH:MM:SS`

### 2. Espacio en Disco
- Total, usado y libre (GB)
- Porcentaje de uso
- Umbral de alerta: 90%

### 3. Backups
- Total de backups disponibles
- Backups en últimas 24 horas
- Backups en últimos 7 días
- Tamaño del último backup

### 4. Base de Datos
- Estado de conexión
- Tiempo de respuesta

### 5. Ollama (IA)
- Disponibilidad del servicio
- Número de modelos disponibles
- Modelos cargados

### 6. Aplicación
- Endpoint `/health` responde
- Tiempo de respuesta (ms)

---

## 🔧 Integración con el Sistema

### Endpoint de Health Check

La aplicación incluye un endpoint para verificar su salud:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "v1.8.2"
    }
```

### Logs Generados

El sistema genera logs en:
- `logs/monitor.log` - Actividad del monitor
- `logs/alerts.log` - Alertas generadas
- `logs/alerts_history.json` - Historial completo

---

## 📈 Ejemplos de Uso

### Verificar Estado Antes de Deploy

```bash
# 1. Verificar estado actual
python scripts/monitor.py

# 2. Verificar alertas críticas
python scripts/alert_manager.py status

# 3. Si todo OK, proceder con deploy
python scripts/deploy.ps1
```

### Monitoreo Continuo

```bash
# Crear script de monitoreo continuo (monitor_loop.py)
while True:
    python scripts/monitor.py
    sleep 300  # 5 minutos
```

### Integrar con Alertas Externas

```python
# Ejemplo: enviar email si hay alerta crítica
from alert_manager import AlertManager, AlertSeverity

alert_mgr = AlertManager()
critical = alert_mgr.get_alerts_by_severity(AlertSeverity.CRITICAL)

if critical:
    # Enviar email
    send_email(
        subject=f"Alerta Crítica: {len(critical)} alertas",
        body=str(critical)
    )
```

---

## 🛠️ Solución de Problemas

### El monitor no detecta Ollama

**Problema:** Ollama aparece como "No disponible"

**Solución:**
1. Verificar que Ollama esté corriendo: `ollama list`
2. Si no corre, iniciarlo: `ollama serve`
3. Verificar puerto 11434 accesible

### Alertas de espacio en disco

**Problema:** Alerta crítica de disco lleno

**Solución:**
1. Revisar backups antiguos: `ls -lh backups/`
2. Eliminar backups > 30 días
3. Ejecutar: `python scripts/backup.py clean_old_backups --days 30`

### Backups no se generan

**Problema:** No hay backups en últimas 24h

**Solución:**
1. Verificar script de auto-backup: `python scripts/auto_backup.py`
2. Revisar permisos de escritura en `backups/`
3. Verificar espacio disponible

---

## 📋 Checklist de Monitoreo

### Diario
- [ ] Revisar alertas críticas
- [ ] Verificar backup del día
- [ ] Revisar espacio en disco

### Semanal
- [ ] Revisar tendencia de uso de disco
- [ ] Verificar backups de la semana
- [ ] Revisar logs de errores

### Mensual
- [ ] Limpiar alertas antiguas (>30 días)
- [ ] Revisar métricas de rendimiento
- [ ] Actualizar umbrales si es necesario

---

## 🔐 Consideraciones de Seguridad

- Los logs no deben contener información sensible
- El archivo `alerts_history.json` puede crecer, limitar tamaño
- El monitoreo no debe exponer endpoints públicamente
- Usar autenticación para accesos remotos

---

## 📚 Referencias

- Documentación principal: `MONITORING.md`
- Scripts: `scripts/monitor.py`, `scripts/alert_manager.py`
- Logs: `logs/monitor.log`, `logs/alerts.log`

---

**Fin del Documento**
