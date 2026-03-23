# REGISTRO DE CONFIGURACION - ISO 27001 Evaluator

> Version: 1.0.0 | Fecha: 2026-03-23

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
│   ├── database.py       # Configuracion SQLite
│   ├── seed.py          # Datos iniciales (93 controles ISO)
│   ├── routes/          # Endpoints de la API
│   ├── templates/       # Plantillas HTML Jinja2
│   └── static/          # CSS y archivos estaticos
├── docs/                 # Documentacion del proyecto
├── scripts/              # Backup y rollback
├── uploads/              # Archivos de evidencia (subidos por usuarios)
├── iso27001.db          # Base de datos SQLite
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

REM Ver status de Git
git status
```

---

## 1. CUENTAS Y CREDENCIALES

| Servicio | Cuenta/Email | Password/Token | Notes |
|----------|--------------|----------------|-------|
| GitHub | `vpalma05@hotmail.com` | (cuenta personal) | Usuario: VPR65 |
| Render | `vpalma05@hotmail.com` | (login via GitHub) | |
| Correo desarrollo | `admin@iso27001.local` | `admin123` | Superadmin |
| Correo demo | `admin@demo.local` | `demo123` | Admin Cliente |

---

## 2. REPOSITORIOS

| Repositorio | URL | Rama principal | Descripcion |
|-------------|-----|----------------|--------------|
| ISO 27001 Evaluator | `https://github.com/VPR65/iso27001-evaluator` | `main` | Codigo fuente completo |

---

## 3. ENTORNOS DE DESPLEGUE

| Entorno | URL | Estado | Rama Git | Notas |
|---------|-----|--------|----------|-------|
| Produccion | `https://iso27001-prod.onrender.com` | Activo | `main` | |
| QA/Pruebas | `https://iso27001-qa.onrender.com` | Activo | `main` | |
| Desarrollo local | `http://localhost:8000` | Activo | - | Tu PC |

---

## 4. CONFIGURACION DE RENDER

### Web Service - Produccion
| Campo | Valor |
|-------|-------|
| Name | `iso27001-prod` |
| Region | Oregon |
| Branch | `main` |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free (750 horas/mes) |

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

---

## 5. BASE DE DATOS

| Entorno | Tipo | Ubicacion | Backup |
|---------|------|-----------|--------|
| Desarrollo local | SQLite | `iso27001.db` | Manual (`python scripts/backup.py`) |
| QA (Render) | SQLite | Volumen Render | Automatico (snapshots 3 dias) |
| Produccion (Render) | SQLite | Volumen Render | Automatico (snapshots 3 dias) |

---

## 6. DOCUMENTACION DEL PROYECTO

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
| docs/BACKUP_RECOVERY.md | `docs/` | Procedimientos de backup y recuperacion |

---

## 7. RESPALDOS Y RECUPERACION

### Ubicaciones de respaldo

| Tipo | Ubicacion desarrollo (F:) | Ubicacion respaldo PC (C:) | Ubicacion backup (F:) |
|------|---------------------------|---------------------------|----------------------|
| Codigo fuente | `F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad\` | `C:\...\ISO27001_ITIL_seguridad\` | `F:\Desarrollo\Opencode\iso27001-backup\codigo\` |
| Base de datos | `F:\...\iso27001.db` | `C:\...\iso27001.db` | `F:\Desarrollo\Opencode\iso27001-backup\database\` |
| Archivos uploads | `F:\...\uploads\` | `C:\...\uploads\` | `F:\Desarrollo\Opencode\iso27001-backup\uploads\` |
| Documentacion | `F:\...\docs\` | `C:\...\docs\` | `F:\Desarrollo\Opencode\iso27001-backup\docs\` |

**Frecuencia:** Semanal (backup completo), antes de cada despliegue (DB), antes de cada cambio importante (snapshot)

**Procedimientos:** Ver `docs/BACKUP_RECOVERY.md`

### Flujo de respaldo:
1. **Desarrollar en F:** - `F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad`
2. **Antes de cambios importantes** -respaldar a `F:\Desarrollo\Opencode\iso27001-backup\`
3. **Push a GitHub** - `https://github.com/VPR65/iso27001-evaluator`
4. **Deploy a QA/Render** - `https://iso27001-qa.onrender.com`
5. **Deploy a Prod** - `https://iso27001-prod.onrender.com`

| Variable | Desarrollo | QA | Produccion |
|----------|------------|-----|------------|
| SECRET_KEY | `changeme` | (generar) | (generar seguro) |
| DEBUG | `false` | `false` | `false` |
| SESSION_EXPIRE_HOURS | `24` | `24` | `24` |

---

## 8. COMANDOS UTILES

```bash
# Desarrollo local
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

# Backup local
python scripts/backup.py backup

# Rollback local
python scripts/rollback.py v1.0.0
```

---

## 9. HISTORIAL DE VERSIONES

| Version | Fecha | Cambios | Quien |
|---------|-------|----------|-------|
| 1.0.0 | 2026-03-22 | Creacion inicial del sistema + documentacion | Equipo desarrollo |
| 1.1.2 | 2026-03-23 | CSRF completo, deploy en Render QA + Prod, fixes Docker | Equipo desarrollo |

---

## 10. NOTAS

- El plan gratuito de Render permite 750 horas/mes (suficiente para 1 app)
- La app "duerme" despues de 15 min de inactividad en Render
- GitHub Actions no configurado todavia (despliegue desde Render via GitHub push)
- Backup de la DB se debe hacer manualmente en desarrollo
- Render QA + Produccion desplegados y funcionando (v1.1.2)

---

*Documento creado automaticamente. Actualizar cuando haya cambios.*