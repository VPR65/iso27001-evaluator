# 🚀 Quick Start Guide - ISO 27001 & ITIL Evaluator

**Versión:** v1.8.3  
**Fecha:** 2026-03-30  
**Estado:** ✅ Listo para producción

---

## ⚡ Inicio Rápido (5 minutos)

### 1. Instalar Dependencias

```bash
# Python 3.8+ requerido
pip install fastapi sqlmodel uvicorn bcrypt passlib python-jose httpx cryptography python-multipart
```

### 2. Ejecutar la Aplicación

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Acceder al Sistema

```
http://localhost:8000
```

**Usuario por defecto:**
- Email: `admin@acme.com`
- Password: `admin123`

### 4. Verificar Estado

```bash
# Health check
curl http://localhost:8000/health

# Verificar con script
python scripts/monitor.py
```

---

## 📋 Comandos Esenciales

### Monitoreo

```bash
# Ver estado completo del sistema
python scripts/monitor.py

# Ver alertas
python scripts/alert_manager.py status

# Ver historial de alertas
python scripts/alert_manager.py history
```

### Backups

```bash
# Backup manual
python scripts/backup.py backup

# Listar backups
python scripts/backup.py list

# Restaurar backup
python scripts/backup.py restore backups/auto/backup_20260330_191715.zip
```

### QA Testing

```bash
# Ejecutar tests rápidos
python scripts/qa_test.py

# Ejecutar tests funcionales
python scripts/functional_test.py
```

---

## 🔧 Configuración Básica

### Variables de Entorno (.env)

```bash
# Copiar ejemplo
cp .env.docker .env

# Editar con tus valores
DATABASE_URL=sqlite:///./iso27001.db
SECRET_KEY=tu_secreto_aqui_32_caracteres
AI_MODE=ollama
AI_LOCAL_MODEL=llama3.1:latest
```

### IA Local (Ollama)

```bash
# Instalar Ollama (si no esta instalado)
# Ver: https://ollama.ai

# Iniciar Ollama
ollama serve

# Cargar modelo
ollama pull llama3.1:latest

# Verificar
ollama list
```

---

## 📊 Estructura de Directorios

```
ISO27001_ITIL_seguridad/
├── app/                   # Código principal
│   ├── main.py           # Aplicación FastAPI
│   ├── config.py         # Configuración
│   ├── database.py       # Conexión DB
│   ├── ai_service.py     # Servicio de IA
│   ├── models.py         # Modelos DB
│   ├── routes/           # Endpoints
│   └── templates/        # HTML templates
├── scripts/              # Scripts de utilidad
│   ├── monitor.py        # Monitoreo
│   ├── alert_manager.py  # Alertas
│   ├── backup.py         # Backups
│   ├── qa_test.py        # Tests
│   └── deploy.ps1        # Deploy
├── docs/                 # Documentación
├── backups/              # Backups
├── logs/                 # Logs
└── uploads/              # Archivos subidos
```

---

## ✅ Checklist Pre-Producción

### Obligatorio
- [ ] Backup realizado: `python scripts/backup.py backup`
- [ ] Tests passing: `python scripts/qa_test.py`
- [ ] Variables de ambiente configuradas
- [ ] Secretos NO hardcodeados
- [ ] Inputs de usuario sanitizados
- [ ] Permisos verificados en endpoints

### Recomendado
- [ ] Monitoreo activo
- [ ] Alertas configuradas
- [ ] Backups automáticos programados
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado

---

## 🚨 Solución de Problemas Comunes

### La aplicación no inicia

```bash
# Verificar logs
cat logs/app.log

# Verificar puerto en uso
netstat -ano | findstr :8000

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error de base de datos

```bash
# Resetear DB (DESARROLLO SOLO)
rm iso27001.db
python -c "from app.database import create_db_and_tables; create_db_and_tables()"
```

### Ollama no disponible

```bash
# Verificar si corre
ollama list

# Iniciar servicio
ollama serve

# En segundo plano (Linux)
nohup ollama serve &
```

### Backups fallan

```bash
# Verificar espacio
python scripts/monitor.py

# Limpiar backups antiguos
python scripts/backup.py clean_old_backups --days 7
```

---

## 📚 Documentación Completa

| Documento | Descripción |
|-----------|-------------|
| `PROJECT_DEFINITION.md` | Visión general del proyecto |
| `ARCHITECTURE.md` | Arquitectura técnica |
| `DEPLOYMENT_AND_TESTING.md` | Guía de deployment |
| `MONITORING.md` | Sistema de monitoreo |
| `AUTO_BACKUP.md` | Backups automáticos |
| `DOCKER.md` | Docker Compose guide |
| `CHANGELOG.md` | Historial de cambios |
| `ROADMAP.md` | Plan futuro |

---

## 🔐 Seguridad

### Usuario por defecto
- **Email:** admin@acme.com
- **Password:** admin123
- **2FA:** Opcional (recomendado activar)

### Cambiar password por defecto

```bash
# Desde la UI: Admin > Usuarios > Editar
# O via SQL:
python -c "from app.security import hash_password; print(hash_password('nuevo_password'))"
```

---

## 📞 Soporte

### Comandos de Diagnóstico

```bash
# Estado completo
python scripts/monitor.py

# Alertas
python scripts/alert_manager.py status

# Tests
python scripts/qa_test.py

# Versiones
python -c "import fastapi, sqlmodel; print(f'FastAPI: {fastapi.__version__}, SQLModel: {sqlmodel.__version__}')"
```

### Logs Principales

- `logs/app.log` - Logs de la aplicación
- `logs/monitor.log` - Logs del monitor
- `logs/alerts.log` - Logs de alertas
- `logs/backup.log` - Logs de backups

---

## 🎯 Próximos Pasos

1. **Configurar Oracle Cloud** (opcional)
2. **Programar backups automáticos**
3. **Configurar alertas por email**
4. **Habilitar 2FA para todos los usuarios**
5. **Revisar runbook de incidentes**

---

**Fin de la Guía Rápida**

Para más detalles, ver la documentación completa en `docs/`.
