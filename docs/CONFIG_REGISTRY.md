# REGISTRO DE CONFIGURACION - ISO 27001 Evaluator

> Version: 1.4.1 | Fecha: 2026-03-26

---

## PUNTO DE PARTIDA - DESARROLLO LOCAL

### Ruta principal de desarrollo (F:)
```
F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad
```

### Para acceder rapidamente:
- **Explorador Windows:** `F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad`
- **Terminal:**
  ```cmd
  cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"
  ```

### Ruta de respaldo en PC (C:)
```
C:\Users\vpalma\Documents\Desarrollo\OpenCode_Antigravity\ISO27001_ITIL_seguridad
```

### Estructura de carpetas desarrollo (F:):
```
ISO27001_ITIL_seguridad/
├── app/                    # Codigo fuente de la app
│   ├── main.py           # Entry point de FastAPI
│   ├── models.py         # Modelos SQLModel
│   ├── auth.py           # Autenticacion
│   ├── database.py       # Configuracion PostgreSQL/SQLite
│   ├── seed.py          # Datos iniciales (153 controles ISO)
│   ├── routes/          # Endpoints de la API
│   ├── templates/       # Plantillas HTML Jinja2
│   └── static/          # CSS y archivos estaticos
├── docs/                 # Documentacion del proyecto
├── scripts/              # Backup y rollback
├── uploads/              # Archivos de evidencia
├── iso27001.db          # Base de datos SQLite (local)
├── requirements.txt      # Dependencias Python
├── Dockerfile           # Imagen Docker
└── docker-compose.yml   # Configuracion Docker
```

### Comandos de desarrollo (F:):
```cmd
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"

REM Iniciar servidor local
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

REM Verificar que la app compila
python -c "from app.main import app; print('OK')"

REM Hacer backup
python scripts/backup.py backup

REM Ejecutar tests
python -m pytest tests/ -v

REM Ver status de Git
git status
```

---

## 1. CUENTAS Y CREDENCIALES

| Servicio | Cuenta/Email | Password/Token | Notas |
|----------|--------------|----------------|-------|
| GitHub | `vpalma05@hotmail.com` | (login via navegador) | Usuario: VPR65 |
| Neon.tech | `vpalma05@hotmail.com` | (login via GitHub) | Base de datos PostgreSQL |
| Render | `vpalma05@hotmail.com` | (login via GitHub) | |
| Correo superadmin | `admin@iso27001.local` | `admin123` | Superadmin |
| Correo demo | `admin@demo.local` | `demo123` | Admin Cliente Demo |

---

## 2. REPOSITORIOS

| Repositorio | URL | Rama principal | Descripcion |
|-------------|-----|----------------|--------------|
| ISO 27001 Evaluator | `https://github.com/VPR65/iso27001-evaluator` | `main` | Codigo fuente completo |

---

## 3. ENTORNOS DE DESPLEGUE

| Entorno | URL | Estado | Rama Git | Base de Datos | Notas |
|---------|-----|--------|----------|--------------|-------|
| Produccion | `https://iso27001-prod.onrender.com` | Activo | `production` | Neon PostgreSQL | Prod real |
| QA/Pruebas | `https://iso27001-qa.onrender.com` | Activo | `main` | Neon PostgreSQL | Testing |
| Desarrollo local | `http://localhost:8000` | Activo | - | SQLite local | Tu PC |

---

## 4. BASE DE DATOS - NEON POSTGRESQL

### Informacion de conexion (NEON TECH)

| Campo | Valor |
|-------|-------|
| Proveedor | AWS |
| Region | Sao Paulo (sa-east-1) |
| Version PostgreSQL | 17 |
| Endpoint Pooler | `ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech` |
| Base de datos | `neondb` |
| Usuario | `neondb_owner` |

### Connection String (NO COMPARTIR - CONFIDENCIAL)
```
postgresql://neondb_owner:npg_PhU0gVlXJ5yW@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Configuracion en Render (Environment Variables)

| Variable | Valor | Entorno |
|---------|-------|---------|
| DATABASE_URL | `postgresql://neondb_owner:***@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require` | QA y Produccion |

### Plan Neon
| Plan | Almacenamiento | Precio |
|------|-----------------|--------|
| Free Tier | 0.5 GB | $0 |
| Paid | Desde 3 GB | $9/mes |

### Limites para 5 clientes + 10 usuarios
- **0.5 GB gratuito** es suficiente para:
  - ~5 clientes
  - ~10 usuarios
  - ~153 controles ISO
  - ~100 evaluaciones
  - Logs de auditoria (6 meses)
- **No exceder:** ~500MB de datos aproximadamente

---

## 5. CONFIGURACION DE RENDER

### Web Service - Produccion
| Campo | Valor |
|-------|-------|
| Name | `iso27001-prod` |
| Region | Oregon |
| Branch | `production` |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free (750 horas/mes) |
| Environment Variables | DATABASE_URL (ver seccion 4) |

### Web Service - QA
| Campo | Valor |
|-------|-------|
| Name | `iso27001-qa` |
| Region | Oregon |
| Branch | `main` |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free (750 horas/mes) |
| Environment Variables | DATABASE_URL (ver seccion 4) |

---

## 6. BASE DE DATOS

