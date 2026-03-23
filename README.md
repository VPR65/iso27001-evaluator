# ISO 27001 Evaluator v1.1.0

Sistema web para evaluar el cumplimiento de seguridad de la informacion bajo el marco **ISO 27001:2022** (Anexo A - 93 controles organizados en 4 dominios).

## Stack Tecnologico

| Capa         | Tecnologia                        |
|--------------|-----------------------------------|
| Backend      | FastAPI + SQLModel + SQLite       |
| Frontend     | Jinja2 + HTMX + Pico.css          |
| UI           | Inter font + Font Awesome 6 + CSS personalizado |
| Estadisticas | Chart.js (barras + radar)         |
| Auth         | Session cookies + bcrypt           |

## Instalacion Rapida

### Local (Python directo)

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up --build
```

La app estara disponible en: **http://localhost:8000**

## Usuarios Demo

| Rol            | Email                  | Password  |
|----------------|------------------------|-----------|
| Superadmin     | admin@iso27001.local   | admin123  |
| Admin Cliente  | admin@demo.local       | demo123   |

## Modulos

| Modulo         | Descripcion                                                |
|----------------|-------------------------------------------------------------|
| Evaluaciones   | Evaluar 93 controles ISO 27001:2022 con madurez CMMI (0-5) |
| Dashboard      | KPIs, score de madurez, reloj en tiempo real, sidebar moderna |
| Documentos     | Versionado semantico (semver), diff, rollback, aprobacion    |
| RFCs           | Solicitudes de cambio ITIL (4 niveles de riesgo, workflow)   |
| Sprints        | Gestion agil: backlog + sprints + tareas por control         |
| Import/Export  | Importar/Exportar evaluaciones desde Excel                  |
| Clientes       | Gestion multi-tenant con usuarios y roles                    |
| Auditoria      | Log de todas las acciones (login, logout, CRUD)              |

## Controles ISO 27001:2022 (93 controles)

| Dominio                            | Controles |
|------------------------------------|-----------|
| A.5 Controles Organizacionales     | 37        |
| A.6 Controles de Personas         | 8         |
| A.7 Controles Fisicos             | 14        |
| A.8 Controles Tecnologicos         | 34        |

## Roles

| Rol              | Descripcion                              |
|------------------|------------------------------------------|
| Superadmin       | Gestiona todo el sistema                 |
| Admin Cliente    | Gestiona su cliente y usuarios            |
| Evaluador        | Evalua controles y sube evidencia         |
| Solo Vista       | Solo ve resultados (solo lectura)         |

## Comandos de Gestion

```bash
# Backup completo (DB + uploads)
python scripts/backup.py backup

# Backup solo base de datos
python scripts/backup.py backup-db

# Restaurar desde backup
python scripts/backup.py restore backups/backup_YYYYMMDD.zip

# Listar backups disponibles
python scripts/backup.py list

# Rollback de codigo (Git)
python scripts/rollback.py              # al tag anterior
python scripts/rollback.py v1.0.0      # a version especifica
python scripts/rollback.py --list      # ver tags disponibles
```

## Estructura del Proyecto

```
app/
  main.py           # Punto de entrada FastAPI
  database.py       # Configuracion SQLite
  models.py         # Modelos SQLModel (15 entidades)
  auth.py           # Autenticacion y permisos
  seed.py           # Datos iniciales (93 controles ISO 27001)
  templates_core.py # Configuracion de templates Jinja2
  routes/           # API endpoints (13 routers)
  templates/        # Plantillas HTML
  static/css/      # Estilos CSS personalizados
scripts/
  backup.py        # Backup/restore de DB y archivos
  rollback.py      # Rollback de codigo via Git
uploads/           # Archivos de evidencia
backups/           # Backups generados
```

## Produccion

```bash
# Crear secreto seguro
openssl rand -hex 32

# Editar .env con SECRET_KEY real
cp .env.example .env

# Con Docker
docker-compose up -d
```

## Version

**v1.1.0** - UI moderna, sidebar, reloj en tiempo real, audit log, 93 controles ISO 27001:2022

---

## Documentacion Completa

Toda la documentacion del proyecto esta en la carpeta `docs/`:

| Documento | Contenido |
|----------|-----------|
| `docs/INFRASTRUCTURE.md` | Plataformas gratuitas para desarrollo, QA y produccion |
| `docs/PROJECT_PLAN.md` | Planificacion, alcance, roadmap, riesgos |
| `docs/PROCESSES.md` | Procesos ITIL y Agile, RFCs, incidentes, backup |
| `docs/ARCHITECTURE.md` | Arquitectura tecnica, modelo de datos, endpoints |
| `docs/TESTING.md` | Plan de pruebas funcionales y de seguridad |
| `docs/CHANGELOG.md` | Registro de cambios por version |
