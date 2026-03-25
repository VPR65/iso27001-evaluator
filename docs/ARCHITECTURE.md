# ARQUITECTURA TECNICA - ISO 27001 Evaluator

> Version: 1.4.0 | Ultima actualizacion: 2026-03-25

---

## 1. VISTA GENERAL DE ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────┐
│                     NAVEGADOR WEB                            │
│              (Chrome, Firefox, Edge)                        │
│         HTML + CSS + JS + HTMX + Chart.js                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   SERVIDOR WEB                               │
│                 FastAPI + Uvicorn                          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │  Routers    │  │  Auth       │  │  Templates      │    │
│  │  /dashboard │  │  Session    │  │  Jinja2         │    │
│  │  /evaluations│ │  bcrypt     │  │  Pico.css       │    │
│  │  /rfcs      │  │  Roles      │  │  Font Awesome   │    │
│  │  /documents │  │             │  │                 │    │
│  │  /sprints   │  │             │  │                 │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    SQLModel                           │  │
│  │  Client | User | Session | Evaluation | Control | RFC |  │
│  │  Document | Sprint | BacklogItem | AuditLog          │  │
│  └──────────────────────┬──────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────┘
                           │ SQLite
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   BASE DE DATOS                             │
│                      SQLite                                  │
│               (app/database.db)                             │
│                                                              │
│  15 tablas: clients, users, sessions,                       │
│  control_definitions, evaluations, control_responses,        │
│  evidence_files, documents, document_versions,               │
│  rfcs, sprints, backlog_items, sprint_tasks, audit_logs      │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Archivos
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ARCHIVOS LOCALES                          │
│                                                              │
│  uploads/          - Archivos de evidencia                 │
│  backups/          - Backups de DB + uploads                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. DIAGRAMA DE CAPAS

```
┌────────────────────────────────────────────────┐
│              PRESENTACION (Templates)          │
│   base.html, login.html, dashboard/*, etc.    │
│   CSS: style.css | JS: HTMX, Chart.js        │
└────────────────────────┬───────────────────────┘
                         │ Jinja2
                         ▼
┌────────────────────────────────────────────────┐
│              LOGICA DE NEGOCIO (Routes)        │
│   auth.py | dashboard.py | evaluations.py        │
│   rfcs.py | documents.py | sprints.py           │
│   stats.py | import_export.py | clients.py      │
│   users.py | evaluate.py | admin.py            │
└────────────────────────┬───────────────────────┘
                         │ SQLModel ORM
                         ▼
┌────────────────────────────────────────────────┐
│              ACCESO A DATOS (Models)            │
│   Client | User | Evaluation | ControlDefinition │
│   ControlResponse | EvidenceFile | Document     │
│   DocumentVersion | Rfc | Sprint | BacklogItem  │
│   SprintTask | AuditLog | Session              │
└────────────────────────┬───────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────┐
│              BASE DE DATOS (SQLite)             │
│   Integrity, security, performance              │
└────────────────────────────────────────────────┘
```

---

## 3. MODELO DE DATOS

### 3.1 Entidades Principales

```
Client (1) ─────┬───── (*) User
                 │              │
                 │              │ belongs to
                 │              ▼
                 │         Session ─── user_id
                 │
                 ├───── (*) Evaluation ─── (*) ControlResponse
                 │              │                    │
                 │              │                  │ control_id
                 │              ▼                  ▼
                 │         Client          ControlDefinition (93)
                 │
                 ├───── (*) Document ─── (*) DocumentVersion
                 │
                 ├───── (*) Rfc
                 │
                 └───── (*) Sprint ─── (*) BacklogItem
                                        │
                                        └─── (*) SprintTask
```

### 3.2 Tablas de la Base de Datos

| Tabla                | Proposito                                      | Relaciones          |
|---------------------|------------------------------------------------|---------------------|
| `clients`           | Empresas/clientes multi-tenant                  | 1:N users, evaluations |
| `users`             | Usuarios con roles                             | N:1 client         |
| `sessions`           | Sesiones de autenticacion                     | N:1 user           |
| `normas`            | Normas disponibles (ISO 27001, ITIL4, etc)   | 1:N control_definitions |
| `control_definitions` | Controles de normas (187 total: 93+25+17+18+34) | 1:N responses     |
| `evaluations`       | Evaluaciones de un cliente                     | N:1 client, N:1 norma, 1:N responses |
| `control_responses` | Respuesta de un control en una evaluacion     | N:1 evaluation, N:1 control, 1:N evidence |
| `evidence_files`     | Archivos de evidencia subidos                  | N:1 response       |
| `documents`         | Documentos versionados                         | 1:N versions       |
| `document_versions`  | Versiones especificas de un documento          | N:1 document       |
| `rfcs`              | Solicitudes de cambio ITIL                    | N:1 client         |
| `sprints`           | Sprints agiles                                 | N:1 client         |
| `backlog_items`     | Items del backlog                              | N:1 sprint, N:1 client |
| `sprint_tasks`      | Tareas dentro de un backlog item              | N:1 backlog_item   |
| `audit_logs`        | Log de auditoria de todas las acciones         | N:1 user          |

### 3.3 Normas Disponibles