| Entorno | Tipo | Ubicacion | Persistencia |
|---------|------|-----------|--------------|
| Desarrollo local | SQLite | `iso27001.db` | Permanente en tu PC |
| QA (Render) | PostgreSQL | Neon.tech | Permanente (0.5GB free) |
| Produccion (Render) | PostgreSQL | Neon.tech | Permanente (0.5GB free) |

### Ventajas de PostgreSQL en Neon
- **Persistencia real:** Los datos NO se pierden al reiniciar
- **Acceso desde cualquier lugar:** Connection string compartido
- **Backups automaticos:** Neon hace snapshots automaticos
- **Gratuito:** 0.5 GB suficiente para el uso previsto

---

## 7. DOCUMENTACION DEL PROYECTO

| Documento | Ubicacion | Descripcion |
|----------|-----------|--------------|
| README.md | Raiz del proyecto | Guia de instalacion rapida |
| AGENTS.md | Raiz del proyecto | Convenciones para agentes AI |
| docs/PROJECT_PLAN.md | `docs/` | Planificacion y alcance |
| docs/PROCESSES.md | `docs/` | Procesos ITIL y Agile |
| docs/ARCHITECTURE.md | `docs/` | Arquitectura tecnica |
| docs/TESTING.md | `docs/` | Plan de pruebas |
| docs/CHANGELOG.md | `docs/` | Registro de cambios |
| docs/INFRASTRUCTURE.md | `docs/` | Plataformas gratuitas |
| docs/CONFIG_REGISTRY.md | `docs/` | Este documento |
| docs/BACKUP_RECOVERY.md | `docs/` | Procedimientos de backup |

---

## 8. RESPALDOS Y RECUPERACION

### Ubicaciones de respaldo

| Tipo | Ubicacion desarrollo (F:) | Ubicacion respaldo PC (C:) | Ubicacion backup (F:) |
|------|---------------------------|---------------------------|----------------------|
| Codigo fuente | `F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad\` | `C:\...\ISO27001_ITIL_seguridad\` | `F:\Desarrollo\Opencode\iso27001-backup\codigo\` |
| Base de datos (local) | `F:\...\iso27001.db` | `C:\...\iso27001.db` | `F:\Desarrollo\Opencode\iso27001-backup\database\` |
| Archivos uploads | `F:\...\uploads\` | `C:\...\uploads\` | `F:\Desarrollo\Opencode\iso27001-backup\uploads\` |
| Documentacion | `F:\...\docs\` | `C:\...\docs\` | `F:\Desarrollo\Opencode\iso27001-backup\docs\` |

### Flujo de respaldo:
1. **Desarrollar en F:** - `F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad`
2. **Antes de cambios importantes** -respaldar a `F:\Desarrollo\Opencode\iso27001-backup\`
3. **Push a GitHub** - `https://github.com/VPR65/iso27001-evaluator`
4. **Deploy a QA/Render** - `https://iso27001-qa.onrender.com`
5. **Deploy a Prod** - `https://iso27001-prod.onrender.com`

### Variables de entorno

| Variable | Desarrollo | QA | Produccion |
|----------|------------|-----|------------|
| DATABASE_URL | `sqlite:///./iso27001.db` | PostgreSQL Neon | PostgreSQL Neon |
| SECRET_KEY | `changeme` | (generar) | (generar seguro) |
| DEBUG | `false` | `false` | `false` |
| SESSION_EXPIRE_HOURS | `24` | `24` | `24` |

---

## 9. COMANDOS UTILES

```bash
# Desarrollo local
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

# Backup local
python scripts/backup.py backup

# Rollback local
python scripts/rollback.py v1.0.0

# Ejecutar tests
python -m pytest tests/ -v

# Inicializar DB en Neon (desde repo)
python scripts/init_neon_db.py
```

---

## 10. DEBUG ENDPOINTS (QA)

| Endpoint | Descripcion | Token |
|----------|-------------|-------|
| `/admin/debug/users?token=qa-debug-2024` | Ver todos los usuarios | `qa-debug-2024` |
| `/admin/debug/reset-password?token=qa-debug-2024&email=X&password=Y` | Reset password | `qa-debug-2024` |
| `/admin/debug/seed-test-data?token=qa-debug-2024` | Poblar datos de prueba | `qa-debug-2024` |

---

## 11. HISTORIAL DE VERSIONES

| Version | Fecha | Cambios | Quien |
|---------|-------|----------|-------|
| 1.0.0 | 2026-03-22 | Creacion inicial del sistema | Equipo desarrollo |
| 1.1.2 | 2026-03-23 | CSRF completo, deploy en Render QA + Prod | Equipo desarrollo |
| 1.3.0 | 2026-03-25 | PostgreSQL en Neon, 43 tests, multi-norma | Equipo desarrollo |

---

## 12. NOTAS

- **PostgreSQL Neon:** Solucion definitiva al problema de datos persistentes
- Plan gratuito de Neon: 0.5 GB suficiente para 5 clientes + 10 usuarios
- Plan gratuito de Render: 750 horas/mes (la app "duerme" despues de 15 min)
- GitHub Actions no configurado (despliegue desde Render via GitHub push)
- Tests automatizados: 43 tests funcionando en `tests/`

---

*Documento creado automaticamente. Actualizar cuando haya cambios en la configuracion.*