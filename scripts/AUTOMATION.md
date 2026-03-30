# 🤖 Scripts de Automatización

## 📋 Descripción

Estos scripts automatizan las tareas más comunes de despliegue, mantenimiento y operación del sistema ISO 27001 Evaluator.

---

## 🚀 Scripts Disponibles

### 1. **deploy.ps1** - Despliegue Automático

Despliega la aplicación completa con Docker Compose.

**Uso:**
```powershell
# Despliegue básico
.\scripts\deploy.ps1

# Con IA local (Ollama)
.\scripts\deploy.ps1 -WithOllama

# Sin cache de Docker
.\scripts\deploy.ps1 -NoCache

# Entorno específico
.\scripts\deploy.ps1 -Environment production
```

**Parámetros:**
- `-Environment`: development (default), qa, production
- `-WithOllama`: Incluir Ollama (IA local)
- `-NoCache`: Sin cache de Docker

---

### 2. **backup_auto.ps1** - Backup Automático

Realiza backup automático de base de datos, uploads y configuración.

**Uso:**
```powershell
# Backup completo
.\scripts\backup_auto.ps1

# Con retención de 14 días
.\scripts\backup_auto.ps1 -RetentionDays 14

# Modo automático (sin prompts)
.\scripts\backup_auto.ps1 -Auto
```

**Parámetros:**
- `-RetentionDays`: Días de retención (default: 7)
- `-BackupDir`: Directorio de backups (default: "backups")
- `-Auto`: Modo automático

**Qué respalda:**
- ✅ Base de datos (PostgreSQL o SQLite)
- ✅ Archivos subidos (uploads)
- ✅ Configuración (.env, docker-compose.yml)

---

### 3. **install.ps1** - Instalación Automática

Instala dependencias y configura el entorno inicial.

**Uso:**
```powershell
.\scripts\install.ps1
```

**Qué hace:**
1. Verifica Python
2. Verifica pip
3. Instala dependencias (requirements.txt)
4. Verifica Ollama (opcional)
5. Crea .env desde plantilla
6. Inicializa base de datos

---

### 4. **qa_test.py** - Pruebas de Funcionamiento

Ejecuta pruebas automáticas de QA.

**Uso:**
```bash
python scripts/qa_test.py
```

**Pruebas:**
- Requisitos (FastAPI, SQLModel, Uvicorn)
- Ollama (IA local)
- Base de datos
- Endpoints básicos
- Configuración

---

### 5. **Start-Ollama.ps1 / Stop-Ollama.ps1**

Gestión de Ollama (IA local).

**Uso:**
```powershell
# Iniciar Ollama
.\scripts\Start-Ollama.ps1

# Detener Ollama
.\scripts\Stop-Ollama.ps1
```

---

## 📅 Automatización con Tareas Programadas

### Windows Task Scheduler

Programar backup diario:

```powershell
# Crear tarea programada
$action = New-ScheduledTaskAction -Execute "PowerShell" `
  -Argument "-File C:\ruta\scripts\backup_auto.ps1 -Auto"
  
$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask -TaskName "ISO27001-Backup" `
  -Action $action -Trigger $trigger `
  -User "usuario" -Password "password"
```

### Linux Cron

Programar backup diario (2 AM):

```bash
# Editar crontab
crontab -e

# Agregar línea:
0 2 * * * cd /ruta/al/proyecto && ./scripts/backup_auto.sh -Auto
```

---

## 🔧 Solución de Problemas

### Problema: "Script no se puede ejecutar"

**Causa:** PowerShell bloquea scripts no firmados

**Solución:**
```powershell
# Opción 1: Ejecutar con permiso temporal
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1

# Opción 2: Cambiar política (admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problema: "Docker no responde"

**Solución:**
```powershell
# Reiniciar Docker Desktop
# O en Linux:
sudo systemctl restart docker
```

### Problema: "Backup falla"

**Causa:** Espacio en disco insuficiente

**Solución:**
```powershell
# Verificar espacio
Get-PSDrive C

# Limpiar backups antiguos
.\scripts\backup_auto.ps1 -RetentionDays 3
```

---

## 📊 Flujo de Trabajo Recomendado

### Despliegue Inicial

```powershell
# 1. Instalar dependencias
.\scripts\install.ps1

# 2. Desplegar con Docker
.\scripts\deploy.ps1 -WithOllama

# 3. Verificar
python scripts/qa_test.py
```

### Mantenimiento Diario

```powershell
# Backup automático (mañana)
.\scripts\backup_auto.ps1 -Auto

# Verificar estado
docker-compose ps
```

### Actualización

```powershell
# 1. Detener
docker-compose down

# 2. Actualizar código
git pull

# 3. Re-desplegar
.\scripts\deploy.ps1 -WithOllama

# 4. Verificar
python scripts/qa_test.py
```

---

## 📞 Comandos Rápidos

```powershell
# Instalar todo
.\scripts\install.ps1

# Desplegar
.\scripts\deploy.ps1 -WithOllama

# Backup
.\scripts\backup_auto.ps1 -Auto

# Pruebas QA
python scripts/qa_test.py

# Estado
docker-compose ps

# Logs
docker-compose logs -f
```

---

## 📚 Documentación Relacionada

- `DOCKER.md` - Guía completa de Docker
- `OLLAMA_START_STOP.md` - Gestión de Ollama
- `TESTING.md` - Plan de pruebas
- `DEPLOYMENT_AND_TESTING.md` - Despliegue y testing

---

**Última actualización:** 2026-03-30  
**Versión:** v1.8.1  
**Estado:** ✅ Producción