| Norma | Version | Controles | Descripcion |
|-------|---------|-----------|-------------|
| ISO/IEC 27001 | 2022 | 93 | Sistema de Gestion de Seguridad de la Informacion |
| ISO 9001 | 2015 | 25 | Sistema de Gestion de la Calidad |
| ISO/IEC 20000-1 | 2018 | 17 | Sistema de Gestion de Servicios de TI |
| ISO 22301 | 2019 | 18 | Sistema de Gestion de Continuidad del Negocio |
| ITIL v4 | 4.0 | 34 | Framework de Gestion de Servicios de TI |

**Total: 187 controles/practicas**

---

## 4. FLUJO DE AUTENTICACION

```
Navegador                          Servidor
    │                                   │
    │  GET /login                      │
    │──────────────────────────────────►│
    │                                   │ Renderiza login.html
    │◄─────────────────────────────────│
    │                                   │
    │  POST /login (email + password)   │
    │──────────────────────────────────►│
    │                                   │ Busca user en DB
    │                                   │ Verifica password (bcrypt)
    │                                   │ Crea Session en DB
    │                                   │ Set-Cookie: session_id
    │  302 /dashboard + Set-Cookie       │
    │◄─────────────────────────────────│
    │                                   │
    │  GET /dashboard (Cookie: session_id)│
    │──────────────────────────────────►│
    │                                   │ Busca Session en DB
    │                                   │ Valida expiracion
    │                                   │ Obtiene User
    │                                   │ Renderiza dashboard
    │  200 HTML + contenido              │
    │◄─────────────────────────────────│
```

### 4.1 Roles y Permisos

```
                    SUPERADMIN
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ADMIN_CLIENTE    EVALUADOR      VISTA_SOLO
         │               │               │
    + CRUD clientes  + Evaluar       Solo lectura
    + CRUD usuarios    controles     de todo
    + Ver eval      + Subir evidencia
    + Crear RFCs   + Crear RFCs
    + Ver stats     + Ver stats
```

---

## 5. ENDPOINTS PRINCIPALES

### 5.1 Rutas Publicas

| Metodo | Ruta         | Descripcion              |
|--------|--------------|--------------------------|
| GET    | `/`          | Redirige a /dashboard o /login |
| GET    | `/login`      | Pagina de login           |
| POST   | `/login`      | Autenticacion              |
| POST   | `/logout`      | Cerrar sesion             |
| GET    | `/health`     | Health check              |

### 5.2 Rutas Protegidas

| Modulo      | Rutas                                         |
|-------------|-----------------------------------------------|
| Dashboard   | `/dashboard`                                  |
| Evaluaciones| `/evaluations`, `/evaluations/{id}`, `/evaluations/new`, `/evaluate/{eval_id}/control/{ctrl_id}` |
| Estadisticas| `/stats/{eval_id}`, `/stats/{eval_id}/json`  |
| Documentos  | `/documents`, `/documents/{id}`, `/documents/new`, `/documents/{id}/versions/{ver}` |
| RFCs        | `/rfcs`, `/rfcs/{id}`, `/rfcs/new`           |
| Sprints     | `/sprints`, `/sprints/{id}`, `/sprints/new`   |
| Clientes    | `/clients`, `/clients/new`                   |
| Usuarios    | `/clients/{id}/users`, `/clients/{id}/users/new` |
| Admin       | `/admin/all-users`                           |
| Import/Export| `/import-export/import`, `/import-export/export/{id}` |

---

## 6. CONFIGURACION DE ENTORNO

```bash
# .env (NO committing to git!)
SECRET_KEY=tu_clave_secreta_generada_con_openssl
SESSION_EXPIRE_HOURS=24
DEBUG=false

# .env.example (committed to git)
SECRET_KEY=changeme
SESSION_EXPIRE_HOURS=24
DEBUG=false
```

---

## 7. SEGURIDAD

| Control                   | Implementacion                              |
|---------------------------|---------------------------------------------|
| Autenticacion             | bcrypt (passlib) + sesiones cookies         |
| Autorizacion              | Roles verificados en cada endpoint          |
| Proteccion XSS            | Jinja2 auto-escape                         |
| Proteccion SQL Injection  | SQLModel ORM (no SQL raw concatenado)       |
| CSRF                      | Tokens en forms                             |
| Archivos subidos           | Validacion de tipo y tamano                 |
| Secrets                   | Variables de entorno (nunca hardcoded)       |
| Auditoria                 | AuditLog para todas las acciones            |

---

## 8. DESPLIEGUE

### 8.1 Local (Desarrollo)

```bash
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

### 8.2 Docker (Produccion)

```bash
docker-compose up --build -d
```

### 8.3 Estructura de Archivos en Produccion

```
/opt/iso27001-evaluator/
├── app/                    # Codigo de la aplicacion
├── uploads/                # Archivos de evidencia
├── backups/                # Backups generados
├── .env                    # Variables de entorno (NO en git)
├── docker-compose.yml       # Configuracion Docker
├── Dockerfile              # Imagen Docker
└── data/                   # Volumen para SQLite (si aplica)
```

---

## 9. MONITOREO

| Componente        | Que monitorear                  | Accion               |
|-------------------|--------------------------------|----------------------|
| Health endpoint   | GET /health debe responder 200  | Alertar si falla    |
| Logs de uvicorn   | ERROR o EXCEPTION              | Revisar inmediatamente|
| Espacio en disco  | < 1GB libre                   | Alertar              |
| Tamano de DB       | > 100MB                       | Investigar          |
| Accesos fallidos   | > 10 en 5 minutos             | Revisar seguridad   |
